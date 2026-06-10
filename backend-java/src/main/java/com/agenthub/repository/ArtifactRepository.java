package com.agenthub.repository;

import com.agenthub.model.Artifact;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ArtifactRepository extends JpaRepository<Artifact, String> {

    List<Artifact> findByConversationId(String conversationId);

    List<Artifact> findByConversationIdAndMessageId(String conversationId, String messageId);

    /** 按会话ID+文件名查找（用于 iframe 中相对路径资源解析） */
    List<Artifact> findByConversationIdAndFilename(String conversationId, String filename);
}
