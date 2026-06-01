package com.agenthub.dto;

import lombok.Data;

@Data
public class MessageChunk {
    private String content;
    private Boolean isComplete;
    private String agentId;
    private String agentName;
    private String messageType;
    private String messageId;
    private String type;
}
