# Memory Anchor

> A local episodic memory system for AI agents that bridges continuity gaps through intelligent storage and contextual retrieval.

## The Problem

AI agents are stateless. Every session starts fresh. Context windows fill up. Expensive API calls for "memory" features. The result: agents that forget, repeat themselves, and never truly learn.

## The Insight

**Memory is not retrieval. Memory is persistence.**

Traditional approaches try to be clever about *what* to store. I took the opposite approach: store everything, query what matters. The intelligence is in the retrieval, not the storage.

## Architecture

```
Conversation → Buffer → Database → Context Briefing → Agent
                    ↓___________________________|
                          (flush on heartbeat)
```

**Key Design Decisions:**

1. **SQLite over vector DB**: Local, fast, zero dependencies. No cloud calls for memory operations.

2. **Raw + Curated dual storage**: Everything goes to `raw_memories`. Important insights extracted to `memories`. This preserves signal while enabling efficient retrieval.

3. **Episodic continuity**: Agents run `startup.py` on session start to generate a context briefing from the last 24h. This bridges the gap between stateless sessions.

4. **Buffered flushing**: Conversations accumulate in a JSON buffer, flushed to DB on heartbeat. Minimizes database writes while preventing data loss.

## Technical Implementation

### Core Components

| File | Purpose |
|------|---------|
| `core.py` | Database operations, memory storage/recall |
| `buffer.py` | Conversation buffering and flushing |
| `startup.py` | Context briefing generation |

### Database Schema

```sql
-- Store everything. Query what matters.
CREATE TABLE raw_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source TEXT,
    tags TEXT,              -- for filtering
    session_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Curated insights (high-value extractions)
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'identity', 'user', 'lesson', 'goal', 'fact'
    content TEXT NOT NULL,
    importance INTEGER,     -- 1-10 scale
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Usage

```python
from memory_system import init_db, log_exchange, flush_buffer, recall_recent

# Initialize
init_db()

# During conversation
log_exchange("What's the weather?", "It's sunny and 72°")

# On heartbeat
flush_buffer()

# Next session
context = recall_recent(hours=24)
print(f"Loaded {context['count']} memories from last session")
```

## Results

- **12,468 exchanges** stored over 24 days of operation
- **Zero API costs** for memory storage/retrieval
- **<2s startup time** for context briefing generation
- **Persistent continuity** across episodic sessions

## What I Learned

**Simple storage, smart retrieval beats smart storage, simple retrieval.**

The temptation was to build filtering at write-time. That would have lost signal. By storing everything and querying with intent, the system preserves information that seemed unimportant at the time but becomes relevant later.

**Context windows are expensive. Local databases are cheap.**

Moving memory out of the context window and into SQLite cut token costs while improving continuity. The context briefing acts as a compression layer, surfacing only what's needed.

## Tech Stack

- Python 3.8+
- SQLite (local storage)
- No external API dependencies

## Author

Built by [Daniel] as a solution to the episodic memory problem in AI agents. Designed for simplicity, implemented for reliability.

## License

MIT