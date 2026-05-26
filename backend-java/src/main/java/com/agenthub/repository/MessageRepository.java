package com.agenthub.repository;

import com.agenthub.model.Message;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MessageRepository extends JpaRepository<Message, String> {

    List<Message> findByConversationIdOrderByCreatedAtAsc(String conversationId);

    List<Message> findByConversationIdAndIsPinnedTrue(String conversationId);

    void deleteByConversationId(String conversationId);
}
