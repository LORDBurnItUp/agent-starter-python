"""
RAG Manager - Coordinates the self-improvement system
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .conversation_logger import ConversationLogger
from .knowledge_retriever import KnowledgeRetriever
from .performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class RAGManager:
    """
    Main coordinator for the RAG-based self-improvement system.
    Manages conversation logging, knowledge retrieval, and performance tracking.
    """

    def __init__(
        self,
        enable_rag: bool = True,
        db_path: str = "data/conversations.db",
        chroma_path: str = "data/chroma_db",
        auto_improve: bool = True,
        improvement_interval_conversations: int = 100,
    ):
        """
        Initialize RAG Manager.

        Args:
            enable_rag: Enable RAG features
            db_path: Path to SQLite database
            chroma_path: Path to ChromaDB directory
            auto_improve: Automatically generate improvement suggestions
            improvement_interval_conversations: Generate report every N conversations
        """
        self.enable_rag = enable_rag
        self.auto_improve = auto_improve
        self.improvement_interval = improvement_interval_conversations
        self.conversation_count = 0

        if not enable_rag:
            logger.info("RAG system is disabled")
            return

        # Initialize components
        self.logger = ConversationLogger(db_path)
        self.retriever = KnowledgeRetriever(chroma_path)
        self.tracker = PerformanceTracker()

        self._initialized = False
        logger.info("RAG Manager initialized")

    async def initialize(self):
        """Initialize the RAG system"""
        if not self.enable_rag or self._initialized:
            return

        await self.logger.initialize()
        self._initialized = True
        logger.info("RAG Manager fully initialized")

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
    ) -> Optional[int]:
        """
        Log a conversation and add it to the knowledge base.

        Returns:
            conversation_id if successful, None otherwise
        """
        if not self.enable_rag:
            return None

        await self.initialize()

        try:
            # Log to database
            conversation_id = await self.logger.log_conversation(
                session_id=session_id,
                user_message=user_message,
                agent_response=agent_response,
                response_time_ms=response_time_ms,
                room_name=room_name,
                success=success,
                error_message=error_message,
                metadata=metadata,
            )

            # Add to vector database for RAG retrieval (only successful conversations)
            if success:
                await self.retriever.add_conversation(
                    conversation_id=f"conv_{conversation_id}",
                    user_message=user_message,
                    agent_response=agent_response,
                    metadata={
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "success": success,
                        "response_time_ms": response_time_ms,
                        **(metadata or {}),
                    },
                )

            # Track performance
            self.tracker.record_metric(
                session_id=session_id,
                metric_name="response_time",
                metric_value=response_time_ms,
                metadata={"success": success},
            )

            # Increment conversation count and check for auto-improvement
            self.conversation_count += 1
            if (
                self.auto_improve
                and self.conversation_count % self.improvement_interval == 0
            ):
                asyncio.create_task(self._generate_improvement_report())

            return conversation_id

        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
            return None

    async def get_relevant_context(
        self,
        query: str,
        n_results: int = 3,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from past conversations.

        Args:
            query: Current user message or query
            n_results: Number of relevant contexts to retrieve
            session_id: Optional session filter

        Returns:
            List of relevant contexts with metadata
        """
        if not self.enable_rag:
            return []

        await self.initialize()

        try:
            # Build metadata filter if session_id provided
            filter_metadata = {"session_id": session_id} if session_id else None

            contexts = await self.retriever.retrieve_relevant_context(
                query=query,
                n_results=n_results,
                filter_metadata=filter_metadata,
            )

            return contexts

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    async def enhance_agent_instructions(
        self, base_instructions: str, current_query: str
    ) -> str:
        """
        Enhance agent instructions with relevant context from past interactions.

        Args:
            base_instructions: Base agent instructions
            current_query: Current user query

        Returns:
            Enhanced instructions with relevant context
        """
        if not self.enable_rag:
            return base_instructions

        contexts = await self.get_relevant_context(current_query, n_results=2)

        if not contexts:
            return base_instructions

        # Build context section
        context_text = "\n\nRelevant past interactions:\n"
        for i, ctx in enumerate(contexts, 1):
            context_text += f"\n{i}. {ctx['document']}\n"

        enhanced_instructions = f"""{base_instructions}

{context_text}

Use the above context if relevant to the current conversation, but prioritize the user's current needs."""

        return enhanced_instructions

    async def generate_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate a performance report for the specified time period.

        Args:
            days: Number of days to include in report

        Returns:
            Performance report with suggestions
        """
        if not self.enable_rag:
            return {"status": "disabled"}

        await self.initialize()

        # Get recent conversations
        conversations = await self.logger.get_recent_conversations(limit=1000)

        # Filter by time period
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        recent_conversations = [
            c
            for c in conversations
            if datetime.fromisoformat(c["timestamp"]) > cutoff
        ]

        # Generate report
        report = self.tracker.generate_improvement_report(recent_conversations)

        # Add database stats
        db_stats = await self.logger.get_performance_stats(days=days)
        report["database_stats"] = db_stats

        # Add knowledge base stats
        kb_stats = await self.retriever.get_statistics()
        report["knowledge_base_stats"] = kb_stats

        return report

    async def _generate_improvement_report(self):
        """Internal method to auto-generate improvement reports"""
        try:
            report = await self.generate_performance_report(days=1)
            logger.info(
                f"Auto-generated improvement report: {report['summary']['total_suggestions']} suggestions"
            )

            # Log high-priority suggestions
            high_priority = [
                s for s in report["suggestions"] if s["severity"] == "high"
            ]
            for suggestion in high_priority:
                logger.warning(
                    f"High priority suggestion: {suggestion['suggestion']}"
                )

        except Exception as e:
            logger.error(f"Error generating improvement report: {e}")

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary for a specific session"""
        if not self.enable_rag:
            return {"status": "disabled"}

        await self.initialize()

        conversations = await self.logger.get_recent_conversations(
            session_id=session_id, limit=1000
        )

        summary = {
            "session_id": session_id,
            "total_conversations": len(conversations),
            "successful_conversations": sum(
                1 for c in conversations if c.get("success", True)
            ),
            "failed_conversations": sum(
                1 for c in conversations if not c.get("success", True)
            ),
        }

        if conversations:
            response_times = [
                c["response_time_ms"]
                for c in conversations
                if c.get("response_time_ms")
            ]
            if response_times:
                summary["avg_response_time_ms"] = sum(response_times) / len(
                    response_times
                )

        return summary

    async def add_pattern(
        self, pattern_type: str, description: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a learned pattern to the knowledge base.

        Args:
            pattern_type: Type of pattern (e.g., "error_recovery", "user_preference")
            description: Description of the pattern
            metadata: Additional metadata
        """
        if not self.enable_rag:
            return

        await self.initialize()

        pattern_id = f"pattern_{uuid.uuid4().hex[:8]}"
        await self.retriever.add_pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=description,
            metadata=metadata,
        )

        logger.info(f"Added pattern: {pattern_type} - {description}")

    async def get_error_insights(self) -> Dict[str, Any]:
        """Get insights about error patterns"""
        if not self.enable_rag:
            return {"status": "disabled"}

        await self.initialize()

        error_patterns = await self.logger.get_error_patterns(limit=20)

        return {
            "total_unique_errors": len(error_patterns),
            "error_patterns": error_patterns,
        }

    def is_enabled(self) -> bool:
        """Check if RAG system is enabled"""
        return self.enable_rag

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        if not self.enable_rag:
            return {"enabled": False}

        await self.initialize()

        kb_stats = await self.retriever.get_statistics()
        db_stats = await self.logger.get_performance_stats(days=7)

        return {
            "enabled": True,
            "initialized": self._initialized,
            "total_conversations_logged": self.conversation_count,
            "knowledge_base": kb_stats,
            "database_stats": db_stats,
            "auto_improve": self.auto_improve,
            "improvement_interval": self.improvement_interval,
        }
