package com.agenthub.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

@Slf4j
@Service
public class AgentGatewayService {
    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    public AgentGatewayService(WebClient.Builder webClientBuilder, ObjectMapper objectMapper) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
        this.objectMapper = objectMapper;
    }

    public void sendToAgent(String message, String agentType, String systemPrompt,
                            List<Map<String, String>> history, Consumer<String> onToken) {
        webClient.post()
                .uri("/api/v1/messages/chat/stream")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(Map.of(
                        "message", message,
                        "agent_type", agentType != null ? agentType : "claude",
                        "system_prompt", systemPrompt != null ? systemPrompt : "",
                        "history", history != null ? history : List.of()
                ))
                .retrieve()
                .bodyToFlux(String.class)
                .doOnNext(line -> {
                    if (line == null || line.isBlank()) {
                        return;
                    }
                    String trimmed = line.trim();
                    if (trimmed.isEmpty()) {
                        return;
                    }
                    try {
                        JsonNode node = objectMapper.readTree(trimmed);
                        String type = node.path("type").asText();

                        if ("msg_chunk".equals(type)) {
                            String delta = node.path("delta").asText();
                            if (delta != null && !delta.isEmpty()) {
                                onToken.accept(delta);
                            }
                        }
                    } catch (Exception e) {
                        log.warn("Skip invalid NDJSON line: {}", trimmed, e);
                    }
                })
                .doOnComplete(() -> log.info("Agent SSE streaming completed successfully"))
                .doOnError(e -> log.error("Error during agent SSE streaming", e))
                .subscribe();
    }
}
