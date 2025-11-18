from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parents[2]  # C:\AGENT LOCAL
SESSIONS_DIR = BASE_DIR / "memory" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.jsonl"


def add_message_to_session(
    session_id: str,
    role: str,
    content: str,
    meta: Dict[str, Any] | None = None,
) -> None:
    meta = meta or {}
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "role": role,
        "content": content,
        "meta": meta,
    }
    path = _session_path(session_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    path = _session_path(session_id)
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    # on ne garde que les derniers
    lines = lines[-limit:]

    out: List[Dict[str, Any]] = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
