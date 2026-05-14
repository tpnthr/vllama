import sys

from vllama.installer import build_vllm_install_command


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

