package com.agenthub.controller;

import com.agenthub.dto.SendMessageRequest;
import com.agenthub.model.Agent;
import com.agenthub.model.Conversation;
import com.agenthub.model.Message;
import com.agenthub.repository.AgentRepository;
import com.agenthub.repository.ConversationRepository;
import com.agenthub.service.AgentGatewayService;
import com.agenthub.service.MessageService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

import java.util.*;

@Slf4j
@Controller
@RequiredArgsConstructor
public class WebSocketController {

    private final SimpMessagingTemplate messagingTemplate;
    private final AgentGatewayService agentGatewayService;
    private final MessageService messageService;
    private final ConversationRepository conversationRepository;
    private final AgentRepository agentRepository;

    @MessageMapping("/chat.send")
    public void handleUserMessage(@Payload SendMessageRequest request) {
        String conversationId = request.getConversationId();
        String content = request.getContent();
        if (content == null || content.isBlank()) return;

        String topic = "/topic/conversation." + conversationId;
        log.info("Processing message: conversationId={}, topic={}, contentLen={}",
                conversationId, topic, content.length());

        // Step 0: Auto-create conversation if it doesn't exist in DB yet
        ensureConversationExists(conversationId);

        // Step 1: Save user message
        Message userMessage = messageService.saveMessage(
                conversationId, "system", "user", content.trim(), "text", null);
        log.info("User message saved: id={}", userMessage.getId());

        // Step 2: Resolve agent from DB (MVP: default to claude_code)
        Agent agent = agentRepository.findById("agent_claude_001").orElse(null);
        String agentType = agent != null ? agent.getType() : "claude_code";
        String systemPrompt = (agent != null && agent.getSystemPrompt() != null)
                ? agent.getSystemPrompt() : "";
        if (agentType == null) {
            messagingTemplate.convertAndSend(topic, errorChunk(
                    "Agent type could not be determined for this conversation."));
            return;
        }

        // Step 3: Build conversation context
        List<Message> contextMessages = messageService.buildConversationContext(conversationId, 20);
        String context = buildContextString(contextMessages);

        // Step 4: Stream agent response via STOMP
        boolean[] receivedTokens = {false};
        StringBuilder fullResponse = new StringBuilder();

        String workspacePath = "./agent_workspaces/" + conversationId;
        agentGatewayService.sendToAgent(context, agentType, systemPrompt, workspacePath, token -> {
            try {
                if (token.getToken() != null && !token.getToken().isEmpty()) {
                    receivedTokens[0] = true;
                    fullResponse.append(token.getToken());

                    Map<String, Object> chunk = new LinkedHashMap<>();
                    chunk.put("type", "chunk");
                    chunk.put("content", token.getToken());
                    chunk.put("isComplete", false);
                    chunk.put("agentId", "agent_" + agentType);
                    chunk.put("agentName", token.getAgentName() != null
                            ? token.getAgentName()
                            : (agent != null ? agent.getName() : getAgentName(agentType)));
                    chunk.put("messageType", "text");
                    messagingTemplate.convertAndSend(topic, chunk);
                }

                if (token.isFinish()) {
                    if (receivedTokens[0]) {
                        log.info("Agent response completed: {} chars, conversationId={}",
                                fullResponse.length(), conversationId);
                        messageService.saveMessage(conversationId, "system", "assistant",
                                fullResponse.toString(), "text", getAgentName(agentType));
                    } else {
                        // Agent returned no tokens — send fallback response
                        log.info("No tokens from agent, sending fallback to topic={}", topic);
                        Map<String, Object> fallback = new LinkedHashMap<>();
                        fallback.put("type", "chunk");
                        fallback.put("content", "你好！我是 AgentHub 的 AI 助手。当前 Agent 服务尚未连接 CLI 工具，这是一条来自 Java 后端的测试回复，验证 WebSocket → STOMP → 前端的消息推送链路正常工作。");
                        fallback.put("isComplete", false);
                        fallback.put("agentId", "agent_system");
                        fallback.put("agentName", "System");
                        fallback.put("messageType", "text");
                        messagingTemplate.convertAndSend(topic, fallback);
                    }

                    Map<String, Object> finish = new LinkedHashMap<>();
                    finish.put("type", "finish");
                    finish.put("content", "");
                    finish.put("isComplete", true);
                    finish.put("agentId", "agent_" + agentType);
                    finish.put("messageId", token.getMessageId() != null ? token.getMessageId() : "");
                    finish.put("messageType", "text");
                    messagingTemplate.convertAndSend(topic, finish);
                }

                if (token.getError() != null && !token.getError().isEmpty()) {
                    log.error("Agent error: {}", token.getError());
                    messagingTemplate.convertAndSend(topic, errorChunk(token.getError()));
                }
            } catch (Exception e) {
                log.error("Failed to push chunk", e);
            }
        });
    }

    private void ensureConversationExists(String conversationId) {
        if (conversationRepository.existsById(conversationId)) return;

        Conversation conv = new Conversation();
        conv.setId(conversationId);
        conv.setTitle("New Chat");
        conv.setType("direct");
        conv.setCreatedBy("system");
        conv.setIsArchived(false);

        Agent defaultAgent = agentRepository.findById("agent_claude_001").orElse(null);
        if (defaultAgent != null) {
            conv.setAgents(Set.of(defaultAgent));
        }

        conversationRepository.save(conv);
        log.info("Auto-created conversation: id={}", conversationId);
    }

    // Agent routing is resolved from DB in Step 2 of handleUserMessage.
    // MVP default: agent_claude_001 for all conversations.
    // Full routing (direct → session agent, group → orchestrator) is P2 scope.

    private String buildContextString(List<Message> messages) {
        StringBuilder sb = new StringBuilder();
        for (Message msg : messages) {
            sb.append(msg.getSenderType()).append(": ").append(msg.getContent()).append("\n");
        }
        return sb.toString();
    }

    private String getAgentName(String agentType) {
        return switch (agentType) {
            case "claude_code" -> "Claude Code";
            case "codex" -> "Codex";
            case "custom" -> "Custom Agent";
            default -> agentType;
        };
    }

    private Map<String, Object> errorChunk(String message) {
        Map<String, Object> chunk = new LinkedHashMap<>();
        chunk.put("type", "error");
        chunk.put("content", message);
        chunk.put("isComplete", true);
        chunk.put("agentName", "System");
        chunk.put("messageType", "error");
        return chunk;
    }
}
