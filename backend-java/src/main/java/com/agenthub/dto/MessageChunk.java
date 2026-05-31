package com.agenthub.dto;

import lombok.Data;

@Data
public class MessageChunk {
    private String content;
    private Boolean isComplete;

}
