"""
Short-Term Memory: Conversation Buffer
Maintains a rolling window of the last N conversation turns
so the LLM has context for follow-up questions.
"""

class ConversationMemory:
    def __init__(self, max_turns=20, system_prompt=None):
        self.max_turns = max_turns
        self.history = []
        self.system_prompt = system_prompt or (
            "You are JARVIS, an advanced AI assistant. "
            "You are intelligent, witty, warm, and empathetic. "
            "You speak in a polished manner — addressing the user as 'Sir' occasionally. "
            "You can open apps, search the web, open websites, and have real conversations."
        )

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant_message(self, message):
        self.history.append({"role": "assistant", "content": message})
        self._trim()

    def get_messages(self):
        """Return the full message list including system prompt."""
        return [{"role": "system", "content": self.system_prompt}] + self.history

    def _trim(self):
        """Keep only the last N turns (each turn = 2 messages)."""
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def clear(self):
        self.history = []

    def get_summary(self):
        """Return a brief summary of conversation state for debugging."""
        return {
            "total_messages": len(self.history),
            "max_turns": self.max_turns,
            "last_user_msg": next(
                (m["content"] for m in reversed(self.history) if m["role"] == "user"),
                None
            )
        }
