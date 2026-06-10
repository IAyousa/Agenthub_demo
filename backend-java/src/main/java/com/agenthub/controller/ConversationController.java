package com.agenthub.controller;

import com.agenthub.model.Agent;
import com.agenthub.model.Conversation;
import com.agenthub.service.ConversationService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.validation.BindException;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/conversations")
@RequiredArgsConstructor
@Validated
public class ConversationController {

    private final ConversationService conversationService;

    @Data
    public static class CreateConversationRequest {
        @NotBlank(message = "title 不能为空")
        @Size(max = 200, message = "title 最大200字符")
        private String title;

        @NotBlank(message = "type 不能为空")
        @Pattern(regexp = "^(direct|group)$", message = "type 只能是 direct 或 group")
        private String type;

        private List<String> agentIds = Collections.emptyList();
    }

    @Data
    public static class UpdateConversationRequest {
        @Size(max = 200, message = "title 最大200字符")
        private String title;
        private Boolean isArchived;
    }

    @Data
    public static class UpdateConversationAgentsRequest {
        private List<String> agentIds = Collections.emptyList();
    }

    @Data
    public static class ErrorResponse {
        private String error;
        private String message;
        private String timestamp;
        private String path;

        public ErrorResponse(String error, String message, String path) {
            this.error = error;
            this.message = message;
            this.timestamp = LocalDateTime.now().toString();
            this.path = path;
        }
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> list(
            @RequestParam(required = false, defaultValue = "false") Boolean archived) {
        String currentUserId = getCurrentUserId();
        List<Conversation> conversations = archived
                ? conversationService.getUserArchivedConversations(currentUserId)
                : conversationService.getUserConversations(currentUserId);

        List<Map<String, Object>> resultList = conversations.stream().map(conv -> {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("id", conv.getId());
            map.put("title", conv.getTitle());
            map.put("type", conv.getType());
            map.put("lastMessage", "");
            map.put("updatedAt", conv.getUpdatedAt() != null ? conv.getUpdatedAt().toString() : null);
            map.put("agentNames", conv.getAgents().stream().map(Agent::getName).collect(Collectors.toList()));
            map.put("isArchived", conv.getIsArchived());
            return map;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(Map.of("conversations", resultList));
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> create(
            @Valid @RequestBody CreateConversationRequest request) {
        List<String> agentIds = request.getAgentIds() != null && !request.getAgentIds().isEmpty()
                ? request.getAgentIds()
                : Collections.singletonList("agent_claude_001");
        Conversation conversation = conversationService.createConversation(
                request.getTitle(), request.getType(), getCurrentUserId(), agentIds);

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", conversation.getId());
        response.put("title", conversation.getTitle());
        response.put("type", conversation.getType());
        response.put("agentIds",
                conversation.getAgents().stream().map(Agent::getId).collect(Collectors.toList()));
        response.put("createdAt", conversation.getCreatedAt() != null
                ? conversation.getCreatedAt().toString() : null);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> detail(@PathVariable String id) {
        Conversation conversation = conversationService.getConversationById(id);

        List<Map<String, Object>> agentList = conversation.getAgents().stream().map(agent -> {
            Map<String, Object> agentMap = new LinkedHashMap<>();
            agentMap.put("id", agent.getId());
            agentMap.put("name", agent.getName());
            agentMap.put("type", agent.getType());
            agentMap.put("avatarUrl", agent.getAvatarUrl() != null ? agent.getAvatarUrl() : "");
            return agentMap;
        }).collect(Collectors.toList());

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", conversation.getId());
        response.put("title", conversation.getTitle());
        response.put("type", conversation.getType());
        response.put("agents", agentList);
        response.put("createdAt", conversation.getCreatedAt() != null
                ? conversation.getCreatedAt().toString() : null);
        response.put("updatedAt", conversation.getUpdatedAt() != null
                ? conversation.getUpdatedAt().toString() : null);

        return ResponseEntity.ok(response);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<Map<String, Object>> update(
            @PathVariable String id,
            @Valid @RequestBody UpdateConversationRequest request) {
        Conversation updated = conversationService.updateConversation(
                id, request.getTitle(), null, request.getIsArchived());

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", updated.getId());
        response.put("title", updated.getTitle());
        response.put("isArchived", updated.getIsArchived());
        response.put("updatedAt", updated.getUpdatedAt() != null
                ? updated.getUpdatedAt().toString() : null);

        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable String id) {
        conversationService.deleteConversation(id);
        return ResponseEntity.ok(Map.of("message", "会话已删除", "deletedId", id));
    }

    @PutMapping("/{id}/agents")
    public ResponseEntity<Map<String, Object>> updateAgents(
            @PathVariable String id,
            @Valid @RequestBody UpdateConversationAgentsRequest request) {
        // 逐个移除现有 Agent → 添加新 Agent → 每个操作独立事务保证持久化
        Conversation conversation = conversationService.getConversationById(id);
        List<String> existingIds = conversation.getAgents().stream()
                .map(Agent::getId).collect(Collectors.toList());
        for (String agentId : existingIds) {
            conversationService.removeAgentFromConversation(id, agentId);
        }
        for (String agentId : request.getAgentIds()) {
            conversation = conversationService.addAgentToConversation(id, agentId);
        }
        // 重新获取最新状态用于响应
        conversation = conversationService.getConversationById(id);

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", conversation.getId());
        response.put("agentIds",
                conversation.getAgents().stream().map(Agent::getId).collect(Collectors.toList()));
        response.put("updatedAt", conversation.getUpdatedAt() != null
                ? conversation.getUpdatedAt().toString() : null);

        return ResponseEntity.ok(response);
    }

    @ExceptionHandler({BindException.class, jakarta.validation.ConstraintViolationException.class,
            IllegalArgumentException.class})
    public ResponseEntity<ErrorResponse> handleValidation(Exception ex) {
        String message;
        if (ex instanceof BindException be) {
            message = Objects.requireNonNull(be.getFieldError()).getDefaultMessage();
        } else {
            message = ex.getMessage();
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ErrorResponse("VALIDATION_ERROR", message, "/conversations"));
    }

    /**
     * 从 SecurityContextHolder 获取当前登录用户 ID
     */
    private String getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            return authentication.getPrincipal().toString();
        }
        return "anonymous";
    }
}
