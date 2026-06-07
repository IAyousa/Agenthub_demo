package com.agenthub.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

@Slf4j
@Service
public class AgentGatewayService {
    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    public AgentGatewayService(WebClient.Builder webClientBuilder, ObjectMapper objectMapper) {
        this.webClient = webClientBuilder
                .baseUrl("http://localhost:8000")
                .build();
        this.objectMapper = objectMapper;
    }

    /**
     * 调用 Python FastAPI Agent 服务进行流式对话。
     * 对齐 API 契约文档第 4.2 节：POST /api/agent/chat
     *
     * @param context      格式化后的对话上下文（由 MessageService 组装）
     * @param agentType    Agent 类型（claude_code / codex / custom）
     * @param systemPrompt 系统提示词
     * @param onToken      token 回调，携带 agentId/agentName 用于 Agent 切换
     */
    public void sendToAgent(String context, String agentType, String systemPrompt,
                            String workingDirectory, String conversationId,
                            Consumer<AgentToken> onToken) {
        Map<String, Object> body = new HashMap<>();
        body.put("agentType", agentType);  // null → Python Orchestrator 编排模式
        body.put("systemPrompt", systemPrompt != null ? systemPrompt : "");
        body.put("context", context != null ? context : "");
        body.put("stream", true);
        if (workingDirectory != null && !workingDirectory.isEmpty()) {
            body.put("workingDirectory", workingDirectory);
        }
        if (conversationId != null && !conversationId.isEmpty()) {
            body.put("conversationId", conversationId);
        }

        webClient.post()
                .uri("/api/agent/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(body)
                .retrieve()
                .bodyToFlux(String.class)
                .doOnNext(chunk -> {
                    if (chunk == null || chunk.isBlank()) return;
                    for (String rawLine : chunk.split("\n")) {
                        String line = rawLine.trim();
                        if (line.isEmpty() || line.equals("[DONE]")) continue;
                        // Support both SSE "data: {...}" format and raw JSON
                        String jsonStr = line.startsWith("data: ")
                                ? line.substring(6).trim()
                                : line;
                        if (jsonStr.isEmpty() || jsonStr.startsWith(":")) continue;
                        try {
                            JsonNode node = objectMapper.readTree(jsonStr);
                            String token = node.path("token").asText(null);
                            boolean finish = node.path("finish").asBoolean(false);
                            String agentId = node.path("agentId").asText(null);
                            String agentName = node.path("agentName").asText(null);
                            String messageId = node.path("messageId").asText(null);
                            String error = node.path("error").asText(null);

                            if (error != null && !error.isEmpty()) {
                                log.error("Agent error: {}", error);
                                onToken.accept(AgentToken.error(error));
                                continue;
                            }

                            if (finish) {
                                onToken.accept(AgentToken.finish(messageId));
                            } else if (token != null && !token.isEmpty()) {
                                onToken.accept(new AgentToken(token, agentId, agentName));
                            }
                        } catch (Exception e) {
                            log.warn("Skip invalid SSE data line: {}", line, e);
                        }
                    }
                })
                .doOnComplete(() -> log.info("Agent SSE streaming completed"))
                .doOnError(e -> {
                    log.error("Agent SSE streaming error", e);
                    String friendlyMsg = e instanceof WebClientRequestException
                            ? "Agent 服务暂时不可用，请检查 Python 服务是否已启动（端口 8000）"
                            : "Agent 服务异常，请稍后重试";
                    onToken.accept(AgentToken.error(friendlyMsg));
                })
                .subscribe();
    }

    /**
     * Agent 流式响应的 token 数据。
     */
    public static class AgentToken {
        private final String token;
        private final String agentId;
        private final String agentName;
        private final String messageId;
        private final boolean finish;
        private final String error;

        public AgentToken(String token, String agentId, String agentName) {
            this.token = token;
            this.agentId = agentId;
            this.agentName = agentName;
            this.messageId = null;
            this.finish = false;
            this.error = null;
        }

        private AgentToken(boolean finish, String messageId, String error) {
            this.token = null;
            this.agentId = null;
            this.agentName = null;
            this.messageId = messageId;
            this.finish = finish;
            this.error = error;
        }

        public static AgentToken finish(String messageId) {
            return new AgentToken(true, messageId, null);
        }

        public static AgentToken error(String error) {
            return new AgentToken(true, null, error);
        }

        public String getToken() { return token; }
        public String getAgentId() { return agentId; }
        public String getAgentName() { return agentName; }
        public String getMessageId() { return messageId; }
        public boolean isFinish() { return finish; }
        public String getError() { return error; }
    }
}
