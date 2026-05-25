package com.agenthub.service;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class AgentGatewayService {
    private final WebClient webClient;

    public AgentGatewayService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public void sendToAgent(String message) {
        // Implementation for calling Python FastAPI service
    }
}
