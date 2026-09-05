#!/usr/bin/env python3
"""
CrisisLens Backend - Setup & Run Script
Usage:
  python run.py setup   # Create virtualenv and install dependencies
  python run.py dev     # Run dev server
  python run.py migrate # Run DB migrations
"""
import sys
import os
import subprocess


def run(cmd, **kwargs):
    print(f">> {cmd}")
    result = subprocess.run(cmd, shell=True, **kwargs)
    if result.returncode != 0:
        sys.exit(result.returncode)


def setup():
    print("[SETUP] Setting up CrisisLens backend...\n")
    run("python -m venv venv")
    pip = "venv\\Scripts\\pip" if sys.platform == "win32" else "venv/bin/pip"
    run(f"{pip} install --upgrade pip")
    run(f"{pip} install -r requirements.txt")

    # Create .env from template if it doesn't exist
    if not os.path.exists(".env"):
        import shutil
        shutil.copy(".env.example", ".env")
        print("\n[OK] .env file created from template -- please fill in your GEMINI_API_KEY and DATABASE_URL")
    else:
        print("\n[OK] .env already exists")

    print("\n[DONE] Setup complete! Next steps:")
    print("  1. Edit .env with your GEMINI_API_KEY and DATABASE_URL")
    print("  2. Make sure PostgreSQL is running")
    print("  3. Run: python run.py dev")


def dev():
    python = "venv\\Scripts\\python" if sys.platform == "win32" else "venv/bin/python"
    run(f"{python} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


def migrate():
    python = "venv\\Scripts\\python" if sys.platform == "win32" else "venv/bin/python"
    run(f"{python} -m alembic upgrade head")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "dev"
    {"setup": setup, "dev": dev, "migrate": migrate}.get(command, dev)()
