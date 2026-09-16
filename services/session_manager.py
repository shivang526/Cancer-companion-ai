from datetime import datetime
from typing import Dict, Optional

from utils.logger import logger
from models.session import UserSession

from utils.database import (
    initialize_database,
    create_session,
    get_messages,
    get_session as get_database_session,
)


class SessionManager:
    """Manages user sessions and persistent SQLite storage."""

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}

        # Make sure the SQLite database and tables exist
        initialize_database()

        logger.info(
            "SessionManager: Initialized session management "
            "with SQLite persistence"
        )

    def create_session(self, user_name: str) -> UserSession:

        session_id = (
            f"session_{len(self.sessions) + 1}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        created_at = datetime.now()

        session = UserSession(
            session_id=session_id,
            user_name=user_name,
            created_at=created_at,
            conversation_history=[],
            user_preferences={},
        )

        # Keep session in memory
        self.sessions[session_id] = session

        # Persist session in SQLite
        create_session(
            session_id=session_id,
            user_name=user_name,
            created_at=created_at.isoformat(),
        )

        logger.info(
            f"SessionManager: Created and persisted "
            f"session {session_id}"
        )

        return session

    def get_session(
        self,
        session_id: str
    ) -> Optional[UserSession]:

        # First check the in-memory sessions
        session = self.sessions.get(session_id)

        if session:
            return session

        # If not in memory, try SQLite
        database_session = get_database_session(session_id)

        if not database_session:
            return None

        # Recover conversation history from SQLite
        messages = get_messages(session_id)

        session = UserSession(
            session_id=database_session["session_id"],
            user_name=database_session["user_name"],
            created_at=datetime.fromisoformat(
                database_session["created_at"]
            ),
            conversation_history=messages,
            user_preferences={},
        )

        # Put recovered session back into memory
        self.sessions[session_id] = session

        logger.info(
            f"SessionManager: Restored session "
            f"{session_id} from SQLite"
        )

        return session

    def save_session_state(self, session: UserSession):
        """Session messages are persisted through add_message()."""

        logger.info(
            f"SessionManager: Saved state for session "
            f"{session.session_id}"
        )

    def get_all_sessions(self) -> Dict[str, UserSession]:
        """Return all active user sessions."""

        return self.sessions.copy()