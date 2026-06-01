package com.agenthub.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class ArtifactDTO {
    private String id;
    private String filename;
    private Long fileSize;
    private String conversationId;
    private String messageId;
    private LocalDateTime createdAt;
}
