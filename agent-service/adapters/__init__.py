"""
AgentHub Agent Service — Agent 适配器包

本包封装了对不同 LLM 提供方的 API 调用，通过统一的 BaseAdapter
接口向上层暴露流式对话能力。

已实现的适配器：
    - ClaudeAdapter : Anthropic Claude Messages API
    - CodexAdapter  : OpenAI Chat Completions API

使用方式：
    from adapters.adapter_factory import AdapterFactory
    adapter = AdapterFactory.get_adapter("claude_code")
"""
