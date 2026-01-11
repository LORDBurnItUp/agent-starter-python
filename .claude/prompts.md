# Project-Specific Prompts

## Working with LiveKit Agents

This is a LiveKit Agents project for building voice AI applications. When working on this project:

- **Use uv for all operations**: `uv run`, `uv sync`, etc.
- **Follow TDD**: Write tests before modifying core agent behavior
- **Keep latency low**: Use handoffs and tasks instead of monolithic prompts
- **Format code**: Run `uv run ruff format` and `uv run ruff check`
- **Consult docs**: Use the LiveKit Docs MCP server for up-to-date information

## Common Tasks

### Running the agent
```bash
# Download models first (first time only)
uv run python src/agent.py download-files

# Run in console mode for testing
uv run python src/agent.py console

# Run in dev mode for frontend/telephony
uv run python src/agent.py dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py
```

### Code quality
```bash
# Format code
uv run ruff format

# Check for issues
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix
```

## Agent Architecture

The main entry point is `src/agent.py`. When building complex agents:

1. Use **handoffs** for different conversation phases
2. Use **tasks** for tightly-scoped objectives
3. Minimize tools and context for each phase to reduce latency
4. Test thoroughly using the eval framework

See AGENTS.md for complete guidelines.
