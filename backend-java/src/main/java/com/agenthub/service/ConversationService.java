package com.agenthub.service;

import com.agenthub.model.Agent;
import com.agenthub.model.Conversation;
import com.agenthub.repository.AgentRepository;
import com.agenthub.repository.ConversationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ConversationService {

    private final ConversationRepository conversationRepository;
    private final AgentRepository agentRepository;

    /**
     * 创建会话，可指定初始 Agent 列表
     */
    @Transactional
    public Conversation createConversation(String title, String type, String createdBy, List<String> agentIds) {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("会话标题不能为空");
        }
        if (type == null || type.isBlank()) {
            throw new IllegalArgumentException("会话类型不能为空");
        }
        if (createdBy == null || createdBy.isBlank()) {
            throw new IllegalArgumentException("创建者不能为空");
        }

        Conversation conversation = new Conversation();
        conversation.setTitle(title.trim());
        conversation.setType(type);
        conversation.setCreatedBy(createdBy);
        conversation.setIsArchived(false);

        if (agentIds != null && !agentIds.isEmpty()) {
            Set<Agent> agents = agentIds.stream()
                    .map(agentId -> agentRepository.findById(agentId)
                            .orElseThrow(() -> new IllegalArgumentException("Agent 不存在: " + agentId)))
                    .collect(Collectors.toSet());
            conversation.setAgents(agents);
        }

        Conversation saved = conversationRepository.save(conversation);
        log.info("创建会话成功: id={}, title={}, createdBy={}", saved.getId(), saved.getTitle(), saved.getCreatedBy());
        return saved;
    }

    /**
     * 更新会话基本信息
     */
    @Transactional
    public Conversation updateConversation(String id, String title, String type, Boolean isArchived) {
        Conversation conversation = getConversationById(id);
        if (title != null && !title.isBlank()) {
            conversation.setTitle(title.trim());
        }
        if (type != null && !type.isBlank()) {
            conversation.setType(type);
        }
        if (isArchived != null) {
            conversation.setIsArchived(isArchived);
        }
        Conversation updated = conversationRepository.save(conversation);
        log.info("更新会话成功: id={}", updated.getId());
        return updated;
    }

    /**
     * 根据 ID 删除会话
     */
    @Transactional
    public void deleteConversation(String id) {
        if (!conversationRepository.existsById(id)) {
            throw new IllegalArgumentException("会话不存在: " + id);
        }
        conversationRepository.deleteById(id);
        log.info("删除会话成功: id={}", id);
    }

    /**
     * 根据 ID 查询会话
     */
    @Transactional(readOnly = true)
    public Conversation getConversationById(String id) {
        return conversationRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("会话不存在: " + id));
    }

    /**
     * 查询用户的会话列表（按更新时间倒序，不含已归档）
     */
    @Transactional(readOnly = true)
    public List<Conversation> getUserConversations(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("用户ID不能为空");
        }
        return conversationRepository.findByCreatedByAndIsArchivedOrderByUpdatedAtDesc(userId, false);
    }

    /**
     * 查询用户的归档会话列表
     */
    @Transactional(readOnly = true)
    public List<Conversation> getUserArchivedConversations(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("用户ID不能为空");
        }
        return conversationRepository.findByCreatedByAndIsArchivedOrderByUpdatedAtDesc(userId, true);
    }

    /**
     * 向会话中添加 Agent
     */
    @Transactional
    public Conversation addAgentToConversation(String conversationId, String agentId) {
        Conversation conversation = getConversationById(conversationId);
        Agent agent = agentRepository.findById(agentId)
                .orElseThrow(() -> new IllegalArgumentException("Agent 不存在: " + agentId));

        conversation.getAgents().add(agent);
        Conversation updated = conversationRepository.save(conversation);
        log.info("向会话添加 Agent 成功: conversationId={}, agentId={}", conversationId, agentId);
        return updated;
    }

    /**
     * 从会话中移除 Agent
     */
    @Transactional
    public Conversation removeAgentFromConversation(String conversationId, String agentId) {
        Conversation conversation = getConversationById(conversationId);
        Agent agent = agentRepository.findById(agentId)
                .orElseThrow(() -> new IllegalArgumentException("Agent 不存在: " + agentId));

        conversation.getAgents().remove(agent);
        Conversation updated = conversationRepository.save(conversation);
        log.info("从会话移除 Agent 成功: conversationId={}, agentId={}", conversationId, agentId);
        return updated;
    }

    /**
     * 归档或取消归档会话
     */
    @Transactional
    public Conversation archiveConversation(String id, boolean archive) {
        Conversation conversation = getConversationById(id);
        conversation.setIsArchived(archive);
        Conversation updated = conversationRepository.save(conversation);
        log.info("会话归档状态变更: id={}, isArchived={}", id, archive);
        return updated;
    }
}
