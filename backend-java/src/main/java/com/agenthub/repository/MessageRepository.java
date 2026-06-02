package com.agenthub.repository;

import com.agenthub.model.Message;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MessageRepository extends JpaRepository<Message, String> {

    List<Message> findByConversationIdOrderByCreatedAtAsc(String conversationId);

    List<Message> findByConversationIdAndIsPinnedTrue(String conversationId);

    void deleteByConversationId(String conversationId);

    /**
     * 根据会话ID分页查询消息，按创建时间倒序
     */
    Page<Message> findByConversationIdOrderByCreatedAtDesc(String conversationId, Pageable pageable);
}
