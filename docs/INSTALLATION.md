# Installation Guide

This guide covers installation for all major platforms: Windows, macOS, and Linux.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Git
- LiveKit Cloud account (sign up at https://cloud.livekit.io/)

### Platform-Specific Installation

#### Windows

1. **Install Python**
   ```powershell
   # Using winget (Windows Package Manager)
   winget install Python.Python.3.11

   # Or download from https://www.python.org/downloads/
   ```

2. **Install uv (Package Manager)**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Clone and Setup Project**
   ```powershell
   git clone <your-repo-url>
   cd agent-starter-python
   uv sync
   ```

4. **Configure Environment**
   ```powershell
   # Copy environment template
   copy .env.example .env.local

   # Edit .env.local with your LiveKit credentials
   notepad .env.local
   ```

#### macOS

1. **Install Homebrew (if not installed)**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**
   ```bash
   brew install python@3.11
   ```

3. **Install uv (Package Manager)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Clone and Setup Project**
   ```bash
   git clone <your-repo-url>
   cd agent-starter-python
   uv sync
   ```

5. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env.local

   # Edit .env.local with your LiveKit credentials
   nano .env.local
   # or use your preferred editor: vim, code, etc.
   ```

#### Linux

1. **Install Python** (if not already installed)
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip

   # Fedora/RHEL
   sudo dnf install python3.11

   # Arch
   sudo pacman -S python
   ```

2. **Install uv (Package Manager)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Clone and Setup Project**
   ```bash
   git clone <your-repo-url>
   cd agent-starter-python
   uv sync
   ```

4. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env.local

   # Edit .env.local with your LiveKit credentials
   nano .env.local
   ```

## LiveKit Configuration

### Option 1: Manual Configuration

Edit `.env.local` and add:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### Option 2: Using LiveKit CLI (Recommended)

1. **Install LiveKit CLI**

   See https://docs.livekit.io/home/cli/cli-setup for installation instructions.

2. **Authenticate and Configure**
   ```bash
   lk cloud auth
   lk app env -w -d .env.local
   ```

## Download Required Models

Before first run, download required models:

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD (Voice Activity Detection)
- LiveKit Turn Detector models

## Verify Installation

Run the agent in console mode to test:

```bash
uv run python src/agent.py console
```

## Automated Setup Script

For fully automated installation with RAG capabilities, use:

```bash
# Run automated setup
uv run python scripts/setup.py --auto

# Or with specific options
uv run python scripts/setup.py --platform auto --install-models --configure-rag
```

## Docker Installation (Optional)

Build and run using Docker:

```bash
docker build -t agent-starter .
docker run -it --env-file .env.local agent-starter
```

## Troubleshooting

### Common Issues

**1. Python Version Error**
```bash
# Check your Python version
python --version  # or python3 --version

# Should be 3.9 or higher
```

**2. uv Not Found**
```bash
# Add uv to PATH (Linux/macOS)
export PATH="$HOME/.local/bin:$PATH"

# Or restart your terminal
```

**3. Permission Errors (Linux/macOS)**
```bash
# Don't use sudo with uv
# If you need to fix permissions:
sudo chown -R $USER:$USER ~/.local
```

**4. SSL Certificate Errors**
```bash
# Update certificates (Ubuntu/Debian)
sudo apt-get install ca-certificates

# macOS
# Install certificates from Python installer or:
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Platform-Specific Issues

**Windows:**
- If PowerShell execution policy errors occur: Run PowerShell as Administrator
- Path issues: Restart terminal after installing Python/uv
- Antivirus blocking: Add project directory to exclusions

**macOS:**
- If brew command not found: Follow prompts to add to PATH
- M1/M2 chip issues: uv handles architecture automatically

**Linux:**
- Missing build tools: `sudo apt install build-essential` (Ubuntu/Debian)
- Sound issues: `sudo apt install portaudio19-dev` for sounddevice

## Next Steps

1. Read [README.md](../README.md) for project overview
2. Check [AGENTS.md](../AGENTS.md) for development guidelines
3. Explore [docs/OPEN_SOURCE_SETUP.md](OPEN_SOURCE_SETUP.md) for IDE setup
4. Review [docs/RAG_SYSTEM.md](RAG_SYSTEM.md) for self-improvement features

## Getting Help

- **LiveKit Docs**: https://docs.livekit.io/
- **Issues**: https://github.com/livekit-examples/agent-starter-python/issues
- **Discord**: https://livekit.io/discord

## Updates

Keep your installation up to date:

```bash
# Update dependencies
uv sync --upgrade

# Update uv itself
uv self update
```
