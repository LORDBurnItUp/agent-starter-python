#!/usr/bin/env python3
"""
Automated Setup Script for LiveKit Agent with RAG

This script automates the complete setup process including:
- Dependency installation
- Model downloads
- RAG system initialization
- Environment configuration
"""

import argparse
import asyncio
import logging
import platform
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutomatedSetup:
    """Automated setup for LiveKit Agent with RAG"""

    def __init__(self, auto_mode: bool = False):
        self.auto_mode = auto_mode
        self.platform = platform.system()
        self.project_root = Path(__file__).parent.parent

    def run_command(self, cmd: list[str], description: str) -> bool:
        """Run a shell command with logging"""
        logger.info(f"{description}...")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"✓ {description} completed successfully")
            if result.stdout:
                logger.debug(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ {description} failed: {e.stderr}")
            return False

    def check_uv_installed(self) -> bool:
        """Check if uv is installed"""
        try:
            subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                check=True,
            )
            logger.info("✓ uv package manager found")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("✗ uv package manager not found")
            return False

    def install_uv(self) -> bool:
        """Install uv package manager"""
        logger.info("Installing uv package manager...")

        if self.platform == "Windows":
            cmd = [
                "powershell",
                "-ExecutionPolicy",
                "ByPass",
                "-c",
                "irm https://astral.sh/uv/install.ps1 | iex",
            ]
        else:  # Linux/macOS
            cmd = ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"]

        try:
            subprocess.run(cmd, check=True)
            logger.info("✓ uv installed successfully")
            logger.info("  Please restart your terminal and run this script again")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install uv: {e}")
            return False

    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        return self.run_command(
            ["uv", "sync"], "Installing project dependencies"
        )

    def download_models(self) -> bool:
        """Download required models"""
        return self.run_command(
            ["uv", "run", "python", "src/agent.py", "download-files"],
            "Downloading required models (VAD, turn detector)",
        )

    async def initialize_rag_system(self) -> bool:
        """Initialize the RAG system"""
        logger.info("Initializing RAG system...")
        try:
            # Import RAG manager
            sys.path.insert(0, str(self.project_root / "src"))
            from rag_system import RAGManager

            # Initialize RAG system
            rag_manager = RAGManager(
                enable_rag=True,
                db_path="data/conversations.db",
                chroma_path="data/chroma_db",
            )

            await rag_manager.initialize()

            # Add initial patterns
            await rag_manager.add_pattern(
                pattern_type="system_initialization",
                description="RAG system initialized successfully during setup",
                metadata={"timestamp": "setup", "platform": self.platform},
            )

            # Get system status
            status = await rag_manager.get_system_status()
            logger.info(f"✓ RAG system initialized: {status}")

            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize RAG system: {e}")
            return False

    def check_environment(self) -> bool:
        """Check if environment variables are configured"""
        env_file = self.project_root / ".env.local"

        if not env_file.exists():
            logger.warning("✗ .env.local not found")
            logger.info("  Creating .env.local from template...")

            env_example = self.project_root / ".env.example"
            if env_example.exists():
                import shutil

                shutil.copy(env_example, env_file)
                logger.info("✓ Created .env.local from template")
                logger.warning(
                    "  Please edit .env.local with your LiveKit credentials"
                )
                logger.info("  Get credentials from: https://cloud.livekit.io/")
            return False

        logger.info("✓ .env.local found")
        return True

    def display_system_info(self):
        """Display system information"""
        logger.info("=== System Information ===")
        logger.info(f"Platform: {self.platform}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Project Root: {self.project_root}")
        logger.info("=" * 30)

    async def run_full_setup(self) -> bool:
        """Run complete automated setup"""
        self.display_system_info()

        steps = [
            ("Checking uv installation", self.check_uv_installed),
            ("Installing dependencies", self.install_dependencies),
            ("Downloading models", self.download_models),
            ("Initializing RAG system", self.initialize_rag_system),
            ("Checking environment", self.check_environment),
        ]

        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")

            if asyncio.iscoroutinefunction(step_func):
                result = await step_func()
            else:
                result = step_func()

            if not result:
                if step_name == "Checking uv installation":
                    # Try to install uv
                    if not self.auto_mode:
                        response = input(
                            "Would you like to install uv now? (y/n): "
                        )
                        if response.lower() != "y":
                            logger.error("Setup cannot continue without uv")
                            return False

                    if not self.install_uv():
                        return False

                    logger.info(
                        "Please restart your terminal and run this script again"
                    )
                    return False

                elif step_name == "Checking environment":
                    # Non-critical, continue
                    logger.warning(
                        "Setup completed but environment needs configuration"
                    )
                else:
                    logger.error(f"Setup failed at: {step_name}")
                    return False

        logger.info("\n=== Setup Complete! ===")
        logger.info("\nNext steps:")
        logger.info("1. Configure .env.local with your LiveKit credentials")
        logger.info("2. Run: uv run python src/agent.py console")
        logger.info("3. Or run: uv run python src/agent.py dev")
        logger.info("\nFor more information, see:")
        logger.info("- README.md")
        logger.info("- docs/INSTALLATION.md")
        logger.info("- docs/RAG_SYSTEM.md")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Automated setup for LiveKit Agent with RAG"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in fully automated mode (no prompts)",
    )
    parser.add_argument(
        "--platform",
        choices=["auto", "windows", "linux", "macos"],
        default="auto",
        help="Target platform (default: auto-detect)",
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip model downloads",
    )
    parser.add_argument(
        "--skip-rag",
        action="store_true",
        help="Skip RAG system initialization",
    )

    args = parser.parse_args()

    # Run setup
    setup = AutomatedSetup(auto_mode=args.auto)

    try:
        success = asyncio.run(setup.run_full_setup())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
