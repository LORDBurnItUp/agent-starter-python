"""
Tests for RAG System Components
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from rag_system import (
    ConversationLogger,
    KnowledgeRetriever,
    PerformanceTracker,
    RAGManager,
)


class TestConversationLogger:
    """Test ConversationLogger functionality"""

    @pytest.fixture
    async def logger(self):
        """Create a temporary conversation logger"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_conversations.db"
            logger = ConversationLogger(str(db_path))
            await logger.initialize()
            yield logger

    @pytest.mark.asyncio
    async def test_log_conversation(self, logger):
        """Test logging a conversation"""
        conv_id = await logger.log_conversation(
            session_id="test_session_1",
            user_message="Hello, how are you?",
            agent_response="I'm doing great! How can I help you?",
            response_time_ms=150.5,
            room_name="test_room",
            success=True,
        )

        assert conv_id is not None
        assert isinstance(conv_id, int)

    @pytest.mark.asyncio
    async def test_get_recent_conversations(self, logger):
        """Test retrieving recent conversations"""
        # Log multiple conversations
        for i in range(5):
            await logger.log_conversation(
                session_id="test_session",
                user_message=f"Message {i}",
                agent_response=f"Response {i}",
                response_time_ms=100.0 + i,
            )

        # Retrieve conversations
        conversations = await logger.get_recent_conversations(limit=3)

        assert len(conversations) == 3
        assert conversations[0]["user_message"] == "Message 4"  # Most recent first

    @pytest.mark.asyncio
    async def test_performance_stats(self, logger):
        """Test performance statistics"""
        # Log successful and failed conversations
        await logger.log_conversation(
            session_id="test",
            user_message="Test 1",
            agent_response="Response 1",
            response_time_ms=100.0,
            success=True,
        )
        await logger.log_conversation(
            session_id="test",
            user_message="Test 2",
            agent_response="",
            response_time_ms=50.0,
            success=False,
            error_message="Test error",
        )

        stats = await logger.get_performance_stats(days=1)

        assert stats["total_conversations"] == 2
        assert stats["successful_conversations"] == 1
        assert stats["failed_conversations"] == 1

    @pytest.mark.asyncio
    async def test_log_metric(self, logger):
        """Test logging metrics"""
        await logger.log_metric(
            session_id="test",
            metric_name="latency",
            metric_value=123.45,
            metadata={"unit": "ms"},
        )

        # Verify metric was logged (implicit - no exception thrown)


class TestKnowledgeRetriever:
    """Test KnowledgeRetriever functionality"""

    @pytest.fixture
    def retriever(self):
        """Create a temporary knowledge retriever"""
        with tempfile.TemporaryDirectory() as tmpdir:
            chroma_path = Path(tmpdir) / "test_chroma"
            retriever = KnowledgeRetriever(
                persist_directory=str(chroma_path),
                collection_name="test_collection",
            )
            yield retriever

    @pytest.mark.asyncio
    async def test_add_conversation(self, retriever):
        """Test adding a conversation to knowledge base"""
        await retriever.add_conversation(
            conversation_id="conv_1",
            user_message="What's the weather?",
            agent_response="The weather is sunny.",
            metadata={"session_id": "test", "timestamp": "2024-01-01"},
        )

        stats = await retriever.get_statistics()
        assert stats["total_entries"] == 1

    @pytest.mark.asyncio
    async def test_retrieve_relevant_context(self, retriever):
        """Test retrieving relevant context"""
        # Add multiple conversations
        await retriever.add_conversation(
            "conv_1",
            "What's the weather like?",
            "It's sunny and warm.",
            metadata={"topic": "weather"},
        )
        await retriever.add_conversation(
            "conv_2",
            "Tell me a joke",
            "Why did the chicken cross the road?",
            metadata={"topic": "humor"},
        )
        await retriever.add_conversation(
            "conv_3",
            "Is it raining?",
            "No, it's clear skies.",
            metadata={"topic": "weather"},
        )

        # Query for weather-related conversations
        contexts = await retriever.retrieve_relevant_context(
            query="How's the weather today?", n_results=2
        )

        assert len(contexts) <= 2
        # Should retrieve weather-related conversations
        assert any("weather" in ctx["document"].lower() for ctx in contexts)

    @pytest.mark.asyncio
    async def test_add_pattern(self, retriever):
        """Test adding a learned pattern"""
        await retriever.add_pattern(
            pattern_id="pattern_1",
            pattern_type="user_preference",
            description="User prefers concise answers",
            metadata={"frequency": "high"},
        )

        stats = await retriever.get_statistics()
        assert stats["total_entries"] == 1

    @pytest.mark.asyncio
    async def test_get_statistics(self, retriever):
        """Test getting knowledge base statistics"""
        stats = await retriever.get_statistics()

        assert "total_entries" in stats
        assert "collection_name" in stats
        assert "embedding_model" in stats


