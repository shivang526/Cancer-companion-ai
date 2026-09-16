import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


# Store the database in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "companionai.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create database tables if they do not already exist."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id)
                    REFERENCES sessions(session_id)
            )
        """)

        # Index for faster conversation retrieval
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id)
        """)

        connection.commit()

    finally:
        connection.close()


def create_session(
    session_id: str,
    user_name: str,
    created_at: str
):
    """Persist a new session."""

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO sessions
            (session_id, user_name, created_at)
            VALUES (?, ?, ?)
            """,
            (session_id, user_name, created_at)
        )

        connection.commit()

    finally:
        connection.close()


def save_message(
    session_id: str,
    role: str,
    content: str,
    timestamp: str
):
    """Persist a conversation message."""

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO messages
            (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, timestamp)
        )

        connection.commit()

    finally:
        connection.close()


def get_messages(session_id: str) -> List[Dict]:
    """Retrieve all messages belonging to a session."""

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT role, content, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_session(session_id: str) -> Optional[Dict]:
    """Retrieve session information."""

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT session_id, user_name, created_at
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,)
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()