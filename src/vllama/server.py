from __future__ import annotations

import json
import os
import signal
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Sequence

from vllama.config import AppConfig, AppPaths


@dataclass(frozen=True)
class ServerState:
    pid: int
    model: str
    host: str
    port: int
    started_at: str
    log_file: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ServerState":
        return cls(
            pid=int(data["pid"]),
            model=str(data["model"]),
            host=str(data["host"]),
            port=int(data["port"]),
            started_at=str(data["started_at"]),
            log_file=str(data["log_file"]),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ServerStatus:
    running: bool
    state: ServerState | None = None


PopenFactory = Callable[..., object]
PidExists = Callable[[int], bool]


def build_vllm_command(
    model: str,
    config: AppConfig,
    extra_args: Sequence[str] | None = None,
) -> list[str]:
    return [
        config.vllm_executable,
        "serve",
        model,
        "--host",
        config.host,
        "--port",
        str(config.port),
        *(extra_args or []),
    ]


class ServerManager:
    def __init__(
        self,
        paths: AppPaths | None = None,
        config: AppConfig | None = None,
        popen: PopenFactory | None = None,
        pid_exists: PidExists | None = None,
    ) -> None:
        self.paths = paths or AppPaths()
        self.config = config or AppConfig()
        self._popen = popen or subprocess.Popen
        self._pid_exists = pid_exists or _pid_exists

    def start(self, model: str, extra_args: Sequence[str] | None = None) -> ServerState:
        status = self.status()
        if status.running and status.state:
            raise RuntimeError(
                f"vLLM is already running as pid {status.state.pid} for {status.state.model}"
            )

        self.paths.ensure()
        log_file = self.paths.logs_dir / "vllm.log"
        command = build_vllm_command(model, self.config, extra_args)
        log_handle = log_file.open("ab")
        try:
            process = self._popen(
                command,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        finally:
            log_handle.close()

        pid = int(getattr(process, "pid"))
        state = ServerState(
            pid=pid,
            model=model,
            host=self.config.host,
            port=self.config.port,
            started_at=datetime.now(UTC).isoformat(),
            log_file=str(log_file),
        )
        self._write_state(state)
        return state

    def status(self) -> ServerStatus:
        state = self._read_state()
        if state is None:
            return ServerStatus(False, None)
        if self._pid_exists(state.pid):
            return ServerStatus(True, state)
        self._clear_state()
        return ServerStatus(False, None)

    def stop(self) -> bool:
        state = self._read_state()
        if state is None:
            return False
        if self._pid_exists(state.pid):
            try:
                os.killpg(state.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except OSError:
                os.kill(state.pid, signal.SIGTERM)
        self._clear_state()
        return True

    def _read_state(self) -> ServerState | None:
        if not self.paths.server_file.exists():
            return None
        try:
            raw = json.loads(self.paths.server_file.read_text())
            return ServerState.from_dict(raw)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._clear_state()
            return None

    def _write_state(self, state: ServerState) -> None:
        self.paths.ensure()
        self.paths.server_file.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n")

    def _clear_state(self) -> None:
        try:
            self.paths.server_file.unlink()
        except FileNotFoundError:
            pass


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def tail_log(path: str | Path, max_lines: int = 80) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    lines = file_path.read_text(errors="replace").splitlines()
    return "\n".join(lines[-max_lines:])

