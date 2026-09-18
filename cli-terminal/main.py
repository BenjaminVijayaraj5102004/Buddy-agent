"""
Direct Launcher for Buddy Agent CLI Terminal
"""
import sys
import os

CLI_DIR = os.path.dirname(os.path.abspath(__file__))
BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(CLI_DIR, ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)
if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)

from cli import app

if __name__ == "__main__":
    app()
