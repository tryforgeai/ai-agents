import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    from fineprint.store import seed
    db = tmp_path / "fineprint.db"
    monkeypatch.setenv("FINEPRINT_DB", str(db))
    monkeypatch.setenv("FINEPRINT_TODAY", "2026-10-18")
    seed(db)
    return db
