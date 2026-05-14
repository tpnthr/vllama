from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from vllama.config import AppPaths


@dataclass(frozen=True)
class ModelRecord:
    name: str
    source: str = "huggingface"
    path: str | None = None
    last_used_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ModelRecord":
        return cls(
            name=str(data["name"]),
            source=str(data.get("source", "huggingface")),
            path=data.get("path") if isinstance(data.get("path"), str) else None,
            last_used_at=(
                data.get("last_used_at") if isinstance(data.get("last_used_at"), str) else None
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ModelStore:
    def __init__(self, paths: AppPaths | None = None) -> None:
        self.paths = paths or AppPaths()
        self.paths.ensure()

    def list(self) -> list[ModelRecord]:
        records = self._load()
        return sorted(records.values(), key=lambda record: record.name.lower())

    def get(self, name: str) -> ModelRecord | None:
        return self._load().get(name)

    def upsert(self, record: ModelRecord) -> None:
        records = self._load()
        records[record.name] = record
        self._save(records)

    def remove(self, name: str) -> bool:
        records = self._load()
        if name not in records:
            return False
        del records[name]
        self._save(records)
        return True

    def _load(self) -> dict[str, ModelRecord]:
        if not self.paths.models_file.exists():
            return {}
        raw = json.loads(self.paths.models_file.read_text())
        return {
            record.name: record
            for record in (
                ModelRecord.from_dict(item) for item in raw.get("models", []) if isinstance(item, dict)
            )
        }

    def _save(self, records: dict[str, ModelRecord]) -> None:
        self.paths.ensure()
        data = {"models": [record.to_dict() for record in sorted(records.values(), key=lambda r: r.name)]}
        self.paths.models_file.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

