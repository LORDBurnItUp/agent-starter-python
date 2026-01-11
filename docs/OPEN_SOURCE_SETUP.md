# Open Source Development Setup

This guide shows you how to work on this LiveKit Agents project using **100% free and open-source tools** (except for the AI model APIs).

## 🎯 Goal: Make Voice AI Accessible to Everyone

You can build production-ready voice AI agents using only free tools:

- ✅ **LiveKit Agents** - Open source (MIT license)
- ✅ **Supabase** - Free tier available
- ✅ **VS Code + Cline** - Free and open source
- ✅ **Cursor** - Free tier available
- ✅ **Continue.dev** - Open source
- ✅ **uv** - Open source Python package manager
- ⚠️ **AI Model APIs** - Require API keys (OpenAI, Anthropic, etc.)

## Option 1: VS Code + Cline (Recommended for Open Source)

**Cline** (formerly Claude Dev) is a free, open-source VS Code extension that works with Claude API.

### Installation

1. **Install VS Code**
   ```bash
   # Ubuntu/Debian
   sudo snap install code --classic

   # macOS
   brew install --cask visual-studio-code

   # Or download from https://code.visualstudio.com
   ```

2. **Install Python Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Python" by Microsoft
   - Click Install

3. **Install Ruff Extension**
   - Search for "Ruff" by Astral Software
   - Click Install

4. **Install Cline Extension**
   - Search for "Cline" (formerly Claude Dev)
   - Click Install
   - OR install from: https://github.com/cline/cline

5. **Configure Cline**
   - Click the Cline icon in sidebar
   - Add your Anthropic API key
   - Key available at: https://console.anthropic.com

### Using This Project

```bash
# Clone the repository
git clone <your-repo-url>
cd agent-starter-python

# Open in VS Code
code .

# The .vscode folder has pre-configured settings!
# Tasks available via Terminal → Run Task:
# - Install Dependencies
# - Download Models
# - Run Agent (Console)
# - Run Agent (Dev)
# - Run Tests
# - Format Code
# - Lint Code
```

## Option 2: Continue.dev (Fully Open Source)

**Continue** is a 100% open-source coding assistant that works with multiple AI providers.

### Installation

1. **Install VS Code** (see above)

2. **Install Continue Extension**
   - Open Extensions (Ctrl+Shift+X)
   - Search for "Continue"
   - Click Install
   - OR visit: https://continue.dev

3. **Configure Continue**
   - This repo includes `.continue/config.json`
   - Add your API key for:
     - Anthropic (Claude)
     - OpenAI (GPT-4)
     - Or use Ollama locally (100% free!)

4. **Optional: Use Ollama Locally (No API Costs!)**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull models
   ollama pull codellama
   ollama pull starcoder2:7b

   # Continue will auto-detect Ollama
   ```

## Option 3: Cursor IDE

**Cursor** is a fork of VS Code with AI built-in. Has a free tier.

### Installation

1. **Download Cursor**
   - Go to https://cursor.sh
   - Download for your OS
   - Install like normal VS Code

2. **Open Project**
   ```bash
   cursor .
   ```

3. **Configure AI**
   - Cursor has built-in Claude/GPT-4 support
   - Free tier: 50 premium requests/month
   - Unlimited basic requests
   - Or use your own API key

4. **Use .cursorrules**
   - This project includes `.cursorrules`
   - Cursor automatically uses these rules
   - Optimized for LiveKit Agents development

## Option 4: Claude Code CLI (If You Have Access)

If you have Claude Code, there's a `.claude/` directory with pre-configured settings.

```bash
# Just run Claude Code in this directory
claude

# All settings are pre-configured!
```

## Setting Up the Project

### 1. Install uv (Python Package Manager)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Set Up Environment

```bash
# Copy example env file
cp .env.example .env.local

# Add your LiveKit credentials
# Get free trial at https://cloud.livekit.io
```

Required variables:
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### 4. Optional: Set Up Supabase

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for details.

Supabase is **100% optional** but great for:
- Storing conversation history
- User preferences
- Agent metrics
- Free tier: 500 MB database

### 5. Download Models

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD
- LiveKit Turn Detector

### 6. Run the Agent

```bash
# Test in your terminal
uv run python src/agent.py console

# Run for frontend/telephony
uv run python src/agent.py dev
```

## Free Resources Checklist

- [ ] **LiveKit Cloud** - Free trial at https://cloud.livekit.io
- [ ] **Supabase** - Free tier at https://supabase.com
- [ ] **Anthropic API** - $5 free credit at https://console.anthropic.com
- [ ] **OpenAI API** - $5 free credit at https://platform.openai.com

## IDE Comparison

| Feature | VS Code + Cline | Continue.dev | Cursor | Claude Code |
|---------|----------------|--------------|--------|-------------|
| **Cost** | Free | Free | Free tier | Paid |
| **Open Source** | Yes | Yes | No | No |
| **AI Provider** | Anthropic | Multiple | Built-in | Built-in |
| **Local Models** | No | Yes (Ollama) | No | No |
| **Setup** | Easy | Easy | Easiest | Easy |
| **Best For** | Claude users | Open source fans | Beginners | Pro users |

## Development Workflow

### With Any IDE

1. **Write tests first** (TDD approach)
   ```bash
   # Create test
   code tests/test_my_feature.py

   # Run tests
   uv run pytest tests/test_my_feature.py
   ```

2. **Implement feature**
   ```python
   # Edit src/agent.py or other files
   ```

3. **Format and lint**
   ```bash
   uv run ruff format
   uv run ruff check --fix
   ```

4. **Test again**
   ```bash
   uv run pytest
   ```

5. **Run agent**
   ```bash
   uv run python src/agent.py console
   ```

## Tips for Success

1. **Use MCP Server** - All IDEs can use LiveKit Docs MCP
   - VS Code/Continue: Configured in `.vscode/settings.json`
   - Cursor: Configured in `.cursorrules`
   - Claude Code: Configured in `.claude/`

2. **Follow TDD** - Write tests before changing agent behavior
   - Ensures reliability
   - Catches bugs early
   - Documents expected behavior

3. **Keep Latency Low** - Voice AI is latency-sensitive
   - Use handoffs for conversation phases
   - Use tasks for specific objectives
   - Minimize context per LLM call

4. **Leverage Free Tiers**
   - LiveKit: 10,000 minutes/month free
   - Supabase: 500 MB database free
   - APIs: Free credits to start

## Getting Help

- **LiveKit Docs**: https://docs.livekit.io
- **LiveKit Discord**: https://livekit.io/discord
- **Supabase Docs**: https://supabase.com/docs
- **This Repo**: Check AGENTS.md for guidelines

## Contributing

This project is designed to be accessible. If you improve the open-source setup:

1. Fork the repo
2. Make your changes
3. Submit a PR
4. Help others build voice AI!

## Next Steps

1. Choose your IDE (VS Code + Cline recommended)
2. Follow setup steps above
3. Read [AGENTS.md](../AGENTS.md) for development guidelines
4. Optional: Set up Supabase for data persistence
5. Start building your voice AI agent!

---

**Remember**: You can build production-ready voice AI with 100% free tools. The only paid component is the AI model API, and even that has free credits to start!
