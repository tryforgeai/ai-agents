"""Memory store on Qdrant: metadata lives in the PAYLOAD (a JSON object per point).

Run:
    python qdrant_demo.py            # in-process Qdrant (no Docker needed)
    python qdrant_demo.py --url http://localhost:6333   # after `docker compose up -d`
"""

from __future__ import annotations

import argparse

from qdrant_client import QdrantClient, models

from common import DIM, build_memory, embed, load_events

COL = "memories"


def connect(url: str | None) -> QdrantClient:
    return QdrantClient(url=url) if url else QdrantClient(":memory:")


def setup(client: QdrantClient) -> None:
    if client.collection_exists(COL):
        client.delete_collection(COL)
    client.create_collection(COL, vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE))
    # Index every field you filter on. Without an index, filtering scans payloads one by one.
    for name, kind in [
        ("user_id", models.PayloadSchemaType.KEYWORD),
        ("scope", models.PayloadSchemaType.KEYWORD),
        ("slot", models.PayloadSchemaType.KEYWORD),
        ("entities", models.PayloadSchemaType.KEYWORD),   # array: indexed per element
        ("valid", models.PayloadSchemaType.BOOL),
        ("event_time", models.PayloadSchemaType.DATETIME),
        ("valid_to", models.PayloadSchemaType.DATETIME),
    ]:
        client.create_payload_index(COL, name, kind)


def write(client: QdrantClient) -> None:
    """WRITE PATH: build metadata, reconcile against the same slot, supersede (never delete)."""
    for i, ev in enumerate(load_events(), start=1):
        m = build_memory(ev, i)
        old = client.scroll(
            COL,
            scroll_filter=models.Filter(must=[
                models.FieldCondition(key="user_id", match=models.MatchValue(value=m.user_id)),
                models.FieldCondition(key="slot", match=models.MatchValue(value=m.slot)),
                models.FieldCondition(key="valid", match=models.MatchValue(value=True)),
            ]),
            limit=10,
        )[0]
        for p in old:  # invalidate, keep the history: close the validity window
            client.set_payload(COL, payload={"valid": False, "valid_to": m.event_time, "superseded_by": m.id},
                               points=[p.id])
            print(f"  supersede #{p.id} -> #{m.id}  ({m.slot})")
        client.upsert(COL, points=[models.PointStruct(id=m.id, vector=m.vector, payload=m.payload())])
    print(f"  wrote {client.count(COL).count} memories")


def show(title: str, hits) -> None:
    print(f"\n{title}")
    for h in hits:
        p = h.payload
        flag = "" if p["valid"] else f"  [superseded by #{p['superseded_by']}]"
        print(f"  #{h.id:<2} {h.score:5.2f}  {p['user_id']:<6} {p['scope']:<7} {p['text'][:70]}{flag}")


def recall_filter(user_id: str) -> models.Filter:
    """READ PATH filter: my drawer + the shared drawer, only valid facts, never other sessions' scratch."""
    return models.Filter(
        must=[models.FieldCondition(key="valid", match=models.MatchValue(value=True))],
        should=[  # at least one: mine, or shared by the app
            models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
            models.FieldCondition(key="scope", match=models.MatchValue(value="app")),
        ],
        must_not=[models.FieldCondition(key="scope", match=models.MatchValue(value="session"))],
    )


def as_of_filter(user_id: str, t: str) -> models.Filter:
    """Time travel: what did Meera's facts say AS OF time t? (valid at t, regardless of today's state)"""
    return models.Filter(
        must=[
            models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
            models.FieldCondition(key="event_time", range=models.DatetimeRange(lte=t)),
            models.Filter(should=[
                models.IsNullCondition(is_null=models.PayloadField(key="valid_to")),
                models.FieldCondition(key="valid_to", range=models.DatetimeRange(gt=t)),
            ]),
        ]
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None)
    client = connect(ap.parse_args().url)

    print("1) setup + write path")
    setup(client)
    write(client)

    q = "Where should supplier samples be shipped?"
    qv = embed(q)

    show(f"2) NO filter: '{q}'  <- old address and Dev's private note leak in",
         client.query_points(COL, query=qv, limit=4).points)

    show("3) recall filter for meera (mine + app, valid only, no session scratch)",
         client.query_points(COL, query=qv, query_filter=recall_filter("meera"), limit=4).points)

    show("4) as-of 2026-12-01 for meera (two clocks: what held then)",
         client.query_points(COL, query=qv, query_filter=as_of_filter("meera", "2026-12-01T00:00:00+00:00"),
                             limit=2).points)

    # 5) metadata changes do NOT need re-embedding: promote Dev's note to shared, then forget Dev entirely
    client.set_payload(COL, payload={"importance": 9}, points=[1])
    print("\n5) set_payload on #1 (importance 8 -> 9): vector untouched")

    client.delete(COL, points_selector=models.FilterSelector(filter=models.Filter(must=[
        models.FieldCondition(key="user_id", match=models.MatchValue(value="dev"))])))
    print(f"6) right to be forgotten: deleted every point with user_id=dev -> {client.count(COL).count} left")
    print("   (a real system must also sweep summaries, caches and derived facts, and keep a tombstone of the event)")


if __name__ == "__main__":
    main()
