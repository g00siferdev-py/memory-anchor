-- Memory Anchor Database Schema
-- Run this to initialize a fresh database

-- Raw memories: stores every exchange without filtering
CREATE TABLE raw_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source TEXT, -- 'conversation', 'insight', 'fact', 'observation'
    tags TEXT, -- comma-separated for searching
    session_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    embedding BLOB -- reserved for future semantic search
);

-- Indexes for efficient querying
CREATE INDEX idx_raw_created ON raw_memories(created_at);
CREATE INDEX idx_raw_tags ON raw_memories(tags);
CREATE INDEX idx_raw_session ON raw_memories(session_id);

-- Curated memories: important insights extracted from raw data
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'identity', 'user', 'lesson', 'goal', 'fact'
    content TEXT NOT NULL,
    source TEXT,
    importance INTEGER DEFAULT 5, -- 1-10 scale
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME,
    access_count INTEGER DEFAULT 0
);

CREATE INDEX idx_memories_created ON memories(created_at);
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_importance ON memories(importance);

-- Session tracking for continuity
CREATE TABLE startup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL,
    run_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    memories_loaded INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success'
);

-- Conversation tracking (optional, for analytics)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_type TEXT NOT NULL,
    participant TEXT NOT NULL,
    key_moment TEXT,
    emotional_tone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily summaries for long-term patterns
CREATE TABLE daily_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_date DATE UNIQUE NOT NULL,
    total_memories INTEGER,
    key_moments TEXT,
    ongoing_projects TEXT,
    emotional_arc TEXT,
    unresolved_threads TEXT,
    raw_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);