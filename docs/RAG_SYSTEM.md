# RAG-Based Self-Improvement System

This document describes the Retrieval-Augmented Generation (RAG) system that enables the LiveKit agent to learn from past interactions and continuously improve its performance.

## Overview

The RAG system provides:

- **Conversation Logging**: Tracks all user-agent interactions
- **Knowledge Retrieval**: Retrieves relevant past conversations for context
- **Performance Tracking**: Analyzes metrics and identifies improvement opportunities
- **Self-Improvement**: Automatically generates suggestions based on performance data

## Architecture

### Components

1. **ConversationLogger** (`src/rag_system/conversation_logger.py`)
   - Stores conversations in SQLite database
   - Tracks response times, success/failure rates
   - Maintains performance metrics

2. **KnowledgeRetriever** (`src/rag_system/knowledge_retriever.py`)
   - Uses ChromaDB vector database for semantic search
   - Stores conversation embeddings using sentence-transformers
   - Enables retrieval of relevant past interactions

3. **PerformanceTracker** (`src/rag_system/performance_tracker.py`)
   - Analyzes response times, error patterns, conversation patterns
   - Generates improvement suggestions
   - Compares performance over time

4. **RAGManager** (`src/rag_system/rag_manager.py`)
   - Coordinates all RAG components
   - Provides unified API for the agent
   - Handles auto-improvement reports

## Installation

The RAG system dependencies are automatically installed with:

```bash
uv sync
```

Or use the automated setup script:

```bash
uv run python scripts/setup.py --auto
```

## Configuration

### Environment Variables

Configure RAG behavior in `.env.local`:

```bash
# Enable/disable RAG system (default: true)
ENABLE_RAG=true

# Auto-generate improvement reports every N conversations (default: 100)
RAG_IMPROVEMENT_INTERVAL=100

# Database paths (optional, defaults shown)
RAG_DB_PATH=data/conversations.db
RAG_CHROMA_PATH=data/chroma_db
```

### Programmatic Configuration

```python
from rag_system import RAGManager

# Initialize with custom settings
rag_manager = RAGManager(
    enable_rag=True,                              # Enable/disable RAG
    db_path="data/conversations.db",              # SQLite database path
    chroma_path="data/chroma_db",                 # ChromaDB path
    auto_improve=True,                            # Auto-generate reports
    improvement_interval_conversations=100,       # Report every N conversations
)

await rag_manager.initialize()
```

## Usage

### Basic Usage

The RAG system is automatically integrated into the agent. When enabled, it:

1. Logs every conversation automatically
2. Tracks performance metrics in real-time
3. Generates improvement reports periodically
4. Stores embeddings for future retrieval

### Logging Conversations

Conversations are logged automatically by the agent, but you can also log manually:

```python
conversation_id = await rag_manager.log_conversation(
    session_id="session_123",
    user_message="What's the weather like?",
    agent_response="The weather is sunny and warm.",
    response_time_ms=150.5,
    room_name="weather_room",
    success=True,
    metadata={"topic": "weather"}
)
```

### Retrieving Relevant Context

Retrieve relevant past conversations to enhance responses:

```python
# Get relevant context for current query
contexts = await rag_manager.get_relevant_context(
    query="How's the weather?",
    n_results=3,
    session_id="session_123"  # Optional: filter by session
)

for ctx in contexts:
    print(f"Relevant: {ctx['document']}")
    print(f"Distance: {ctx['distance']}")
```

### Performance Reports

Generate performance analysis reports:

```python
# Generate report for last 7 days
report = await rag_manager.generate_performance_report(days=7)

print(f"Total conversations: {report['database_stats']['total_conversations']}")
print(f"Error rate: {report['analyses']['errors']['error_rate']}%")
print(f"Suggestions: {report['summary']['total_suggestions']}")

# View improvement suggestions
for suggestion in report['suggestions']:
    print(f"[{suggestion['severity']}] {suggestion['suggestion']}")
```

### Adding Learned Patterns

Store learned patterns for future reference:

```python
await rag_manager.add_pattern(
    pattern_type="user_preference",
    description="User prefers concise, technical responses",
    metadata={"confidence": "high"}
)
```

### Session Summaries

Get summary for a specific session:

```python
summary = await rag_manager.get_session_summary(session_id="session_123")

print(f"Total conversations: {summary['total_conversations']}")
print(f"Success rate: {summary['successful_conversations'] / summary['total_conversations']}")
```

## Features

### Automatic Conversation Tracking

Every user-agent interaction is automatically logged with:
- User message
- Agent response
- Response time
- Success/failure status
- Metadata (models used, room name, etc.)

### Semantic Search

The system uses sentence-transformers to create embeddings, enabling:
- Finding similar past conversations
- Context-aware retrieval
- Semantic similarity matching

### Performance Analytics

Analyzes multiple dimensions:
- **Response Times**: Average, percentiles (p50, p95, p99)
- **Error Patterns**: Error rates, common failures
- **Conversation Patterns**: Message lengths, interaction quality

### Self-Improvement Suggestions

Automatically generates actionable suggestions:
- High priority: Critical issues (e.g., >10% error rate)
- Medium priority: Performance concerns (e.g., slow responses)
- Low priority: Quality improvements (e.g., response verbosity)

### Auto-Improvement Reports

Every N conversations (default: 100), the system:
1. Analyzes recent performance
2. Generates improvement suggestions
3. Logs high-priority issues as warnings
4. Compares against historical baseline

## Data Storage

### SQLite Database

Located at `data/conversations.db` (configurable):

**Tables:**
- `conversations`: All user-agent interactions
- `performance_metrics`: Detailed metrics
- `feedback`: User feedback (future use)

