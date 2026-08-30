import logging
from collections import defaultdict
from typing import List, Dict

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages per-session conversation memory.
    Keeps the last N exchanges in memory.
    """
    
    def __init__(self, max_exchanges: int = 10):
        # Maps session_id to a list of message dicts: {"role": "user"/"assistant", "content": "..."}
        self.memory: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.max_exchanges = max_exchanges

    def add_user_message(self, session_id: str, content: str):
        self.memory[session_id].append({"role": "user", "content": content})
        self._trim_memory(session_id)

    def add_assistant_message(self, session_id: str, content: str):
        self.memory[session_id].append({"role": "assistant", "content": content})
        self._trim_memory(session_id)

    def get_history_string(self, session_id: str) -> str:
        """
        Formats the history for the prompt.
        """
        messages = self.memory.get(session_id, [])
        if not messages:
            return "No previous conversation."
            
        history = ""
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            history += f"{role}: {msg['content']}\n"
        return history

    def _trim_memory(self, session_id: str):
        """
        Ensures we only keep up to max_exchanges * 2 messages (user + assistant).
        """
        max_messages = self.max_exchanges * 2
        if len(self.memory[session_id]) > max_messages:
            self.memory[session_id] = self.memory[session_id][-max_messages:]

    def clear(self, session_id: str):
        if session_id in self.memory:
            del self.memory[session_id]

conversation_manager = ConversationManager()
