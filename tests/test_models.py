from pathlib import Path

from vllama.config import AppPaths
from vllama.models import ModelRecord, ModelStore


def test_model_store_adds_lists_and_removes_models(tmp_path: Path) -> None:
    store = ModelStore(AppPaths(tmp_path))
    record = ModelRecord(
        name="Qwen/Qwen2.5-1.5B-Instruct",
        source="huggingface",
        path=None,
        last_used_at="2026-05-15T00:00:00Z",
    )

    store.upsert(record)

    assert store.get(record.name) == record
    assert store.list()[0].name == record.name

    assert store.remove(record.name) is True
    assert store.get(record.name) is None
    assert store.remove(record.name) is False


def test_model_store_reads_existing_json(tmp_path: Path) -> None:
    paths = AppPaths(tmp_path)
    paths.ensure()
    paths.models_file.write_text(
        '{"models":[{"name":"meta/llama","source":"huggingface","path":null,"last_used_at":"now"}]}'
    )

    store = ModelStore(paths)

    assert [model.name for model in store.list()] == ["meta/llama"]

