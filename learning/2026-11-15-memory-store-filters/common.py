"""Shared pieces: a toy embedding, the sample events, and the WRITE PATH that fills metadata.

The point of this lab is *where metadata comes from* and *how stores keep it*, not embedding quality.
So `embed()` is a deterministic hashed character-trigram vector: no API key, no model download.
Swap it for a real embedding model (OpenAI, Voyage, sentence-transformers) when you want real recall.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DIM = 256
DATA = Path(__file__).parent / "data" / "events.jsonl"


# --------------------------------------------------------------------------- embedding (toy)
def embed(text: str) -> list[float]:
    """Hashed character trigrams, L2-normalised. Similar wording -> similar vector."""
    v = [0.0] * DIM
    t = f"  {re.sub(r'[^a-z0-9 ]', ' ', text.lower())}  "
    for i in range(len(t) - 2):
        h = int(hashlib.md5(t[i : i + 3].encode()).hexdigest(), 16)
        v[h % DIM] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


# --------------------------------------------------------------------------- the memory record
@dataclass
class Memory:
    id: int
    text: str
    # --- filled by CODE from the session context (never by the LLM): scope, audit
    user_id: str
    scope: str                 # "session" | "user" | "app"  (ADK-style drawers)
    source: str                # provenance: session#turn
    ingested_at: str           # clock 2: when the system learned it
    # --- filled by the LLM extractor (structured output); simulated by the data file here
    memory_type: str           # "episodic" | "semantic" | "procedural"
    entities: list[str]
    topic: str
    importance: int            # 1-10, scored once at write time (Smallville)
    event_time: str            # clock 1: when it held in the world
    slot: str                  # what fact this is about, used to reconcile ("supplier_sample_address")
    # --- lifecycle, changed later without re-embedding
    valid: bool = True
    valid_to: str | None = None
    superseded_by: int | None = None
    vector: list[float] = field(default_factory=list, repr=False)

    def payload(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k not in ("id", "vector")}
        return d


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_events() -> list[dict]:
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


# --------------------------------------------------------------------------- WRITE PATH
def build_memory(ev: dict, next_id: int) -> Memory:
    """Turn one raw event into a Memory: code fields + extracted fields.

    In production, `ev["extracted"]` is the LLM's structured output for this turn
    (atomic fact with pronouns resolved, entities, topic, importance, event_time, slot).
    Everything about WHO and WHERE comes from the session context `ev["ctx"]`.
    """
    ctx, ex = ev["ctx"], ev["extracted"]
    m = Memory(
        id=next_id,
        text=ex["text"],
        user_id=ctx["user_id"],
        scope=ctx.get("scope", "user"),
        source=f'{ctx["session_id"]}#turn_{ctx["turn"]}',
        ingested_at=ctx.get("ingested_at") or now_iso(),
        memory_type=ex["memory_type"],
        entities=ex["entities"],
        topic=ex["topic"],
        importance=int(ex["importance"]),
        event_time=ex.get("event_time") or ctx.get("ingested_at") or now_iso(),
        slot=ex["slot"],
    )
    m.vector = embed(m.text)
    return m


def chunk_document(doc_text: str, parent_meta: dict, size: int = 200) -> list[tuple[str, dict]]:
    """Chunking that PROPAGATES metadata: every chunk carries the parent's filter fields.

    A chunk is retrieved on its own, so it must say on its own whose it is and when it held.
    """
    words, out = doc_text.split(), []
    for i in range(0, len(words), size):
        piece = " ".join(words[i : i + size])
        meta = {**parent_meta, "chunk_index": i // size}      # inherit everything, add position
        out.append((piece, meta))
    return out
