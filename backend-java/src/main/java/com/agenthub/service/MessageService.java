package com.agenthub.service;

import com.agenthub.model.Conversation;
import com.agenthub.model.Message;
import com.agenthub.repository.ConversationRepository;
import com.agenthub.repository.MessageRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

@Slf4j
@Service
@RequiredArgsConstructor
public class MessageService {

    private final MessageRepository messageRepository;
    private final ConversationRepository conversationRepository;

    private static final Set<String> VALID_SENDER_TYPES = Set.of("user", "assistant");
    private static final int MAX_PAGE_SIZE = 100;

    /**
     * 保存用户/助手消息到数据库，并同步更新会话的更新时间
     *
     * @param conversationId 会话ID
     * @param senderId       发送者ID
     * @param senderType     发送者类型（user / assistant）
     * @param content        消息内容
     * @param messageType    消息类型（如 text）
     * @param agentName      Agent名称（助手消息时可填）
     * @return 保存后的消息实体
     */
    @Transactional
    public Message saveMessage(String conversationId, String senderId, String senderType,
                               String content, String messageType, String agentName) {
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        if (senderId == null || senderId.isBlank()) {
            throw new IllegalArgumentException("发送者ID不能为空");
        }
        if (senderType == null || senderType.isBlank()) {
            throw new IllegalArgumentException("发送者类型不能为空");
        }
        if (!VALID_SENDER_TYPES.contains(senderType.toLowerCase())) {
            throw new IllegalArgumentException("发送者类型无效，仅支持: user, assistant");
        }
        if (content == null || content.isBlank()) {
            throw new IllegalArgumentException("消息内容不能为空");
        }
        if (messageType == null || messageType.isBlank()) {
            throw new IllegalArgumentException("消息类型不能为空");
        }

        Conversation conversation = conversationRepository.findById(conversationId)
                .orElseThrow(() -> new IllegalArgumentException("会话不存在: " + conversationId));

        Message message = new Message();
        message.setConversationId(conversationId);
        message.setSenderId(senderId);
        message.setSenderType(senderType.toLowerCase());
        message.setContent(content.trim());
        message.setMessageType(messageType);
        message.setAgentName(agentName != null ? agentName.trim() : null);
        message.setIsPinned(false);

        Message saved = messageRepository.save(message);

        conversation.setUpdatedAt(LocalDateTime.now());
        conversationRepository.save(conversation);

        log.info("保存消息成功: id={}, conversationId={}, senderType={}", saved.getId(), conversationId, senderType);
        return saved;
    }

    /**
     * 根据会话ID分页查询历史消息（按时间倒序）
     *
     * @param conversationId 会话ID
     * @param page           页码（从0开始）
     * @param size           每页条数
     * @return 分页消息列表
     */
    @Transactional(readOnly = true)
    public Page<Message> getMessagesByConversationId(String conversationId, int page, int size) {
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        if (page < 0) {
            throw new IllegalArgumentException("页码不能小于0");
        }
        if (size <= 0 || size > MAX_PAGE_SIZE) {
            throw new IllegalArgumentException("每页条数必须在 1-" + MAX_PAGE_SIZE + " 之间");
        }

        if (!conversationRepository.existsById(conversationId)) {
            throw new IllegalArgumentException("会话不存在: " + conversationId);
        }

        Pageable pageable = PageRequest.of(page, size);
        return messageRepository.findByConversationIdOrderByCreatedAtDesc(conversationId, pageable);
    }

    /**
     * 获取最近N条消息，并按时间正序组装成对话上下文（供AI调用）
     *
     * @param conversationId 会话ID
     * @param limit          最近消息条数
     * @return 按时间正序排列的消息列表
     */
    @Transactional(readOnly = true)
    public List<Message> buildConversationContext(String conversationId, int limit) {
        if (conversationId == null || conversationId.isBlank()) {
            throw new IllegalArgumentException("会话ID不能为空");
        }
        if (limit <= 0) {
            throw new IllegalArgumentException("消息条数必须大于0");
        }

        if (!conversationRepository.existsById(conversationId)) {
            throw new IllegalArgumentException("会话不存在: " + conversationId);
        }

        Pageable pageable = PageRequest.of(0, limit);
        List<Message> recentMessages = new ArrayList<>(
                messageRepository.findByConversationIdOrderByCreatedAtDesc(conversationId, pageable).getContent()
        );

        // 将数据库倒序结果反转为正序，以符合AI对话上下文的时间线
        Collections.reverse(recentMessages);

        log.debug("构建对话上下文成功: conversationId={}, limit={}, actualSize={}",
                conversationId, limit, recentMessages.size());
        return recentMessages;
    }

    /**
     * 置顶消息
     *
     * @param messageId 消息ID
     * @return 更新后的消息实体
     */
    @Transactional
    public Message pinMessage(String messageId) {
        Message message = getMessageById(messageId);
        if (Boolean.TRUE.equals(message.getIsPinned())) {
            log.warn("消息已是置顶状态: messageId={}", messageId);
            return message;
        }
        message.setIsPinned(true);
        Message updated = messageRepository.save(message);
        log.info("置顶消息成功: messageId={}, conversationId={}", updated.getId(), updated.getConversationId());
        return updated;
    }

    /**
     * 取消置顶消息
     *
     * @param messageId 消息ID
     * @return 更新后的消息实体
     */
    @Transactional
    public Message unpinMessage(String messageId) {
        Message message = getMessageById(messageId);
        if (Boolean.FALSE.equals(message.getIsPinned())) {
            log.warn("消息已是未置顶状态: messageId={}", messageId);
            return message;
        }
        message.setIsPinned(false);
        Message updated = messageRepository.save(message);
        log.info("取消置顶消息成功: messageId={}, conversationId={}", updated.getId(), updated.getConversationId());
        return updated;
    }

    /**
     * 根据ID查询消息
     *
     * @param messageId 消息ID
     * @return 消息实体
     */
    @Transactional(readOnly = true)
    public Message getMessageById(String messageId) {
        if (messageId == null || messageId.isBlank()) {
            throw new IllegalArgumentException("消息ID不能为空");
        }
        return messageRepository.findById(messageId)
                .orElseThrow(() -> new IllegalArgumentException("消息不存在: " + messageId));
    }
}
