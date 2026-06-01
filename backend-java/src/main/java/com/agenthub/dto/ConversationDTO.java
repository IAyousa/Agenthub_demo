package com.agenthub.dto;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class ConversationDTO {
    private String id;
    private String title;
    private String type;
    private String lastMessage;
    private LocalDateTime updatedAt;
    private List<String> agentNames;
    private Boolean isArchived;
    private List<AgentInfo> agents;
    private LocalDateTime createdAt;

    @Data
    public static class AgentInfo {
        private String id;
        private String name;
        private String type;
        private String avatarUrl;
    }
}
