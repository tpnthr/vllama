from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


class UnsupportedPythonForVllmError(RuntimeError):
    """Raised when the active Python cannot install or run vLLM."""


VLLM_PYTHON_MIN = (3, 10)
VLLM_PYTHON_MAX_EXCLUSIVE = (3, 14)


def collect_install_checks() -> list[CheckResult]:
    return [
        _check_linux(),
        _check_python(),
        _check_nvidia_smi(),
        _check_uv(),
        _check_vllm(),
    ]


def build_vllm_install_command(
    uv_executable: str = "uv",
    python_executable: str = sys.executable,
) -> list[str]:
    return [
        uv_executable,
        "pip",
        "install",
        "--python",
        python_executable,
        "vllm",
        "--torch-backend=auto",
    ]


def install_vllm_with_uv(dry_run: bool = False) -> list[str]:
    ensure_vllm_python_supported()
    command = build_vllm_install_command(uv_executable=find_uv_executable() or "uv")
    if dry_run:
        return command
    subprocess.run(command, check=True)
    return command


def find_vllm_executable() -> str | None:
    path = shutil.which("vllm")
    if path:
        return path
    sibling = Path(sys.executable).with_name("vllm")
    if sibling.exists():
        return str(sibling)
    return None


def find_uv_executable() -> str | None:
    path = shutil.which("uv")
    if path:
        return path
    local_uv = Path.home() / ".local" / "bin" / "uv"
    if local_uv.exists():
        return str(local_uv)
    return None


def is_vllm_python_supported(version_info: Sequence[int] = sys.version_info) -> bool:
    major_minor = (int(version_info[0]), int(version_info[1]))
    return VLLM_PYTHON_MIN <= major_minor < VLLM_PYTHON_MAX_EXCLUSIVE


def ensure_vllm_python_supported(version_info: Sequence[int] = sys.version_info) -> None:
    if is_vllm_python_supported(version_info):
        return
    version = _python_version_label(version_info)
    raise UnsupportedPythonForVllmError(
        "vLLM cannot be installed into this vllama environment because it uses "
        f"Python {version}. vLLM currently requires Python >=3.10,<3.14.\n"
        "Reinstall vllama with a compatible Python:\n"
        "  rm -rf ~/.vllama/.venv\n"
        "  VLLAMA_PYTHON=3.12 curl -fsSL https://raw.githubusercontent.com/tpnthr/vllama/main/install.sh | sh"
    )


def _python_version_label(version_info: Sequence[int] = sys.version_info) -> str:
    return ".".join(str(int(part)) for part in version_info[:3])


def _check_linux() -> CheckResult:
    system = platform.system()
    return CheckResult("linux", system == "Linux", f"platform={system}")


def _check_python() -> CheckResult:
    ok = is_vllm_python_supported()
    version = _python_version_label()
    detail = f"Python {version}; vLLM requires >=3.10,<3.14"
    return CheckResult("python", ok, detail)


def _check_nvidia_smi() -> CheckResult:
    path = shutil.which("nvidia-smi")
    if not path:
        return CheckResult("nvidia-smi", False, "not found on PATH")
    try:
        completed = subprocess.run(
            [path, "--query-gpu=name,memory.total", "--format=csv,noheader"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return CheckResult("nvidia-smi", False, str(exc))
    first_line = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else "no GPUs"
    return CheckResult("nvidia-smi", True, first_line)


def _check_uv() -> CheckResult:
    path = find_uv_executable()
    return CheckResult("uv", bool(path), path or "not found on PATH")


def _check_vllm() -> CheckResult:
    path = find_vllm_executable()
    return CheckResult("vllm", bool(path), path or "not found on PATH")
