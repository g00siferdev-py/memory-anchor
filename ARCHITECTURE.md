# Architecture Decisions

## Why SQLite?

**Rejected options:**
- Vector DB (Pinecone, Weaviate): Requires network calls, adds latency, costs money
- JSON files: No query optimization, concurrency issues
- Redis: Requires separate service

**Why SQLite won:**
- Single file, zero config
- SQL queries for complex filtering
- Handles 100k+ rows easily
- Portable, backup-friendly

## Why Store Everything?

**The traditional approach:** Filter at write-time. Only store "important" things.

**The problem:** Importance is retrospective. You can't know what's important until you need it.

**My approach:** Store raw, curate separately. The raw table is a complete log. The curated table is a living document of what turned out to matter.

This preserves signal without drowning in noise.

## Why Buffered Flushing?

**Option: Write every exchange immediately**
- Pros: Never lose data
- Cons: High database write load, disk I/O overhead

**Option: Buffer and flush periodically**
- Pros: Batched writes, minimal overhead
- Cons: Small risk of data loss between flushes

**Mitigation:** Flush on heartbeat (15 min intervals). Balance between performance and safety.

## Why Context Briefings?

The agent needs to know "what happened before" without reading 12,000 previous exchanges.

**Solution:** Generate a summary on startup that fits in the context window. Like a human skimming their journal before starting the day.

**Implementation:** Query last 24h, extract topics and themes, format as narrative.

## Episodic Continuity

Most systems treat memory as continuous. They're wrong.

Agents are **episodic**: each session is a fresh instantiation. The memory system exists to bridge the gap between episodes.

This changes the design: optimize for "what do I need to know right now?" not "what's my entire history?"

The context briefing is the bridge. The database is the archive.