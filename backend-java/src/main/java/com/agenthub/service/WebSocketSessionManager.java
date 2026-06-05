package com.agenthub.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * STOMP WebSocket session manager.
 * Maps userId → StompSessionId for user-targeted message delivery.
 * Delegates actual message sending to SimpMessagingTemplate.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WebSocketSessionManager {

    private final SimpMessagingTemplate messagingTemplate;
    private final ConcurrentHashMap<String, String> userSessionMap = new ConcurrentHashMap<>();

    public void register(String userId, String sessionId) {
        userSessionMap.put(userId, sessionId);
        log.debug("Session registered: userId={}, sessionId={}", userId, sessionId);
    }

    public void unregister(String sessionId) {
        userSessionMap.values().remove(sessionId);
        log.debug("Session unregistered: sessionId={}", sessionId);
    }

    public void sendToConversation(String conversationId, Object payload) {
        messagingTemplate.convertAndSend(
                "/topic/conversation." + conversationId, payload);
    }

    public void sendToUser(String userId, String destination, Object payload) {
        messagingTemplate.convertAndSendToUser(userId, destination, payload);
    }

    public boolean isOnline(String userId) {
        return userSessionMap.containsKey(userId);
    }

    public Set<String> getOnlineUsers() {
        return Set.copyOf(userSessionMap.keySet());
    }
}
