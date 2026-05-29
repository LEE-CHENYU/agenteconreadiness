from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from aeread_lab.models import Agent


DEFAULT_CACHE_DIR = Path(".aeread-cache") / "responses"


def cache_key(agent_name: str, system: str, user: str) -> str:
    payload = json.dumps(
        {"agent": agent_name, "system": system, "user": user},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class CachedAgent:
    """File-backed response cache for paid model calls."""

    inner: Agent
    cache_dir: Path = DEFAULT_CACHE_DIR
    enabled: bool = True

    @property
    def name(self) -> str:
        return self.inner.name

    def complete(self, system: str, user: str) -> str:
        if not self.enabled:
            return self.inner.complete(system, user)
        key = cache_key(self.inner.name, system, user)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())["response"]
        response = self.inner.complete(system, user)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "agent": self.inner.name,
                    "key": key,
                    "response": response,
                    "system": system,
                    "user": user,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return response
