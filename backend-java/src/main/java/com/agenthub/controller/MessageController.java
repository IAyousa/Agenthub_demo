package com.agenthub.controller;

import com.agenthub.model.Message;
import com.agenthub.service.MessageService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindException;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequiredArgsConstructor
@Validated
public class MessageController {

    private final MessageService messageService;
    private final ObjectMapper objectMapper;

    @Data
    public static class PinMessageRequest {
        @NotNull(message = "pinned 不能为空")
        private Boolean pinned;
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

    @GetMapping("/conversations/{conversationId}/messages")
    public ResponseEntity<Map<String, Object>> list(
            @PathVariable String conversationId,
            @RequestParam(required = false, defaultValue = "0") @Min(0) Integer page,
            @RequestParam(required = false, defaultValue = "50") @Min(1) @Max(100) Integer size) {

        Page<Message> messagePage = messageService.getMessagesByConversationId(conversationId, page, size);

        List<Map<String, Object>> messageList = messagePage.getContent().stream().map(msg -> {
            Map<String, Object> msgMap = new LinkedHashMap<>();
            msgMap.put("id", msg.getId());
            msgMap.put("senderType", msg.getSenderType());
            msgMap.put("messageType", msg.getMessageType());
            msgMap.put("createdAt", msg.getCreatedAt() != null ? msg.getCreatedAt().toString() : null);

            if ("agent".equals(msg.getSenderType()) && msg.getAgentName() != null) {
                msgMap.put("agentName", msg.getAgentName());
            }

            Object parsed = parseContent(msg.getContent(), msg.getMessageType());
            msgMap.put("content", parsed);
            return msgMap;
        }).collect(java.util.stream.Collectors.toList());

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("messages", messageList);
        response.put("page", messagePage.getNumber());
        response.put("size", messagePage.getSize());
        response.put("total", messagePage.getTotalElements());

        return ResponseEntity.ok(response);
    }

    @PutMapping("/conversations/{conversationId}/messages/{messageId}/pin")
    public ResponseEntity<Map<String, Object>> togglePin(
            @PathVariable String conversationId,
            @PathVariable String messageId,
            @Valid @RequestBody PinMessageRequest request) {

        Message message = messageService.getMessageById(messageId);
        if (!message.getConversationId().equals(conversationId)) {
            throw new IllegalArgumentException("消息不属于此会话");
        }

        Message updated = Boolean.TRUE.equals(request.getPinned())
                ? messageService.pinMessage(messageId)
                : messageService.unpinMessage(messageId);

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", updated.getId());
        response.put("pinned", updated.getIsPinned());

        return ResponseEntity.ok(response);
    }

    private Object parseContent(String content, String messageType) {
        if (content == null) return "";
        if ("text".equals(messageType)) return content;
        try {
            return objectMapper.readValue(content, Map.class);
        } catch (JsonProcessingException e) {
            return content;
        }
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
}
