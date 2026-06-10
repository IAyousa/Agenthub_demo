package com.agenthub.controller;

import com.agenthub.dto.ArtifactDTO;
import com.agenthub.dto.InternalArtifactRequest;
import com.agenthub.model.Artifact;
import com.agenthub.service.ArtifactService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Slf4j
@RestController
@RequiredArgsConstructor
public class ArtifactController {

    private final ArtifactService artifactService;
    private final SimpMessagingTemplate messagingTemplate;

    @Value("${agent.workspace.root:${user.home}/agenthub_workspaces}")
    private String workspaceRoot;

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

    /**
     * Serve artifact by conversationId + filename — resolves relative paths in HTML iframes.
     * e.g. /artifacts/conversation/conv123/style.css → serves the latest matching artifact.
     */
    @GetMapping("/artifacts/conversation/{conversationId}/{filename}")
    public ResponseEntity<?> serveByConversationAndFilename(
            @PathVariable String conversationId,
            @PathVariable String filename) {
        try {
            List<Artifact> artifacts = artifactService.findByConversationIdAndFilename(conversationId, filename);
            if (artifacts.isEmpty()) {
                return error(HttpStatus.NOT_FOUND, "NOT_FOUND",
                        "文件不存在: " + filename, "/artifacts/conversation/" + conversationId + "/" + filename);
            }
            // Use the latest version (last in list) if multiple exist
            Artifact artifact = artifacts.get(artifacts.size() - 1);
            java.io.File file = artifactService.getFile(artifact.getId());
            if (file == null) {
                return error(HttpStatus.NOT_FOUND, "NOT_FOUND",
                        "产物文件丢失: " + filename, "/artifacts/conversation/" + conversationId + "/" + filename);
            }
            return serveFile(file, artifact.getId());
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(),
                    "/artifacts/conversation/" + conversationId + "/" + filename);
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
     * Saves file content → DB record only (no WebSocket push — use /batch for notifications).
     */
    @PostMapping("/internal/artifacts")
    public ResponseEntity<?> internalUpload(@RequestBody InternalArtifactRequest req) {
        try {
            ArtifactDTO dto = artifactService.saveFromContent(
                    req.getConversationId(), req.getMessageId(),
                    req.getFilename(), req.getContent(), req.getContentType());

            log.info("Internal artifact saved (silent): id={}, conversation={}, filename={}",
                    dto.getId(), req.getConversationId(), dto.getFilename());
            return ResponseEntity.status(HttpStatus.CREATED).body(dto);
        } catch (IllegalArgumentException e) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", e.getMessage(), "/internal/artifacts");
        } catch (IOException e) {
            log.error("Failed to save internal artifact", e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "产物保存失败", "/internal/artifacts");
        }
    }

