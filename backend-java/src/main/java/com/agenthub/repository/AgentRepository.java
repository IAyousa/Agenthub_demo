package com.agenthub.repository;

import com.agenthub.model.Agent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface AgentRepository extends JpaRepository<Agent, String> {

    List<Agent> findByType(String type);

    List<Agent> findByCreatedBy(String createdBy);
}
