from pathlib import Path

from typer.testing import CliRunner

from vllama.cli import app
from vllama.installer import CheckResult, UnsupportedPythonForVllmError


def test_cli_list_shows_empty_state(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No models known to vllama yet" in result.output


def test_cli_install_dry_run_prints_checks(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(app, ["install", "--dry-run"])

    assert result.exit_code == 0
    assert "vllama install check" in result.output
    assert "cuda-build-deps" in result.output
    assert "Dry run: no packages were installed" in result.output


def test_cli_install_reports_unsupported_python_without_traceback(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    monkeypatch.setattr("vllama.cli.collect_install_checks", lambda: [CheckResult("uv", True, "/tmp/uv")])

    def fail_install(*, dry_run: bool = False) -> list[str]:
        raise UnsupportedPythonForVllmError("Python 3.14 is not supported")

    monkeypatch.setattr("vllama.cli.install_vllm_with_uv", fail_install)
    runner = CliRunner()

    result = runner.invoke(app, ["install"])

    assert result.exit_code == 1
    assert "Python 3.14 is not supported" in result.output
    assert "Traceback" not in result.output


def test_cli_serve_requires_missing_vllm_to_be_reported(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(app, ["serve", "Qwen/Qwen2.5-1.5B-Instruct", "--vllm-bin", "/missing/vllm"])

    assert result.exit_code == 1
    assert "vLLM executable was not found" in result.output


def test_cli_run_ensures_server_before_request(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    ensured: list[str] = []

    def fake_ensure(model: str, startup_timeout: float, extra_args: list[str] | None = None) -> None:
        ensured.append(f"{model}:{startup_timeout}:{extra_args}")

    class FakeClient:
        def __init__(self, config) -> None:  # noqa: ANN001
            self.config = config

        def chat(self, model, messages, stream=False):  # noqa: ANN001, ARG002
            return "hello from vllm"

    monkeypatch.setattr("vllama.cli._ensure_server_for_model", fake_ensure)
    monkeypatch.setattr("vllama.cli.VllmClient", FakeClient)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "run",
            "Qwen/Qwen2.5-1.5B-Instruct",
            "hello",
            "--arg",
            "--trust-remote-code",
            "--startup-timeout",
            "3",
        ],
    )

    assert result.exit_code == 0
    assert ensured == ["Qwen/Qwen2.5-1.5B-Instruct:3.0:['--trust-remote-code']"]
    assert "hello from vllm" in result.output


def test_cli_chat_ensures_server_before_prompt_loop(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    ensured: list[str] = []

    def fake_ensure(model: str, startup_timeout: float, extra_args: list[str] | None = None) -> None:
        ensured.append(f"{model}:{startup_timeout}:{extra_args}")

    class FakeClient:
        def __init__(self, config) -> None:  # noqa: ANN001
            self.config = config

        def chat(self, model, messages, stream=False):  # noqa: ANN001, ARG002
            return "assistant reply"

    monkeypatch.setattr("vllama.cli._ensure_server_for_model", fake_ensure)
    monkeypatch.setattr("vllama.cli.VllmClient", FakeClient)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["chat", "Qwen/Qwen2.5-1.5B-Instruct", "--arg", "--trust-remote-code", "--startup-timeout", "3"],
        input="hello\n/bye\n",
    )

    assert result.exit_code == 0
    assert ensured == ["Qwen/Qwen2.5-1.5B-Instruct:3.0:['--trust-remote-code']"]
    assert "assistant reply" in result.output
