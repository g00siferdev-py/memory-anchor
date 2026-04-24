#!/usr/bin/env python3
"""
Buffer Management - Flush conversation buffer to database.
Called periodically (e.g., every heartbeat) to persist buffered exchanges.
"""

import sqlite3
import json
from datetime import datetime
import os

# Default paths - can be overridden via environment variables
DEFAULT_DB_PATH = os.path.expanduser("~/.memory-anchor/data/memory.db")
DEFAULT_BUFFER_PATH = os.path.expanduser("~/.memory-anchor/data/conversation_buffer.json")


def get_db_path():
    return os.environ.get("MEMORY_DB_PATH", DEFAULT_DB_PATH)


def get_buffer_path():
    return os.environ.get("BUFFER_PATH", DEFAULT_BUFFER_PATH)


def flush_buffer(buffer_path: str = None, db_path: str = None):
    """
    Flush all buffered exchanges to database.
    
    Args:
        buffer_path: Path to buffer JSON file (optional)
        db_path: Path to SQLite database (optional)
    
    Returns:
        int: Number of exchanges flushed
    """
    if buffer_path is None:
        buffer_path = get_buffer_path()
    if db_path is None:
        db_path = get_db_path()
    
    if not os.path.exists(buffer_path):
        return 0
    
    try:
        with open(buffer_path, 'r') as f:
            buffer = json.load(f)
    except:
        reset_buffer(buffer_path)
        return 0
    
    exchanges = buffer.get("since_last_heartbeat", [])
    
    if not exchanges:
        return 0
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    for exchange in exchanges:
        try:
            cursor.execute("""
                INSERT INTO raw_memories (content, source, tags, session_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                exchange.get("content", ""),
                exchange.get("source", "conversation"),
                exchange.get("tags", ""),
                exchange.get("session_id", ""),
                exchange.get("timestamp", datetime.now().isoformat())
            ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting exchange: {e}")
    
    conn.commit()
    conn.close()
    
    # Reset buffer
    reset_buffer(buffer_path)
    
    return inserted


def reset_buffer(buffer_path: str = None):
    """Reset the conversation buffer."""
    if buffer_path is None:
        buffer_path = get_buffer_path()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(buffer_path), exist_ok=True)
    
    buffer = {
        "since_last_heartbeat": [],
        "last_flush": datetime.now().isoformat(),
        "session_date": datetime.now().strftime("%Y-%m-%d")
    }
    with open(buffer_path, 'w') as f:
        json.dump(buffer, f, indent=2)


def log_exchange(user_message: str, assistant_response: str, tags: str = "",
                  buffer_path: str = None):
    """
    Log a single exchange to the buffer.
    Call this during conversation, then flush periodically.
    
    Args:
        user_message: What the user said
        assistant_response: What the assistant replied
        tags: Comma-separated tags for categorization
        buffer_path: Path to buffer file (optional)
    """
    if buffer_path is None:
        buffer_path = get_buffer_path()
    
    content = f"USER: {user_message}\nASSISTANT: {assistant_response}"
    
    exchange = {
        "content": content,
        "source": "conversation",
        "tags": tags,
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat()
    }
    
    # Load existing buffer
    if os.path.exists(buffer_path):
        try:
            with open(buffer_path, 'r') as f:
                buffer = json.load(f)
        except:
            buffer = {"since_last_heartbeat": [], "last_flush": "", "session_date": ""}
    else:
        buffer = {"since_last_heartbeat": [], "last_flush": "", "session_date": ""}
    
    # Append exchange
    buffer["since_last_heartbeat"].append(exchange)
    
    # Save buffer
    with open(buffer_path, 'w') as f:
        json.dump(buffer, f, indent=2)
    
    return True


if __name__ == "__main__":
    count = flush_buffer()
    if count > 0:
        print(f"✓ Flushed {count} exchange(s) to database")
    else:
        print("✓ No exchanges to flush")