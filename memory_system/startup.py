#!/usr/bin/env python3
"""
Startup Routine - Generates context briefing for new sessions.
Run this on session start to bridge episodic continuity gaps.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system.core import get_startup_briefing, log_startup_run, recall_recent
from datetime import datetime

# Configuration
CONTEXT_FILE = os.path.expanduser("~/.memory-anchor/data/current_context.md")


def generate_context(briefing_path: str = None):
    """
    Generate and write the context briefing.
    
    Args:
        briefing_path: Where to write the briefing (optional)
    """
    if briefing_path is None:
        briefing_path = CONTEXT_FILE
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(briefing_path), exist_ok=True)
    
    print("[Startup] Generating context briefing...")
    
    # Get recent memories
    recent = recall_recent(hours=24, limit=50)
    briefing = get_startup_briefing(hours=24)
    
    # Write to file
    with open(briefing_path, 'w') as f:
        f.write(briefing)
        f.write("\n\n---\n\n")
        f.write(f"Last updated: {datetime.now().isoformat()}\n")
        f.write(f"Memories in last 24h: {recent['count']}\n")
    
    # Log that we ran
    log_startup_run(memories_loaded=recent['count'])
    
    print(f"[Startup] Briefing generated. {recent['count']} memories available.")
    return True


if __name__ == "__main__":
    # Always regenerate context on startup
    generate_context()
    print("[Startup] Complete. Current context ready.")