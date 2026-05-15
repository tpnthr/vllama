import sys
import subprocess

import pytest

from vllama.installer import (
    REQUIRED_DEBIAN_CUDA_PACKAGES,
    UnsupportedPythonForVllmError,
    build_vllm_install_command,
    check_debian_cuda_build_packages,
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


def test_debian_cuda_build_package_check_passes_when_required_packages_are_installed(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("vllama.installer.shutil.which", lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None)

    def fake_run(command, **kwargs):  # noqa: ANN001, ARG001
        stdout = "".join(f"{package}\tii \n" for package in REQUIRED_DEBIAN_CUDA_PACKAGES)
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    monkeypatch.setattr("vllama.installer.subprocess.run", fake_run)

    result = check_debian_cuda_build_packages()

    assert result.name == "cuda-build-deps"
    assert result.ok
    assert "5/5 installed" in result.detail


def test_debian_cuda_build_package_check_lists_missing_packages(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("vllama.installer.shutil.which", lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None)

    def fake_run(command, **kwargs):  # noqa: ANN001, ARG001
        stdout = "cuda-nvcc-13-1\tii \nninja-build\tii \n"
        return subprocess.CompletedProcess(command, 1, stdout=stdout, stderr="missing packages")

    monkeypatch.setattr("vllama.installer.subprocess.run", fake_run)

    result = check_debian_cuda_build_packages()

    assert not result.ok
    assert "2/5 installed" in result.detail
    assert "cuda-nvrtc-dev-13-1" in result.detail
    assert "libcurand-dev-13-1" in result.detail
    assert "libcublas-dev-13-1" in result.detail
