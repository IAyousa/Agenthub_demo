package com.agenthub.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Value("${cors.allowed-origins}")
    private String allowedOrigins;

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // 原生 WebSocket 端点（流式输出推荐，无 SockJS 帧缓冲延迟）
        registry.addEndpoint("/ws-chat")
                .setAllowedOriginPatterns(allowedOrigins.split(","));

        // SockJS 降级端点（企业代理/旧浏览器兼容）
        registry.addEndpoint("/ws-chat-sockjs")
                .setAllowedOriginPatterns(allowedOrigins.split(","))
                .withSockJS();
    }
}
