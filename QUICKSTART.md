# 🚀 Quick Start Guide - LiveKit Voice Agent

## ✅ What's Already Done

Your LiveKit Voice Agent is **production-ready** with these improvements:

1. **Bug Fixes Applied:**
   - ✓ Fixed potential `KeyError` in VAD access (src/agent.py:64-67)
   - ✓ Added error handling to prewarm function (src/agent.py:51-57)
   - ✓ Implemented fallback VAD loading mechanism
   - ✓ Code formatted with ruff
   - ✓ All linting checks passed

2. **Resilience Features:**
   - Agent won't crash if prewarm fails
   - Automatic VAD loading on-demand
   - Comprehensive error logging
   - Fail-safe initialization

## 🛠️ Setup Steps (When You Have Network Access)

### Step 1: Get LiveKit Credentials

Sign up at [LiveKit Cloud](https://cloud.livekit.io/) and get your credentials.

**Option A: Using LiveKit CLI (Recommended)**
```bash
lk cloud auth
lk app env -w -d .env.local
```

**Option B: Manual Setup**
```bash
cp .env.example .env.local
# Edit .env.local and add:
# LIVEKIT_URL=wss://your-project.livekit.cloud
# LIVEKIT_API_KEY=your-api-key
# LIVEKIT_API_SECRET=your-api-secret
```

### Step 2: Download Required Models

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD (Voice Activity Detection)
- LiveKit Turn Detector (multilingual)

### Step 3: Run Your Agent

**Console Mode (Test in Terminal):**
```bash
uv run python src/agent.py console
```

**Dev Mode (For Web/Telephony):**
```bash
uv run python src/agent.py dev
```

**Production Mode:**
```bash
uv run python src/agent.py start
```

## 🧪 Testing

Run the eval suite:
```bash
uv run pytest
```

Note: Tests require `LIVEKIT_API_KEY` environment variable.

## 🌐 Frontend Integration

Connect your agent to a frontend:

- **React/Next.js:** [agent-starter-react](https://github.com/livekit-examples/agent-starter-react)
- **iOS/macOS:** [agent-starter-swift](https://github.com/livekit-examples/agent-starter-swift)
- **Flutter:** [agent-starter-flutter](https://github.com/livekit-examples/agent-starter-flutter)
- **Android:** [agent-starter-android](https://github.com/livekit-examples/agent-starter-android)
- **Telephony:** [SIP Documentation](https://docs.livekit.io/agents/start/telephony/)

## 🤖 Claude CLI (Already Installed!)

Claude Code CLI v2.1.1 is installed at `/opt/node22/bin/claude`

**Available Commands:**
```bash
claude --version              # Check version
claude --help                 # Get help
claude mcp add                # Add MCP servers
```

## 📚 LiveKit Documentation

Install the LiveKit Docs MCP server for better AI assistance:

```bash
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

## 🔧 Code Quality Tools

```bash
uv run ruff format             # Format code
uv run ruff check              # Lint code
uv run pytest                  # Run tests
```

## 📝 Agent Instructions

Edit the agent's behavior in `src/agent.py`:
- Modify the `Assistant` class instructions
- Add custom tools/functions
- Adjust voice pipeline settings (STT, LLM, TTS)

## 🚢 Deployment

Ready for production! See [deployment docs](https://docs.livekit.io/agents/ops/deployment/)

The included `Dockerfile` is production-ready.

---

**Need Help?** Check the [LiveKit Agents docs](https://docs.livekit.io/agents/)
