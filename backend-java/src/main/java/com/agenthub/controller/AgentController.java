package com.agenthub.controller;

import com.agenthub.model.Agent;
import com.agenthub.repository.AgentRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequiredArgsConstructor
public class AgentController {

    private final AgentRepository agentRepository;
    private final ObjectMapper objectMapper;

    private static final List<String> VALID_AGENT_TYPES = List.of("claude_code", "codex", "custom");

    @GetMapping("/agents")
    public ResponseEntity<?> list() {
        List<Map<String, Object>> agents = agentRepository.findAll().stream()
                .map(this::toSummary)
                .collect(Collectors.toList());
        return ResponseEntity.ok(Map.of("agents", agents));
    }

    @PostMapping("/agents")
    public ResponseEntity<?> create(@RequestBody Map<String, Object> body) {
        String name = (String) body.get("name");
        String type = (String) body.get("type");
        String systemPrompt = (String) body.get("systemPrompt");
        String avatarUrl = (String) body.get("avatarUrl");

        if (name == null || name.isBlank()) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", "name 不能为空", "/agents");
        }
        if (type == null || type.isBlank()) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", "type 不能为空", "/agents");
        }
        if (!VALID_AGENT_TYPES.contains(type.trim())) {
            return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR",
                    "type 必须是 claude_code、codex 或 custom", "/agents");
        }

        Agent agent = new Agent();
        agent.setName(name.trim());
        agent.setType(type.trim());
        agent.setSystemPrompt(systemPrompt != null ? systemPrompt : "");
        agent.setAvatarUrl(avatarUrl != null ? avatarUrl.trim() : null);
        agent.setCreatedBy("system");

        @SuppressWarnings("unchecked")
        List<String> capabilities = (List<String>) body.get("capabilities");
        if (capabilities != null) {
            try {
                agent.setCapabilities(objectMapper.writeValueAsString(capabilities));
            } catch (JsonProcessingException e) {
                return error(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR",
                        "capabilities 格式无效", "/agents");
            }
        }

        Agent saved = agentRepository.save(agent);
        log.info("Agent created: id={}, name={}, type={}", saved.getId(), saved.getName(), saved.getType());

        Map<String, Object> response = new LinkedHashMap<>(toSummary(saved));
        response.put("systemPrompt", saved.getSystemPrompt());
        response.put("createdAt", saved.getCreatedAt() != null
                ? saved.getCreatedAt().toString() : null);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/agents/{id}")
    public ResponseEntity<?> detail(@PathVariable String id) {
        Agent agent = agentRepository.findById(id).orElse(null);
        if (agent == null) {
            return error(HttpStatus.NOT_FOUND, "NOT_FOUND",
                    "Agent 不存在: " + id, "/agents/" + id);
        }
        return ResponseEntity.ok(toDetail(agent));
    }

    private Map<String, Object> toSummary(Agent agent) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("id", agent.getId());
        map.put("name", agent.getName());
        map.put("type", agent.getType());
        map.put("avatarUrl", agent.getAvatarUrl());
        map.put("capabilities", parseCapabilities(agent.getCapabilities()));
        // data.sql 预置 Agent 未设 created_by（为 null），API 创建的设为 "system"
        // 以此区分内置 Agent 与用户自定义 Agent
        map.put("isBuiltin", agent.getCreatedBy() == null);
        return map;
    }

    private Map<String, Object> toDetail(Agent agent) {
        Map<String, Object> map = toSummary(agent);
        map.put("systemPrompt", agent.getSystemPrompt());
        map.put("createdAt", agent.getCreatedAt() != null
                ? agent.getCreatedAt().toString() : null);
        return map;
    }

    private List<String> parseCapabilities(String capabilitiesJson) {
        if (capabilitiesJson == null || capabilitiesJson.isBlank()) {
            return Collections.emptyList();
        }
        try {
            return objectMapper.readValue(capabilitiesJson, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
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