class TestPerformanceTracker:
    """Test PerformanceTracker functionality"""

    @pytest.fixture
    def tracker(self):
        """Create a performance tracker"""
        return PerformanceTracker()

    def test_record_metric(self, tracker):
        """Test recording a metric"""
        tracker.record_metric(
            session_id="test",
            metric_name="response_time",
            metric_value=150.5,
        )

        assert "test" in tracker.session_metrics
        assert len(tracker.session_metrics["test"]) == 1

    def test_analyze_response_times(self, tracker):
        """Test analyzing response times"""
        conversations = [
            {"response_time_ms": 100.0},
            {"response_time_ms": 200.0},
            {"response_time_ms": 300.0},
            {"response_time_ms": 150.0},
        ]

        analysis = tracker.analyze_response_times(conversations)

        assert analysis["status"] == "analyzed"
        assert analysis["total_conversations"] == 4
        assert analysis["avg_response_time_ms"] == 187.5
        assert analysis["min_response_time_ms"] == 100.0
        assert analysis["max_response_time_ms"] == 300.0

    def test_analyze_error_patterns(self, tracker):
        """Test analyzing error patterns"""
        conversations = [
            {"success": True},
            {"success": False, "error_message": "Connection timeout"},
            {"success": True},
            {"success": False, "error_message": "Connection timeout"},
            {"success": False, "error_message": "Invalid input"},
        ]

        analysis = tracker.analyze_error_patterns(conversations)

        assert analysis["status"] == "analyzed"
        assert analysis["total_conversations"] == 5
        assert analysis["total_errors"] == 3
        assert analysis["error_rate"] == 60.0

    def test_generate_improvement_report(self, tracker):
        """Test generating improvement report"""
        conversations = [
            {
                "response_time_ms": 100.0,
                "success": True,
                "user_message": "Hello",
                "agent_response": "Hi there!",
            },
            {
                "response_time_ms": 6000.0,  # Slow response
                "success": True,
                "user_message": "How are you?",
                "agent_response": "I'm doing well!",
            },
        ]

        report = tracker.generate_improvement_report(conversations)

        assert "timestamp" in report
        assert "analyses" in report
        assert "suggestions" in report
        assert "summary" in report


class TestRAGManager:
    """Test RAGManager integration"""

    @pytest.fixture
    async def rag_manager(self):
        """Create a temporary RAG manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_conversations.db"
            chroma_path = Path(tmpdir) / "test_chroma"

            manager = RAGManager(
                enable_rag=True,
                db_path=str(db_path),
                chroma_path=str(chroma_path),
                auto_improve=False,  # Disable auto-improve for testing
            )
            await manager.initialize()
            yield manager

    @pytest.mark.asyncio
    async def test_log_conversation(self, rag_manager):
        """Test logging a conversation through RAG manager"""
        conv_id = await rag_manager.log_conversation(
            session_id="test_session",
            user_message="What's 2+2?",
            agent_response="2+2 equals 4",
            response_time_ms=100.0,
            success=True,
        )

        assert conv_id is not None

    @pytest.mark.asyncio
    async def test_get_relevant_context(self, rag_manager):
        """Test retrieving relevant context"""
        # Log some conversations
        await rag_manager.log_conversation(
            "session1",
            "What's the capital of France?",
            "The capital of France is Paris.",
            100.0,
        )
        await rag_manager.log_conversation(
            "session1", "Tell me about Paris", "Paris is a beautiful city.", 100.0
        )

        # Retrieve context
        contexts = await rag_manager.get_relevant_context(
            query="Tell me about French cities", n_results=2
        )

        assert len(contexts) <= 2

    @pytest.mark.asyncio
    async def test_generate_performance_report(self, rag_manager):
        """Test generating performance report"""
        # Log multiple conversations
        for i in range(10):
            await rag_manager.log_conversation(
                f"session_{i}",
                f"Question {i}",
                f"Answer {i}",
                100.0 + i * 10,
                success=i % 5 != 0,  # Every 5th conversation fails
            )

        report = await rag_manager.generate_performance_report(days=1)

        assert "analyses" in report
        assert "suggestions" in report
        assert "summary" in report

    @pytest.mark.asyncio
    async def test_add_pattern(self, rag_manager):
        """Test adding a learned pattern"""
        await rag_manager.add_pattern(
            pattern_type="user_preference",
            description="User prefers detailed technical explanations",
        )

        # Verify pattern was added (implicit - no exception)

    @pytest.mark.asyncio
    async def test_get_system_status(self, rag_manager):
        """Test getting system status"""
        status = await rag_manager.get_system_status()

        assert status["enabled"] is True
        assert status["initialized"] is True
        assert "knowledge_base" in status

    @pytest.mark.asyncio
    async def test_disabled_rag(self):
        """Test RAG manager with RAG disabled"""
        manager = RAGManager(enable_rag=False)

        # These should all return None/empty when disabled
        conv_id = await manager.log_conversation(
            "test", "Hello", "Hi", 100.0
        )
        assert conv_id is None

        contexts = await manager.get_relevant_context("test query")
        assert contexts == []

        report = await manager.generate_performance_report()
        assert report["status"] == "disabled"
