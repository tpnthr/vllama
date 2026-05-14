from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    default_model: str | None = None
    vllm_executable: str = "vllm"


class AppPaths:
    def __init__(self, root: Path | str | None = None) -> None:
        env_root = os.environ.get("VLLAMA_HOME")
        self.root = Path(root or env_root or Path.home() / ".vllama").expanduser()
        self.config_file = self.root / "config.toml"
        self.models_file = self.root / "models.json"
        self.server_file = self.root / "server.json"
        self.logs_dir = self.root / "logs"
        self.venv_dir = self.root / ".venv"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def load_config(paths: AppPaths | None = None) -> AppConfig:
    paths = paths or AppPaths()
    paths.ensure()
    if not paths.config_file.exists():
        config = AppConfig()
        save_config(paths, config)
        return config

    raw = tomllib.loads(paths.config_file.read_text())
    default_model = raw.get("default_model") or None
    return AppConfig(
        host=str(raw.get("host", AppConfig.host)),
        port=int(raw.get("port", AppConfig.port)),
        default_model=default_model,
        vllm_executable=str(raw.get("vllm_executable", AppConfig.vllm_executable)),
    )


def save_config(paths: AppPaths, config: AppConfig) -> None:
    paths.ensure()
    default_model = config.default_model or ""
    content = "\n".join(
        [
            f'host = "{_escape(config.host)}"',
            f"port = {config.port}",
            f'default_model = "{_escape(default_model)}"',
            f'vllm_executable = "{_escape(config.vllm_executable)}"',
            "",
        ]
    )
    paths.config_file.write_text(content)


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

