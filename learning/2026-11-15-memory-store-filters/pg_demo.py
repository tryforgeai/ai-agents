"""Memory store on Postgres + pgvector: metadata lives in ORDINARY COLUMNS (plus an optional JSONB).

Run (needs the Postgres container):
    docker compose up -d
    python pg_demo.py              # default DSN: postgresql://mem:mem@localhost:5432/mem
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from common import DIM, build_memory, embed, load_events

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;
DROP TABLE IF EXISTS memories;
CREATE TABLE memories (
  id            bigint PRIMARY KEY,
  text          text NOT NULL,
  embedding     vector({DIM}) NOT NULL,
  -- filled by code (scope / audit)
  user_id       text NOT NULL,
  scope         text NOT NULL CHECK (scope IN ('session','user','app')),
  source        text NOT NULL,
  ingested_at   timestamptz NOT NULL,   -- clock 2
  -- filled by the extractor
  memory_type   text NOT NULL,
  entities      text[] NOT NULL DEFAULT '{{}}',
  topic         text,
  importance    int CHECK (importance BETWEEN 1 AND 10),
  event_time    timestamptz NOT NULL,   -- clock 1
  slot          text NOT NULL,
  -- lifecycle: change these without re-embedding
  valid         boolean NOT NULL DEFAULT true,
  valid_to      timestamptz,
  superseded_by bigint REFERENCES memories(id),
  meta          jsonb NOT NULL DEFAULT '{{}}'   -- for fields that are not fixed yet
);
-- vector index: "what is similar"
CREATE INDEX memories_hnsw ON memories USING hnsw (embedding vector_cosine_ops);
-- metadata indexes: "what may this user see"
CREATE INDEX memories_user        ON memories (user_id);
CREATE INDEX memories_slot_valid  ON memories (user_id, slot) WHERE valid;   -- partial index: live facts only
CREATE INDEX memories_entities    ON memories USING gin (entities);
CREATE INDEX memories_meta        ON memories USING gin (meta);
"""


def write(conn: psycopg.Connection) -> None:
    for i, ev in enumerate(load_events(), start=1):
        m = build_memory(ev, i)
        # insert first so superseded_by can reference it, then close the old window (never DELETE)
        conn.execute(
            """INSERT INTO memories (id, text, embedding, user_id, scope, source, ingested_at, memory_type,
                                     entities, topic, importance, event_time, slot, meta)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (m.id, m.text, np.array(m.vector), m.user_id, m.scope, m.source, m.ingested_at, m.memory_type,
             m.entities, m.topic, m.importance, m.event_time, m.slot, json.dumps({"chunk_index": 0})),
        )
        rows = conn.execute(
            """UPDATE memories SET valid = false, valid_to = %s, superseded_by = %s
               WHERE user_id = %s AND slot = %s AND valid AND id <> %s RETURNING id""",
            (m.event_time, m.id, m.user_id, m.slot, m.id),
        ).fetchall()
        for (old_id,) in rows:
            print(f"  supersede #{old_id} -> #{m.id}  ({m.slot})")
    conn.commit()
    print(f"  wrote {conn.execute('SELECT count(*) FROM memories').fetchone()[0]} memories")


def show(title: str, rows) -> None:
    print(f"\n{title}")
    for r in rows:
        mid, dist, user, scope, text, valid, sup = r
        flag = "" if valid else f"  [superseded by #{sup}]"
        print(f"  #{mid:<2} {1 - dist:5.2f}  {user:<6} {scope:<7} {text[:70]}{flag}")


COLS = "id, embedding <=> %(q)s AS dist, user_id, scope, text, valid, superseded_by"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", default="postgresql://mem:mem@localhost:5432/mem")
    dsn = ap.parse_args().dsn

    with psycopg.connect(dsn, autocommit=False) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        register_vector(conn)

        print("1) schema + write path")
        conn.execute(SCHEMA)
        write(conn)

        # pgvector >= 0.8: keep scanning the HNSW index until enough rows pass the WHERE clause
        try:
            conn.execute("SET hnsw.iterative_scan = relaxed_order")
        except psycopg.Error:
            conn.rollback()
            print("  (pgvector < 0.8: no iterative scan; strict filters may return fewer rows)")

        q = {"q": np.array(embed("Where should supplier samples be shipped?"))}

        show("2) NO filter  <- old address and Dev's private note leak in",
             conn.execute(f"SELECT {COLS} FROM memories ORDER BY dist LIMIT 4", q).fetchall())

        show("3) recall filter for meera (mine + app, valid only, no session scratch)",
             conn.execute(f"""SELECT {COLS} FROM memories
                              WHERE valid AND (user_id = 'meera' OR scope = 'app') AND scope <> 'session'
                              ORDER BY dist LIMIT 4""", q).fetchall())

        show("4) as-of 2026-12-01 for meera (two clocks)",
             conn.execute(f"""SELECT {COLS} FROM memories
                              WHERE user_id = 'meera' AND event_time <= %(t)s
                                AND (valid_to IS NULL OR valid_to > %(t)s)
                              ORDER BY dist LIMIT 2""", {**q, "t": "2026-12-01T00:00:00+00:00"}).fetchall())

        show("5) entity filter: only memories about the Diya floor lamp",
             conn.execute(f"""SELECT {COLS} FROM memories
                              WHERE valid AND entities && ARRAY['Diya floor lamp']
                              ORDER BY dist LIMIT 4""", q).fetchall())

        conn.execute("UPDATE memories SET importance = 9 WHERE id = 1")   # no re-embedding
        n = conn.execute("DELETE FROM memories WHERE user_id = 'dev' RETURNING id").rowcount
        conn.commit()
        print(f"\n6) UPDATE metadata without re-embedding; right to be forgotten: deleted {n} row(s) for dev")

        print("\n7) plan for query 3 (look for the hnsw index and the filter):")
        try:
            for (line,) in conn.execute(f"""EXPLAIN SELECT {COLS} FROM memories
                                             WHERE valid AND user_id = 'meera' ORDER BY dist LIMIT 4""", q):
                print("  ", line)
        except psycopg.Error as e:
            print("   EXPLAIN failed:", e)
        print("   note: with 8 rows Postgres will likely seq-scan; the HNSW index pays off at thousands of rows")


if __name__ == "__main__":
    main()
