"""
Agent X - Automated Setup Script
Run this once on a new device to set up the project.

Usage:
    python setup.py
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent


def run(cmd, check=True):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def check_python_version():
    print("\n[1/6] Checking Python version...")
    version = sys.version_info
    if version < (3, 9):
        print(f"  ERROR: Python 3.9+ required. You have {version.major}.{version.minor}.")
        sys.exit(1)
    print(f"  OK: Python {version.major}.{version.minor}.{version.micro}")


def install_dependencies():
    print("\n[2/6] Installing dependencies from requirements.txt...")
    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        print("  ERROR: requirements.txt not found.")
        sys.exit(1)
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
    print("  OK: Dependencies installed.")


def create_env_file():
    print("\n[3/6] Setting up .env file...")
    env_file = BASE_DIR / ".env"
    example_file = BASE_DIR / ".env.example"

    if env_file.exists():
        print("  SKIP: .env already exists.")
        return

    if example_file.exists():
        shutil.copy(example_file, env_file)
        print("  Created .env from .env.example")
    else:
        env_content = (
            "# LLM Provider: gemini or openai\n"
            "LLM_PROVIDER=gemini\n"
            "GOOGLE_API_KEY=your_google_api_key_here\n"
            "OPENAI_API_KEY=your_openai_api_key_here\n\n"
            "# Email SMTP\n"
            "SMTP_SERVER=smtp.gmail.com\n"
            "SMTP_PORT=587\n"
            "EMAIL_ADDRESS=your_email@gmail.com\n"
            "EMAIL_PASSWORD=your_app_password_here\n"
        )
        env_file.write_text(env_content)
        print("  Created default .env")

    print("  ACTION REQUIRED: Open .env and fill in your API keys and credentials.")


def create_directories():
    print("\n[4/6] Creating required directories...")
    dirs = [
        BASE_DIR / "data",
        BASE_DIR / "logs",
        BASE_DIR / "outputs" / "reports",
        BASE_DIR / "outputs" / "summaries",
        BASE_DIR / "outputs" / "organized",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # Add a .gitkeep if directory is empty
        gitkeep = d / ".gitkeep"
        if not any(d.iterdir()):
            gitkeep.touch()
    print("  OK: Directories ready.")


def init_database():
    print("\n[5/6] Initialising SQLite database...")
    try:
        # Importing db triggers init_db() and default user creation automatically
        sys.path.insert(0, str(BASE_DIR))
        import database.db  # noqa: F401
        print("  OK: Database initialised.")
    except Exception as e:
        print(f"  WARNING: Could not initialise database: {e}")


def verify_setup():
    print("\n[6/6] Verifying setup...")
    checks = {
        ".env": (BASE_DIR / ".env").exists(),
        "requirements installed": True,  # already confirmed above
        "database/users.db": (BASE_DIR / "database" / "users.db").exists(),
        "outputs/reports": (BASE_DIR / "outputs" / "reports").exists(),
    }
    all_ok = True
    for name, status in checks.items():
        icon = "OK" if status else "MISSING"
        print(f"  [{icon}] {name}")
        if not status:
            all_ok = False

    if all_ok:
        print("\nSetup complete! Start the app with:\n")
        if sys.platform == "win32":
            print("    run.bat        (double-click or run in terminal)\n")
            print("  or:\n")
        print("    streamlit run app.py\n")
    else:
        print("\nSetup finished with warnings. Fix the MISSING items above before running.")


if __name__ == "__main__":
    print("=" * 55)
    print("  Agent X - Setup Script")
    print("=" * 55)

    check_python_version()
    install_dependencies()
    create_env_file()
    create_directories()
    init_database()
    verify_setup()
