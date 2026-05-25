package com.agenthub.controller;

import com.agenthub.dto.SendMessageRequest;
import com.agenthub.service.AgentGatewayService;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
public class WebSocketController {

    private final SimpMessagingTemplate messagingTemplate;
    private final AgentGatewayService agentGatewayService;

    @MessageMapping("/chat.send")
    public void handleUserMessage(@Payload SendMessageRequest request) {
        // 1. Save message to DB (To be implemented)
        // 2. Call Agent Service
        // 3. Push results via WebSocket
    }
}
