package com.agenthub.repository;

import com.agenthub.model.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ConversationRepository extends JpaRepository<Conversation, String> {

    List<Conversation> findByCreatedByOrderByUpdatedAtDesc(String createdBy);

    List<Conversation> findByCreatedByAndIsArchivedOrderByUpdatedAtDesc(String createdBy, Boolean isArchived);
}
