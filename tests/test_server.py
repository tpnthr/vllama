from pathlib import Path

from vllama.config import AppConfig, AppPaths
from vllama.server import ServerManager, build_vllm_command


def test_build_vllm_command_includes_model_host_port_and_extra_args() -> None:
    config = AppConfig(host="0.0.0.0", port=8100, vllm_executable="vllm")

    command = build_vllm_command(
        "Qwen/Qwen2.5-1.5B-Instruct",
        config,
        extra_args=["--tensor-parallel-size", "2"],
    )

    assert command == [
        "vllm",
        "serve",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "--host",
        "0.0.0.0",
        "--port",
        "8100",
        "--tensor-parallel-size",
        "2",
    ]


class FakeProcess:
    pid = 4242


def test_server_manager_writes_state_when_starting(tmp_path: Path) -> None:
    paths = AppPaths(tmp_path)
    config = AppConfig(port=9000)
    calls: list[list[str]] = []

    def fake_popen(command, stdout, stderr, start_new_session):  # noqa: ANN001
        calls.append(command)
        return FakeProcess()

    manager = ServerManager(paths, config, popen=fake_popen, pid_exists=lambda pid: False)

    state = manager.start("Qwen/Qwen2.5-1.5B-Instruct", extra_args=["--dtype", "auto"])

    assert state.pid == 4242
    assert state.model == "Qwen/Qwen2.5-1.5B-Instruct"
    assert calls[0][:3] == ["vllm", "serve", "Qwen/Qwen2.5-1.5B-Instruct"]
    assert paths.server_file.exists()
    assert paths.logs_dir.joinpath("vllm.log").exists()


def test_server_manager_reports_stopped_for_stale_state(tmp_path: Path) -> None:
    paths = AppPaths(tmp_path)
    paths.ensure()
    paths.server_file.write_text(
        '{"pid":9999,"model":"stale","host":"127.0.0.1","port":8000,"started_at":"now","log_file":"x"}'
    )
    manager = ServerManager(paths, AppConfig(), pid_exists=lambda pid: False)

    assert manager.status().running is False
    assert manager.status().state is None

