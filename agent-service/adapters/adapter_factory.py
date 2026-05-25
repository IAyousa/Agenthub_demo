from .claude_adapter import ClaudeAdapter

class AdapterFactory:
    @staticmethod
    def get_adapter(name: str):
        if name == "claude":
            return ClaudeAdapter()
        return None
