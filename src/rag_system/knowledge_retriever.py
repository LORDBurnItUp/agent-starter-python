"""
Knowledge Retriever - Uses RAG to retrieve relevant past interactions
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Uses vector database (ChromaDB) to store and retrieve relevant
    conversation history and learned patterns.
    """

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        collection_name: str = "agent_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Agent conversation history and learned patterns"},
        )

        logger.info(f"Knowledge retriever initialized: {persist_directory}")

    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        return self.embedding_model.encode(text).tolist()

    async def add_conversation(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a conversation to the knowledge base.

        Args:
            conversation_id: Unique identifier for this conversation
            user_message: User's message
            agent_response: Agent's response
            metadata: Additional metadata (session_id, timestamp, success, etc.)
        """
        # Combine user message and agent response for context
        combined_text = f"User: {user_message}\nAgent: {agent_response}"

        # Create embedding
        embedding = self._create_embedding(combined_text)

        # Prepare metadata
        metadata = metadata or {}
        metadata.update(
            {
                "user_message": user_message,
                "agent_response": agent_response,
            }
        )

        # Add to collection
        self.collection.add(
            ids=[conversation_id],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[metadata],
        )

        logger.debug(f"Added conversation to knowledge base: {conversation_id}")

    async def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a learned pattern to the knowledge base.

        Args:
            pattern_id: Unique identifier for this pattern
            pattern_type: Type of pattern (e.g., "error_recovery", "user_preference")
            description: Description of the pattern
            metadata: Additional metadata
        """
        embedding = self._create_embedding(description)

        metadata = metadata or {}
        metadata.update(
            {
                "pattern_type": pattern_type,
                "description": description,
            }
        )

        self.collection.add(
            ids=[pattern_id],
            embeddings=[embedding],
            documents=[description],
            metadatas=[metadata],
        )

        logger.debug(f"Added pattern to knowledge base: {pattern_id}")

    async def retrieve_relevant_context(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from past conversations and patterns.

        Args:
            query: Query text (e.g., current user message)
            n_results: Number of results to retrieve
            filter_metadata: Optional metadata filter

        Returns:
            List of relevant conversations/patterns with metadata
        """
        if self.collection.count() == 0:
            logger.debug("No data in knowledge base yet")
            return []

        # Create query embedding
        query_embedding = self._create_embedding(query)

        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
            where=filter_metadata,
        )

        # Format results
        contexts = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                context = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                    if "distances" in results
                    else None,
                }
                contexts.append(context)

        logger.debug(f"Retrieved {len(contexts)} relevant contexts for query")
        return contexts

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        count = self.collection.count()

        return {
            "total_entries": count,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model_name,
            "persist_directory": str(self.persist_directory),
        }

    async def clear_knowledge_base(self):
        """Clear all data from the knowledge base (use with caution!)"""
        logger.warning("Clearing knowledge base")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Agent conversation history and learned patterns"},
        )

    def get_embedding_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model_name": self.embedding_model_name,
            "max_seq_length": self.embedding_model.max_seq_length,
            "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension(),
        }
