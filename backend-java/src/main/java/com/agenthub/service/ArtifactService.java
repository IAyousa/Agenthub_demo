package com.agenthub.service;

import com.agenthub.dto.ArtifactDTO;
import com.agenthub.model.Artifact;
import com.agenthub.repository.ArtifactRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ArtifactService {

    private final ArtifactRepository artifactRepository;

    @Value("${artifact.storage.path:./artifacts}")
    private String storagePath;

    @PostConstruct
    public void init() {
        Path baseDir = Paths.get(storagePath);
        if (!Files.isDirectory(baseDir)) {
            return;
        }
        int imported = 0;
        try (var convDirs = Files.list(baseDir)) {
            for (Path convDir : convDirs.toList()) {
                if (!Files.isDirectory(convDir)) continue;
                String conversationId = convDir.getFileName().toString();
                try (var msgDirs = Files.list(convDir)) {
                    for (Path msgDir : msgDirs.toList()) {
                        if (!Files.isDirectory(msgDir)) continue;
                        String messageId = msgDir.getFileName().toString();
                        try (var files = Files.list(msgDir)) {
                            for (Path file : files.toList()) {
                                if (!Files.isRegularFile(file)) continue;
                                String storedName = file.getFileName().toString();
                                // 检查此孤儿文件是否已在之前的启动中恢复过
                                boolean alreadyImported = artifactRepository
                                    .findByConversationIdAndMessageId(conversationId, messageId)
                                    .stream()
                                    .anyMatch(a -> storedName.equals(a.getStoredName()));
                                if (alreadyImported) continue;

                                BasicFileAttributes attrs = Files.readAttributes(file, BasicFileAttributes.class);
                                Artifact artifact = new Artifact();
                                artifact.setId(java.util.UUID.randomUUID().toString());
                                artifact.setStoredName(storedName);
                                // 孤儿文件无法恢复原始文件名，回退使用 storedName
                                artifact.setFilename(storedName);
                                artifact.setFileSize(attrs.size());
                                artifact.setConversationId(conversationId);
                                artifact.setMessageId(messageId);
                                artifact.setCreatedAt(LocalDateTime.ofInstant(
                                        attrs.creationTime().toInstant(), ZoneId.systemDefault()));
                                artifactRepository.save(artifact);
                                imported++;
                            }
                        }
                    }
                }
            }
        } catch (IOException e) {
            log.error("Failed to scan artifact directory for orphan files", e);
        }
        if (imported > 0) {
            log.info("Imported {} orphan artifact files into registry", imported);
        }
    }

    @Transactional
    public ArtifactDTO save(MultipartFile file, String conversationId, String messageId) throws IOException {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("产物文件不能为空");
        }
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        validatePathSegment(conversationId);
        if (messageId != null && !messageId.isBlank()) {
            validatePathSegment(messageId);
        }

        String originalFilename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "untitled";
        validatePathSegment(originalFilename);
        String ext = "";
        int dot = originalFilename.lastIndexOf('.');
        if (dot > 0) {
            ext = originalFilename.substring(dot);
        }

        String id = java.util.UUID.randomUUID().toString();
        String storedName = id + ext;

        Path dir = Paths.get(storagePath, conversationId, messageId != null ? messageId : "");
        Files.createDirectories(dir);

        Path filePath = dir.resolve(storedName);
        file.transferTo(filePath);

        Artifact artifact = new Artifact();
        artifact.setId(id);
        artifact.setFilename(originalFilename);
        artifact.setStoredName(storedName);
        artifact.setFileSize(file.getSize());
        artifact.setConversationId(conversationId);
        artifact.setMessageId(messageId != null && !messageId.isBlank() ? messageId : null);

        Artifact saved = artifactRepository.save(artifact);
        log.info("Artifact saved: id={}, filename={}, path={}", saved.getId(), originalFilename, filePath);
        return toDTO(saved);
    }

    /**
     * Save artifact from text content (used by /internal/artifacts endpoint).
     * Writes the content string directly to disk — no MultipartFile needed.
     */
    @Transactional
    public ArtifactDTO saveFromContent(String conversationId, String messageId, String filename,
                                        String content, String contentType) throws IOException {
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        validatePathSegment(conversationId);
        if (messageId != null && !messageId.isBlank()) {
            validatePathSegment(messageId);
        }
        if (filename == null || filename.isBlank()) {
            filename = "untitled";
        }
        validatePathSegment(filename);
        if (content == null) {
            content = "";
        }

        String ext = "";
        int dot = filename.lastIndexOf('.');
        if (dot > 0) {
            ext = filename.substring(dot);
        }

        String id = java.util.UUID.randomUUID().toString();
        String storedName = id + ext;

        Path dir = Paths.get(storagePath, conversationId, messageId != null ? messageId : "");
        Files.createDirectories(dir);

        Path filePath = dir.resolve(storedName);
        Files.writeString(filePath, content, StandardCharsets.UTF_8);

        Artifact artifact = new Artifact();
        artifact.setId(id);
        artifact.setFilename(filename);
        artifact.setStoredName(storedName);
        artifact.setFileSize((long) content.getBytes(StandardCharsets.UTF_8).length);
        artifact.setConversationId(conversationId);
        artifact.setMessageId(messageId != null && !messageId.isBlank() ? messageId : null);

        Artifact saved = artifactRepository.save(artifact);
        log.info("Artifact saved from content: id={}, filename={}, path={}", saved.getId(), filename, filePath);
        return toDTO(saved);
    }

    @Transactional(readOnly = true)
    public List<ArtifactDTO> getByConversation(String conversationId) {
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        return artifactRepository.findByConversationId(conversationId).stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<Artifact> findByConversationIdAndFilename(String conversationId, String filename) {
        return artifactRepository.findByConversationIdAndFilename(conversationId, filename);
    }

    @Transactional(readOnly = true)
    public java.io.File getFile(String id) {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("产物ID不能为空");
        }
        Artifact artifact = artifactRepository.findById(id).orElse(null);
        if (artifact == null) {
            return null;
        }
        Path filePath = buildFilePath(artifact);
        java.io.File file = filePath.toFile();
        if (file.exists()) {
            return file;
        }
        log.warn("Artifact record exists but file missing on disk: id={}, path={}", id, filePath);
        return null;
    }

    @Transactional(rollbackFor = Exception.class)
    public void delete(String id) throws IOException {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("产物ID不能为空");
        }
        Artifact artifact = artifactRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("产物不存在: " + id));

        Path filePath = buildFilePath(artifact);
        try {
            Files.deleteIfExists(filePath);
        } catch (IOException e) {
            log.error("Failed to delete artifact file on disk: id={}, path={}", id, filePath, e);
            throw e;
        }

        artifactRepository.delete(artifact);
        log.info("Artifact deleted: id={}", id);
    }

    private Path buildFilePath(Artifact artifact) {
        return Paths.get(storagePath,
                artifact.getConversationId(),
                artifact.getMessageId() != null ? artifact.getMessageId() : "",
                artifact.getStoredName());
    }

    private ArtifactDTO toDTO(Artifact artifact) {
        ArtifactDTO dto = new ArtifactDTO();
        dto.setId(artifact.getId());
        dto.setFilename(artifact.getFilename());
        dto.setFileSize(artifact.getFileSize());
        dto.setConversationId(artifact.getConversationId());
        dto.setMessageId(artifact.getMessageId());
        dto.setCreatedAt(artifact.getCreatedAt());
        return dto;
    }

    private void validatePathSegment(String segment) {
        if (segment.contains("..") || segment.contains("/") || segment.contains("\\")) {
            throw new IllegalArgumentException("参数包含非法字符: " + segment);
        }
    }
}
