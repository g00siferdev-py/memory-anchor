#!/usr/bin/env python3
"""
Basic Usage Example - Demonstrates the Memory Anchor system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_system import init_db, log_exchange, flush_buffer, recall_recent

def main():
    print("Memory Anchor - Basic Usage Example")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   ✓ Database ready")
    
    # Simulate a conversation
    print("\n2. Simulating conversation...")
    log_exchange(
        "What's the weather like today?",
        "It's sunny and 72 degrees. Perfect weather for a walk!",
        tags="weather,query"
    )
    print("   ✓ Exchange logged to buffer")
    
    log_exchange(
        "Remind me to call Mom tomorrow",
        "I'll note that down. Reminder set for tomorrow.",
        tags="reminder,family"
    )
    print("   ✓ Exchange logged to buffer")
    
    # Flush to database
    print("\n3. Flushing buffer to database...")
    count = flush_buffer()
    print(f"   ✓ Flushed {count} exchange(s) to database")
    
    # Recall recent memories
    print("\n4. Recalling recent memories...")
    recent = recall_recent(hours=24)
    print(f"   ✓ Found {recent['count']} memories")
    
    print("\n5. Memory details:")
    for i, mem in enumerate(recent['raw'][:3], 1):
        print(f"   Memory {i}:")
        print(f"      Content: {mem['content'][:60]}...")
        print(f"      Tags: {mem['tags']}")
    
    print("\n" + "=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()