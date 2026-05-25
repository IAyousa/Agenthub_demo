from .base_adapter import BaseAdapter

class ClaudeAdapter(BaseAdapter):
    async def chat(self, message: str, history: list):
        # Implementation for Claude API
        pass
