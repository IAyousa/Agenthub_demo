package com.agenthub.service;

import com.agenthub.model.Agent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Agent 元数据 Redis 缓存服务 — P2 阶段用于 Java↔Python 共享 Agent 列表。
 * 当前 Python 端使用 AGENT_REGISTRY fallback，P2 通过此服务实现 DB→Redis→Python 同步。
 */
@Service
public class AgentCacheService {

    private static final String AGENT_METADATA_PREFIX = "agent:metadata:";
    private static final String AGENT_LIST_KEY = "agent:list";

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public void saveAgent(Agent agent) {
        String key = AGENT_METADATA_PREFIX + agent.getId();
        redisTemplate.opsForValue().set(key, agent);
    }

    public void saveAgentsBatch(List<Agent> agents) {
        Map<String, Agent> agentMap = agents.stream()
                .collect(Collectors.toMap(agent -> AGENT_METADATA_PREFIX + agent.getId(), agent -> agent));
        redisTemplate.opsForValue().multiSet(agentMap);
        redisTemplate.opsForValue().set(AGENT_LIST_KEY, agents);
    }

    public Agent getAgentById(String id) {
        String key = AGENT_METADATA_PREFIX + id;
        return (Agent) redisTemplate.opsForValue().get(key);
    }

    @SuppressWarnings("unchecked")
    public List<Agent> getAllAgents() {
        Object listObj = redisTemplate.opsForValue().get(AGENT_LIST_KEY);
        if (listObj instanceof List) {
            return (List<Agent>) listObj;
        }
        return new ArrayList<>();
    }
}
