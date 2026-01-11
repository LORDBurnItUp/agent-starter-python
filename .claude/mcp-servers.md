# MCP Servers for this Project

## LiveKit Docs MCP Server

This project uses the LiveKit Docs MCP server to access up-to-date documentation for LiveKit Agents and related APIs.

### Configuration

The server has been configured in `~/.config/claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "livekit-docs": {
      "transport": {
        "type": "http",
        "url": "https://docs.livekit.io/mcp"
      }
    }
  }
}
```

### Usage

With the MCP server installed, you can:
- Search LiveKit documentation
- Browse API references
- Get the latest information on LiveKit Agents features
- Submit documentation feedback to help improve the docs

### Why This Matters

LiveKit Agents is a fast-evolving project with frequently updated documentation. The MCP server ensures you always have access to the latest information, which is critical for:
- Understanding new features
- Following best practices
- Using the correct APIs
- Building reliable voice AI agents

### Manual Installation (if needed)

If you need to reinstall or configure this on another system, run:

```bash
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

Or manually create/edit `~/.config/claude/mcp_config.json` with the configuration shown above.
