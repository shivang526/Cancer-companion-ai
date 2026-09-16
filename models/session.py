from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import logging

from utils.database import save_message


logger = logging.getLogger("CancerSupportCompanion")


@dataclass
class UserSession:
    """Session management for user conversations"""

    session_id: str
    user_name: str
    created_at: datetime
    conversation_history: List[Dict]
    user_preferences: Dict

    def add_message(self, role: str, content: str):
        """Add a message to memory and persist it in SQLite."""

        timestamp = datetime.now().isoformat()

        message = {
            "timestamp": timestamp,
            "role": role,
            "content": content,
        }

        # Keep the existing in-memory conversation history
        self.conversation_history.append(message)

        # Persist the message in SQLite
        try:
            save_message(
                session_id=self.session_id,
                role=role,
                content=content,
                timestamp=timestamp,
            )

            logger.info(
                f"Session {self.session_id}: "
                f"Added {role} message and saved to SQLite"
            )

        except Exception as e:
            # Database failure should not crash the chatbot
            logger.error(
                f"Failed to persist message to SQLite: {e}"
            )