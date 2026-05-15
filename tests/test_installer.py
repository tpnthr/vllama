import sys

import pytest

from vllama.installer import (
    UnsupportedPythonForVllmError,
    build_vllm_install_command,
    ensure_vllm_python_supported,
    is_vllm_python_supported,
)


def test_build_vllm_install_command_targets_current_python() -> None:
    command = build_vllm_install_command()

    assert command == [
        "uv",
        "pip",
        "install",
        "--python",
        sys.executable,
        "vllm",
        "--torch-backend=auto",
    ]


def test_vllm_python_support_rejects_python_314() -> None:
    assert is_vllm_python_supported((3, 13, 0))
    assert not is_vllm_python_supported((3, 14, 0))


def test_ensure_vllm_python_supported_explains_reinstall_command() -> None:
    with pytest.raises(UnsupportedPythonForVllmError) as exc_info:
        ensure_vllm_python_supported((3, 14, 4))

    message = str(exc_info.value)
    assert "Python 3.14.4" in message
    assert "VLLAMA_PYTHON=3.12" in message