**Benefits:**
- Persistent storage
- Fast queries
- No external dependencies

### ChromaDB Vector Database

Located at `data/chroma_db/` (configurable):

**Stores:**
- Conversation embeddings
- Learned patterns
- Metadata for filtering

**Benefits:**
- Semantic search
- Efficient similarity matching
- Built-in persistence

## Performance Impact

The RAG system is designed to be lightweight:

- **Embedding Generation**: ~50-100ms per conversation (background)
- **Database Writes**: ~5-10ms per conversation (async)
- **Memory Usage**: ~200MB for embedding model
- **Storage**: ~1KB per conversation in SQLite, ~4KB in ChromaDB

**Recommendations:**
- RAG operations run asynchronously (non-blocking)
- Embedding model loads once at startup
- Database writes are batched when possible

## Testing

Run RAG system tests:

```bash
# Run all RAG tests
uv run pytest tests/test_rag_system.py -v

# Run specific test
uv run pytest tests/test_rag_system.py::TestRAGManager::test_log_conversation -v

# Run with coverage
uv run pytest tests/test_rag_system.py --cov=rag_system
```

## Monitoring

### Logs

The RAG system uses Python's logging module:

```python
import logging

# Enable debug logging for RAG
logging.getLogger("rag_system").setLevel(logging.DEBUG)
```

### System Status

Check RAG system status:

```python
status = await rag_manager.get_system_status()

print(f"Enabled: {status['enabled']}")
print(f"Total conversations: {status['total_conversations_logged']}")
print(f"Knowledge base entries: {status['knowledge_base']['total_entries']}")
```

### Error Insights

Analyze error patterns:

```python
insights = await rag_manager.get_error_insights()

print(f"Total unique errors: {insights['total_unique_errors']}")

for error in insights['error_patterns']:
    print(f"Error: {error['error_message']}")
    print(f"Count: {error['count']}")
    print(f"Last seen: {error['last_occurrence']}")
```

## Advanced Usage

### Custom Embedding Models

Use a different embedding model:

```python
from rag_system import KnowledgeRetriever

retriever = KnowledgeRetriever(
    persist_directory="data/chroma_db",
    embedding_model="all-mpnet-base-v2"  # More accurate but slower
)
```

Popular models:
- `all-MiniLM-L6-v2`: Fast, good quality (default)
- `all-mpnet-base-v2`: Higher quality, slower
- `multi-qa-MiniLM-L6-cos-v1`: Optimized for Q&A

### Custom Analysis

Create custom performance analyses:

```python
from rag_system import PerformanceTracker

tracker = PerformanceTracker()

# Get recent conversations from logger
conversations = await rag_manager.logger.get_recent_conversations(limit=1000)

# Analyze specific aspects
response_analysis = tracker.analyze_response_times(conversations)
error_analysis = tracker.analyze_error_patterns(conversations)

# Compare time periods
recent = conversations[:100]
historical = conversations[100:]
comparison = tracker.compare_time_periods(recent, historical)

print(f"Improvement: {comparison['improvement']['response_time_improvement_pct']}%")
```

### Bulk Operations

Add multiple conversations efficiently:

```python
import asyncio

conversations = [
    ("user_msg_1", "agent_resp_1", 100.0),
    ("user_msg_2", "agent_resp_2", 120.0),
    # ... more conversations
]

tasks = [
    rag_manager.log_conversation(
        session_id="bulk_import",
        user_message=user_msg,
        agent_response=agent_resp,
        response_time_ms=resp_time,
    )
    for user_msg, agent_resp, resp_time in conversations
]

await asyncio.gather(*tasks)
```

## Troubleshooting

### RAG Not Logging Conversations

Check if RAG is enabled:
```python
if rag_manager.is_enabled():
    print("RAG is enabled")
else:
    print("RAG is disabled - check ENABLE_RAG environment variable")
```

### Slow Performance

1. Check embedding model size
2. Reduce `n_results` in retrieval queries
3. Disable auto-improvement temporarily
4. Use faster embedding model

### Database Locked Errors

SQLite can have lock issues with high concurrency:
```python
# Increase timeout (default: 5.0)
import aiosqlite
aiosqlite.timeout = 10.0
```

### Large Database Size

Clean up old data:
```sql
-- Connect to database
sqlite3 data/conversations.db

-- Delete conversations older than 30 days
DELETE FROM conversations WHERE timestamp < datetime('now', '-30 days');

-- Vacuum to reclaim space
VACUUM;
```

## Privacy & Security

### Data Privacy

- All data is stored locally (no cloud sync)
- No external API calls for RAG operations
- Embeddings are generated locally

### Sensitive Data

To avoid logging sensitive information:

```python
# Disable RAG for sensitive sessions
ENABLE_RAG=false

# Or filter specific content
if not is_sensitive(user_message):
    await rag_manager.log_conversation(...)
```

### Data Retention

Implement data retention policies:

```python
# Delete old conversations
async def cleanup_old_data(days=90):
    async with aiosqlite.connect("data/conversations.db") as db:
        await db.execute(
            "DELETE FROM conversations WHERE timestamp < datetime('now', '-' || ? || ' days')",
            (days,)
        )
        await db.commit()
```

## Roadmap

Future enhancements:
- [ ] Real-time dashboard for monitoring
- [ ] Automated A/B testing of improvements
- [ ] Multi-agent knowledge sharing
- [ ] Integration with external analytics platforms
- [ ] Federated learning across deployments

## Contributing

To contribute to the RAG system:

1. Follow the code structure in `src/rag_system/`
2. Add tests in `tests/test_rag_system.py`
3. Update this documentation
4. Run tests: `uv run pytest tests/test_rag_system.py`

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review test examples in `tests/test_rag_system.py`
