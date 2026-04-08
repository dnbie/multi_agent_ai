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
    print("\n[1/7] Checking Python version...")
    version = sys.version_info
    if version < (3, 9):
        print(f"  ERROR: Python 3.9+ required. You have {version.major}.{version.minor}.")
        print("  Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"  OK: Python {version.major}.{version.minor}.{version.micro}")


def check_node_version():
    print("\n[2/7] Checking Node.js version...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    node_cmd = "node"
    try:
        result = subprocess.run([node_cmd, "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip().lstrip("v")
        major = int(node_version.split(".")[0])
        if major < 18:
            print(f"  ERROR: Node.js 18+ required. You have {node_version}.")
            print("  Download from: https://nodejs.org/")
            sys.exit(1)
        print(f"  OK: Node.js {node_version}")
    except FileNotFoundError:
        print("  ERROR: Node.js not found!")
        print("  Download and install from: https://nodejs.org/")
        print("  (Required for the React frontend)")
        sys.exit(1)

    try:
        result = subprocess.run([npm_cmd, "--version"], capture_output=True, text=True, check=True)
        print(f"  OK: npm {result.stdout.strip()}")
    except FileNotFoundError:
        print("  ERROR: npm not found! It should come with Node.js.")
        sys.exit(1)


def install_dependencies():
    print("\n[3/7] Installing Python dependencies from requirements.txt...")
    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        print("  ERROR: requirements.txt not found.")
        sys.exit(1)
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
    print("  OK: Dependencies installed.")


def create_env_file():
    print("\n[4/7] Setting up .env file...")
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
            "# ============== Agent X Environment Variables ==============\n\n"
            "# JWT Secret Key (change this to a random string)\n"
            "SECRET_KEY=agentx-secret-key-change-me\n\n"
            "# LLM Provider: gemini or openai\n"
            "LLM_PROVIDER=gemini\n"
            "GOOGLE_API_KEY=your_google_api_key_here\n"
            "OPENAI_API_KEY=your_openai_api_key_here\n\n"
            "# Google OAuth\n"
            "GOOGLE_CLIENT_ID=your_google_client_id_here\n\n"
            "# Email SMTP\n"
            "SMTP_SERVER=smtp.gmail.com\n"
            "SMTP_PORT=587\n"
            "EMAIL_ADDRESS=your_email@gmail.com\n"
            "EMAIL_PASSWORD=your_app_password_here\n\n"
            "# Weather API (OpenWeatherMap)\n"
            "WEATHER_API_KEY=your_weather_api_key_here\n\n"
            "# News API\n"
            "NEWS_API_KEY=your_news_api_key_here\n\n"
            "# Flight API (Aviation Stack)\n"
            "AVIATION_STACK_API_KEY=your_aviation_api_key_here\n\n"
            "# Razorpay Payment (optional)\n"
            "RAZORPAY_KEY_ID=your_razorpay_key_id\n"
            "RAZORPAY_KEY_SECRET=your_razorpay_key_secret\n"
        )
        env_file.write_text(env_content)
        print("  Created default .env")

    print("  ACTION REQUIRED: Open .env and fill in your API keys and credentials.")


def create_directories():
    print("\n[5/7] Creating required directories...")
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
    print("\n[5/7] Initialising SQLite database...")
    try:
        sys.path.insert(0, str(BASE_DIR))
        import database.db  # noqa: F401
        print("  OK: Database initialised.")
    except Exception as e:
        print(f"  WARNING: Could not initialise database: {e}")


def install_frontend():
    print("\n[6/7] Installing React frontend dependencies...")
    frontend_dir = BASE_DIR / "frontend"
    if not frontend_dir.exists():
        print("  ERROR: frontend/ directory not found.")
        return
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("  SKIP: node_modules already exists.")
        return
    # Check if npm is available
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run([npm_cmd, "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  ERROR: npm not found. Install Node.js 18+ from https://nodejs.org")
        return
    print("  Installing npm packages (this may take a minute)...")
    subprocess.run([npm_cmd, "install"], cwd=str(frontend_dir), check=True)
    print("  OK: Frontend dependencies installed.")


def verify_setup():
    print("\n[7/7] Verifying setup...")
    checks = {
        ".env": (BASE_DIR / ".env").exists(),
        "requirements installed": True,
        "database/users.db": (BASE_DIR / "database" / "users.db").exists(),
        "outputs/reports": (BASE_DIR / "outputs" / "reports").exists(),
        "frontend/node_modules": (BASE_DIR / "frontend" / "node_modules").exists(),
    }
    all_ok = True
    for name, status in checks.items():
        icon = "OK" if status else "MISSING"
        print(f"  [{icon}] {name}")
        if not status:
            all_ok = False

    if all_ok:
        print("\nSetup complete! Start the app:\n")
        if sys.platform == "win32":
            print("    Double-click  run_dev.bat")
            print("    (starts both backend + frontend)\n")
        else:
            print("    Terminal 1:  python app.py")
            print("    Terminal 2:  cd frontend && npm start\n")
    else:
        print("\nSetup finished with warnings. Fix the MISSING items above before running.")


if __name__ == "__main__":
    print("=" * 55)
    print("  Agent X - Setup Script")
    print("=" * 55)

    check_python_version()
    check_node_version()
    install_dependencies()
    create_env_file()
    create_directories()
    init_database()
    install_frontend()
    verify_setup()
