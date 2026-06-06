package com.agenthub.controller;

import com.agenthub.dto.ArtifactDTO;
import com.agenthub.dto.InternalArtifactRequest;
import com.agenthub.service.ArtifactService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@Slf4j
@RestController
@RequiredArgsConstructor
public class ArtifactController {

    private final ArtifactService artifactService;
    private final SimpMessagingTemplate messagingTemplate;

    @PostMapping(value = "/artifacts/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> upload(@RequestParam("file") MultipartFile file,
                                    @RequestParam("conversationId") String conversationId,
                                    @RequestParam(value = "messageId", required = false) String messageId) {
        try {
            ArtifactDTO dto = artifactService.save(file, conversationId, messageId);
            return ResponseEntity.status(HttpStatus.CREATED).body(dto);
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(), "/artifacts/upload");
        } catch (IOException e) {
            log.error("Failed to save artifact", e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "产物保存失败", "/artifacts/upload");
        }
    }

    @GetMapping("/artifacts/{id}")
    public ResponseEntity<?> download(@PathVariable String id) {
        try {
            java.io.File file = artifactService.getFile(id);
            if (file == null) {
                log.warn("Artifact not found or file missing on disk: id={}", id);
                return error(HttpStatus.NOT_FOUND, "NOT_FOUND",
                        "产物不存在: " + id, "/artifacts/" + id);
            }
            return serveFile(file, id);
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(), "/artifacts/" + id);
        }
    }

    @GetMapping("/conversations/{conversationId}/artifacts")
    public ResponseEntity<?> listByConversation(@PathVariable String conversationId) {
        try {
            return ResponseEntity.ok(Map.of("artifacts",
                    artifactService.getByConversation(conversationId)));
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(),
                    "/conversations/" + conversationId + "/artifacts");
        }
    }

    @DeleteMapping("/artifacts/{id}")
    public ResponseEntity<?> delete(@PathVariable String id) {
        try {
            artifactService.delete(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(), "/artifacts/" + id);
        } catch (IOException e) {
            log.error("Failed to delete artifact: id={}", id, e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
                    "产物文件删除失败，请查看服务端日志", "/artifacts/" + id);
        }
    }

    /**
     * Internal endpoint for Python Agent Service to push agent-generated files.
     * Saves file content → DB record → pushes preview_card to WebSocket.
     */
    @PostMapping("/internal/artifacts")
    public ResponseEntity<?> internalUpload(@RequestBody InternalArtifactRequest req) {
        try {
            ArtifactDTO dto = artifactService.saveFromContent(
                    req.getConversationId(), req.getMessageId(),
                    req.getFilename(), req.getContent(), req.getContentType());

            // Push preview_card to the conversation topic
            String topic = "/topic/conversation." + req.getConversationId();
            Map<String, Object> previewCard = new LinkedHashMap<>();
            previewCard.put("type", "chunk");
            // Send actual file content (trimmed for large files) so the frontend can render it
            String displayContent = req.getContent() != null ? req.getContent() : dto.getFilename();
            previewCard.put("content", displayContent);
            previewCard.put("isComplete", true);
            previewCard.put("agentId", "agent_system");
            previewCard.put("agentName", "System");
            previewCard.put("messageType", "preview_card");
            // Metadata: frontend uses title/language/previewUrl for the preview card UI
            Map<String, String> metadata = new LinkedHashMap<>();
            metadata.put("artifactId", dto.getId());
            metadata.put("filename", dto.getFilename());
            metadata.put("title", dto.getFilename());
            metadata.put("language", inferLanguage(dto.getFilename()));
            metadata.put("previewUrl", "/artifacts/" + dto.getId());
            previewCard.put("metadata", metadata);
            messagingTemplate.convertAndSend(topic, previewCard);

            log.info("Internal artifact saved and preview pushed: id={}, conversation={}",
                    dto.getId(), req.getConversationId());
            return ResponseEntity.status(HttpStatus.CREATED).body(dto);
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(), "/internal/artifacts");
        } catch (IOException e) {
            log.error("Failed to save internal artifact", e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "产物保存失败", "/internal/artifacts");
        }
    }

    private String inferLanguage(String filename) {
        if (filename == null) return "plaintext";
        String name = filename.toLowerCase();
        if (name.endsWith(".html") || name.endsWith(".htm")) return "html";
        if (name.endsWith(".js")) return "javascript";
        if (name.endsWith(".ts")) return "typescript";
        if (name.endsWith(".css")) return "css";
        if (name.endsWith(".py")) return "python";
        if (name.endsWith(".java")) return "java";
        if (name.endsWith(".json")) return "json";
        if (name.endsWith(".md")) return "markdown";
        if (name.endsWith(".xml")) return "xml";
        return "plaintext";
    }

    private ResponseEntity<?> serveFile(java.io.File file, String artifactId) {
        try {
            Path path = file.toPath();
            String contentType = Files.probeContentType(path);
            if (contentType == null) {
                contentType = "application/octet-stream";
            }
            Resource resource = new FileSystemResource(file);
            String encoded = URLEncoder.encode(file.getName(), StandardCharsets.UTF_8)
                    .replace("+", "%20");
            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "inline; filename*=UTF-8''" + encoded)
                    .body(resource);
        } catch (IOException e) {
            log.error("Failed to serve artifact file: id={}, name={}", artifactId, file.getName(), e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
                    "文件读取失败", "/artifacts/" + artifactId);
        }
    }

    private ResponseEntity<?> error(HttpStatus status, String errorCode,
                                     String message, String path) {
        return ResponseEntity.status(status).body(Map.of(
                "error", errorCode,
                "message", message,
                "timestamp", LocalDateTime.now().toString(),
                "path", path
        ));
    }
}
