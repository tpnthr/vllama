from pathlib import Path

from typer.testing import CliRunner

from vllama.cli import app


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
    assert "Dry run: no packages were installed" in result.output


def test_cli_serve_requires_missing_vllm_to_be_reported(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("VLLAMA_HOME", str(tmp_path))
    runner = CliRunner()

    result = runner.invoke(app, ["serve", "Qwen/Qwen2.5-1.5B-Instruct", "--vllm-bin", "/missing/vllm"])

    assert result.exit_code == 1
    assert "vLLM executable was not found" in result.output

