package com.agenthub.dto;

import lombok.Data;

/**
 * Python Agent Service → Java Backend internal artifact upload request.
 * Used by POST /internal/artifacts to persist agent-generated files.
 */
@Data
public class InternalArtifactRequest {
    private String conversationId;
    private String messageId;
    private String filename;
    private String content;      // file body (text)
    private String contentType;  // MIME type hint (e.g. "text/html")
}
