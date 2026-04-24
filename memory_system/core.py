#!/usr/bin/env python3
"""
Memory Anchor - Core functions for storing and recalling memories.
Built for episodic continuity: store everything, query what matters.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Default database path - can be overridden
DEFAULT_DB_PATH = os.path.expanduser("~/.memory-anchor/data/memory.db")


def get_db_path():
    """Get the database path from environment or use default."""
    return os.environ.get("MEMORY_DB_PATH", DEFAULT_DB_PATH)


def init_db(db_path: str = None):
    """
    Initialize the database with the full schema.
    Run this once to set up a fresh database.
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), "..", "examples", "schema.sql")
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()
    return True


def store_memory(content: str, source: str = "conversation", tags: str = "", 
                 session_id: str = "", db_path: str = None):
    """
    Store any memory immediately. No curation. Everything matters.
    
    Args:
        content: The memory to store (can be any text)
        source: Where it came from ('conversation', 'insight', 'fact', 'observation')
        tags: Comma-separated tags for searching later
        session_id: Optional session identifier
        db_path: Path to SQLite database (optional)
    """
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO raw_memories (content, source, tags, session_id)
        VALUES (?, ?, ?, ?)
    """, (content, source, tags, session_id))
    
    conn.commit()
    conn.close()
    return True


def store_curated(category: str, content: str, importance: int = 5, 
                  source: str = "conversation", db_path: str = None):
    """
    Store a curated memory (for important, high-value insights)
    
    Args:
        category: 'identity', 'user', 'lesson', 'goal', 'fact'
        content: The memory content
        importance: 1-10 scale
        source: Where it came from
        db_path: Path to SQLite database (optional)
    """
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO memories (category, content, source, importance)
        VALUES (?, ?, ?, ?)
    """, (category, content, source, importance))
    
    conn.commit()
    conn.close()
    return True


def recall_recent(hours: int = 24, limit: int = 50, db_path: str = None) -> Dict:
    """
    Get recent memories from the last N hours.
    Used for startup briefing.
    
    Args:
        hours: How far back to look
        limit: Maximum number of memories to return
        db_path: Path to SQLite database (optional)
    
    Returns:
        Dict with 'raw', 'curated', and 'count' keys
    """
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    
    # Get from raw_memories
    cursor.execute("""
        SELECT content, source, tags, created_at 
        FROM raw_memories 
        WHERE created_at > ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (since.isoformat(), limit))
    
    raw = cursor.fetchall()
    
    # Get from curated memories
    cursor.execute("""
        SELECT category, content, source, importance, created_at
        FROM memories
        WHERE created_at > ?
        ORDER BY importance DESC, created_at DESC
        LIMIT ?
    """, (since.isoformat(), limit))
    
    curated = cursor.fetchall()
    conn.close()
    
    return {
        "raw": [{"content": r[0], "source": r[1], "tags": r[2], "time": r[3]} for r in raw],
        "curated": [{"category": c[0], "content": c[1], "source": c[2], "importance": c[3], "time": c[4]} for c in curated],
        "count": len(raw) + len(curated)
    }


def recall_by_topic(topic: str, limit: int = 10, db_path: str = None) -> List[Dict]:
    """
    Search memories by topic/tag.
    Used during conversation to fill gaps.
    """
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    search_term = f"%{topic}%"
    
    cursor.execute("""
        SELECT content, source, tags, created_at
        FROM raw_memories
        WHERE content LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (search_term, search_term, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"content": r[0], "source": r[1], "tags": r[2], "time": r[3]} for r in results]


def get_startup_briefing(hours: int = 24, db_path: str = None) -> str:
    """
    Generate a context briefing for new sessions.
    This is what gets read on startup to bridge the continuity gap.
    """
    if db_path is None:
        db_path = get_db_path()
    
    recent = recall_recent(hours=hours, db_path=db_path)
    
    briefing = f"""# Context Briefing

Generated: {datetime.now().isoformat()}
Memories available: {recent['count']}

## Recent Activity (Last {hours}h)

**Raw Exchanges:** {len(recent['raw'])}
**Curated Insights:** {len(recent['curated'])}

### Key Topics:
"""
    
    # Extract topics from tags
    topics = set()
    for mem in recent['raw']:
        if mem['tags']:
            topics.update([t.strip() for t in mem['tags'].split(',')])
    
    if topics:
        briefing += "\n".join([f"- {topic}" for topic in sorted(topics)[:10]])
    else:
        briefing += "- No specific topics tagged"
    
    # Add curated insights
    if recent['curated']:
        briefing += "\n\n## Important Insights:\n\n"
        for mem in recent['curated'][:5]:
            briefing += f"- **{mem['category']}**: {mem['content'][:100]}...\n"
    
    return briefing


def log_startup_run(memories_loaded: int = 0, status: str = "success", db_path: str = None):
    """Log that the startup routine ran."""
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    session_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO startup_log (session_date, memories_loaded, status)
        VALUES (?, ?, ?)
    """, (session_date, memories_loaded, status))
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Initialize database if run directly
    print("Initializing Memory Anchor database...")
    init_db()
    print(f"Database created at: {get_db_path()}")