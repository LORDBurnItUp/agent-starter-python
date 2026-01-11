# Claude Code Configuration

This directory contains Claude Code configuration files for the LiveKit Agents project.

## Files

### `settings.json`
Project-specific settings including:
- Package manager preference (uv)
- Test runner (pytest)
- Code formatter and linter (ruff)
- Project reminders and best practices

### `prompts.md`
Common tasks and commands for working with this LiveKit Agents project, including:
- How to run the agent in different modes
- Testing commands
- Code quality tools
- Architecture guidelines

### `mcp-servers.md`
Documentation about the LiveKit Docs MCP server integration, including:
- What it provides
- How it's configured
- Why it's important for this project
- Manual installation instructions

## MCP Server

The LiveKit Docs MCP server has been configured to provide access to the latest LiveKit documentation. This is essential because:

1. **Fast-evolving project**: LiveKit Agents is updated frequently
2. **Latest information**: Always get current API docs and best practices
3. **Better assistance**: AI coding assistants can reference up-to-date documentation
4. **Documentation feedback**: You can submit feedback to improve the docs

## Project Guidelines

For complete project-specific guidelines, see the main `AGENTS.md` file in the repository root.

## Quick Start

Key reminders when working on this project:

```bash
# Always use uv
uv sync                           # Install dependencies
uv run python src/agent.py console  # Test agent
uv run pytest                     # Run tests
uv run ruff format               # Format code
uv run ruff check                # Lint code
```

## TDD Approach

When modifying core agent behavior (instructions, tools, workflows):
1. Write tests first for the desired behavior
2. Implement the changes
3. Iterate until tests pass
4. This ensures reliable, working agents