    /**
     * Internal batch endpoint for Python workspace scanner to push multiple files at once.
     * Processes each file → pushes a single project_bundle WebSocket event.
     */
    @PostMapping("/internal/artifacts/batch")
    public ResponseEntity<?> internalBatchUpload(@RequestBody List<InternalArtifactRequest> requests) {
        List<Map<String, Object>> files = new ArrayList<>();
        String conversationId = null;
        String messageId = null;

        for (InternalArtifactRequest req : requests) {
            try {
                ArtifactDTO dto = artifactService.saveFromContent(
                        req.getConversationId(), req.getMessageId(),
                        req.getFilename(), req.getContent(), req.getContentType());

                if (conversationId == null) conversationId = req.getConversationId();
                if (messageId == null) messageId = req.getMessageId();

                Map<String, Object> fileInfo = new LinkedHashMap<>();
                fileInfo.put("artifactId", dto.getId());
                fileInfo.put("filename", dto.getFilename());
                fileInfo.put("path", req.getFilename());
                fileInfo.put("language", inferLanguage(req.getFilename()));
                fileInfo.put("previewUrl", "/artifacts/" + dto.getId());
                fileInfo.put("size", dto.getFileSize());
                files.add(fileInfo);
            } catch (IllegalArgumentException | IOException e) {
                log.warn("Batch upload: skipping file {} — {}", req.getFilename(), e.getMessage());
            }
        }

        // Push project_bundle summary to WebSocket — 延迟 1s 确保文本消息先到达前端
        if (conversationId != null && !files.isEmpty()) {
            final String topic = "/topic/conversation." + conversationId;
            final String finalMessageId = messageId;
            final List<Map<String, Object>> finalFiles = files;
            log.info("Batch upload: {} files → scheduling project_bundle push to {}", files.size(), topic);

            java.util.concurrent.CompletableFuture.delayedExecutor(
                    1500, java.util.concurrent.TimeUnit.MILLISECONDS).execute(() -> {
                Map<String, Object> bundle = new LinkedHashMap<>();
                bundle.put("type", "chunk");
                bundle.put("content", "项目成果已生成，共 " + finalFiles.size() + " 个文件");
                bundle.put("isComplete", true);
                bundle.put("agentId", "agent_system");
                bundle.put("agentName", "System");
                bundle.put("messageType", "project_bundle");
                bundle.put("messageId", finalMessageId);
                bundle.put("metadata", Map.of("files", finalFiles));
                messagingTemplate.convertAndSend(topic, bundle);
                log.info("Batch upload: pushed project_bundle to {}", topic);
            });
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("files", files);
        result.put("total", files.size());
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    /**
     * Download all project files for a conversation as a ZIP archive.
     * Scans the workspace directory and packages everything (excluding node_modules, .git, etc.).
     */
    @GetMapping("/conversations/{conversationId}/download")
    public ResponseEntity<?> downloadProject(@PathVariable String conversationId) {
        Path workspaceDir = Paths.get(workspaceRoot, conversationId);
        if (!Files.isDirectory(workspaceDir)) {
            return error(HttpStatus.NOT_FOUND, "NOT_FOUND",
                    "项目工作目录不存在: " + conversationId, "/conversations/" + conversationId + "/download");
        }

        try {
            java.io.File zipFile = File.createTempFile("project_" + conversationId + "_", ".zip");
            Set<String> ignoreDirs = Set.of(".claude", ".codex", ".git", "node_modules",
                    "__pycache__", ".venv", "venv", ".DS_Store");

            try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(zipFile))) {
                Files.walk(workspaceDir)
                        .filter(Files::isRegularFile)
                        .filter(p -> {
                            for (Path part : workspaceDir.relativize(p)) {
                                if (ignoreDirs.contains(part.toString())) return false;
                            }
                            return true;
                        })
                        .forEach(p -> {
                            try {
                                String entryName = workspaceDir.relativize(p).toString().replace("\\", "/");
                                zos.putNextEntry(new ZipEntry(entryName));
                                Files.copy(p, zos);
                                zos.closeEntry();
                            } catch (IOException ignored) {}
                        });
            }

            Resource resource = new FileSystemResource(zipFile);
            String downloadName = URLEncoder.encode("project_" + conversationId + ".zip",
                    StandardCharsets.UTF_8).replace("+", "%20");

            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType("application/zip"))
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename*=UTF-8''" + downloadName)
                    .body(resource);
        } catch (IOException e) {
            log.error("Failed to zip project for conversation: {}", conversationId, e);
            return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
                    "项目打包失败", "/conversations/" + conversationId + "/download");
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

    private String mimeType(String filename) {
        if (filename == null) return "application/octet-stream";
        String name = filename.toLowerCase();
        if (name.endsWith(".html") || name.endsWith(".htm")) return "text/html";
        if (name.endsWith(".css")) return "text/css";
        if (name.endsWith(".js")) return "application/javascript";
        if (name.endsWith(".ts")) return "text/typescript";
        if (name.endsWith(".tsx")) return "text/typescript";
        if (name.endsWith(".jsx")) return "text/javascript";
        if (name.endsWith(".json")) return "application/json";
        if (name.endsWith(".xml")) return "application/xml";
        if (name.endsWith(".svg")) return "image/svg+xml";
        if (name.endsWith(".png")) return "image/png";
        if (name.endsWith(".jpg") || name.endsWith(".jpeg")) return "image/jpeg";
        if (name.endsWith(".gif")) return "image/gif";
        if (name.endsWith(".ico")) return "image/x-icon";
        if (name.endsWith(".woff2")) return "font/woff2";
        if (name.endsWith(".woff")) return "font/woff";
        if (name.endsWith(".ttf")) return "font/ttf";
        if (name.endsWith(".md")) return "text/markdown";
        if (name.endsWith(".py")) return "text/plain";
        if (name.endsWith(".java")) return "text/plain";
        if (name.endsWith(".yaml") || name.endsWith(".yml")) return "text/yaml";
        return "text/plain";
    }

    private ResponseEntity<?> serveFile(java.io.File file, String artifactId) {
        String contentType = mimeType(file.getName());
        Resource resource = new FileSystemResource(file);
        String encoded = URLEncoder.encode(file.getName(), StandardCharsets.UTF_8)
                .replace("+", "%20");
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "inline; filename*=UTF-8''" + encoded)
                .body(resource);
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
