from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def collect_install_checks() -> list[CheckResult]:
    return [
        _check_linux(),
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


def _check_linux() -> CheckResult:
    system = platform.system()
    return CheckResult("linux", system == "Linux", f"platform={system}")


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
