"""
Conversation Logger - Tracks and stores all agent interactions
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


class ConversationLogger:
    """
    Logs conversations, errors, and interactions to SQLite database.
    This data is used for RAG retrieval and self-improvement.
    """

    def __init__(self, db_path: str = "data/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def initialize(self):
        """Initialize the database schema"""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            # Conversations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    room_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT,
                    agent_response TEXT,
                    response_time_ms REAL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    metadata TEXT
                )
            """)

            # Performance metrics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metadata TEXT
                )
            """)

            # Feedback table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    feedback_type TEXT,
                    feedback_value TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)

            # Create indexes for better query performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
                ON conversations(timestamp)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_session
                ON performance_metrics(session_id)
            """)

            await db.commit()

        self._initialized = True
        logger.info(f"Conversation logger initialized: {self.db_path}")

    async def log_conversation(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        response_time_ms: float,
        room_name: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Log a conversation turn.

        Returns:
            conversation_id for this turn
        """
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO conversations
                (session_id, room_name, user_message, agent_response,
                 response_time_ms, success, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    room_name,
                    user_message,
                    agent_response,
                    response_time_ms,
                    success,
                    error_message,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def log_metric(
        self,
        session_id: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log a performance metric"""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO performance_metrics
                (session_id, metric_name, metric_value, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    metric_name,
                    metric_value,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            await db.commit()

    async def log_feedback(
        self,
        conversation_id: int,
        feedback_type: str,
        feedback_value: str,
    ):
        """Log user feedback about a conversation"""
        await self.initialize()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO feedback (conversation_id, feedback_type, feedback_value)
                VALUES (?, ?, ?)
                """,
                (conversation_id, feedback_type, feedback_value),
            )
            await db.commit()

    async def get_recent_conversations(
        self, limit: int = 100, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent conversations for analysis"""
        await self.initialize()

        query = "SELECT * FROM conversations"
        params: tuple = ()

        if session_id:
            query += " WHERE session_id = ?"
            params = (session_id,)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params = params + (limit,)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_performance_stats(
        self, session_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """Get performance statistics"""
        await self.initialize()

        query = """
            SELECT
                COUNT(*) as total_conversations,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_conversations,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed_conversations
            FROM conversations
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """
        params = [days]

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else {}

    async def get_error_patterns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error patterns for analysis"""
        await self.initialize()

        query = """
            SELECT error_message, COUNT(*) as count,
                   MAX(timestamp) as last_occurrence
            FROM conversations
            WHERE success = FALSE AND error_message IS NOT NULL
            GROUP BY error_message
            ORDER BY count DESC, last_occurrence DESC
            LIMIT ?
        """

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
