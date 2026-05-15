from __future__ import annotations

from datetime import UTC, datetime
import shutil
from subprocess import CalledProcessError
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from vllama.client import VllmClient
from vllama.config import AppConfig, AppPaths, load_config, save_config
from vllama.installer import (
    UnsupportedPythonForVllmError,
    collect_install_checks,
    find_vllm_executable,
    install_vllm_with_uv,
)
from vllama.models import ModelRecord, ModelStore
from vllama.server import ServerManager, tail_log

app = typer.Typer(no_args_is_help=True, help="Ollama-like CLI and TUI for vLLM backends.")
console = Console()


def _paths() -> AppPaths:
    return AppPaths()


def _config() -> AppConfig:
    return load_config(_paths())


@app.command()
def install(
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Check only; do not install packages.")] = False,
) -> None:
    """Check Linux/NVIDIA/vLLM readiness and optionally install vLLM."""
    console.print("[bold]vllama install check[/bold]")
    checks = collect_install_checks()
    table = Table("Check", "OK", "Detail")
    for check in checks:
        table.add_row(check.name, "yes" if check.ok else "no", check.detail)
    console.print(table)
    if dry_run:
        console.print("Dry run: no packages were installed")
        return
    if not any(check.name == "uv" and check.ok for check in checks):
        console.print("uv is required before installing vLLM")
        raise typer.Exit(1)
    try:
        install_vllm_with_uv(dry_run=False)
    except UnsupportedPythonForVllmError as exc:
        console.print(str(exc))
        raise typer.Exit(1) from exc
    except CalledProcessError as exc:
        command = " ".join(str(part) for part in exc.cmd)
        console.print(f"vLLM installation failed with exit code {exc.returncode}: {command}")
        raise typer.Exit(exc.returncode) from exc
    vllm_path = find_vllm_executable()
    if vllm_path:
        paths = _paths()
        current = load_config(paths)
        save_config(
            paths,
            AppConfig(
                host=current.host,
                port=current.port,
                default_model=current.default_model,
                vllm_executable=vllm_path,
            ),
        )
        console.print(f"Configured vLLM executable: {vllm_path}")


@app.command()
def serve(
    model: str,
    host: Annotated[str | None, typer.Option("--host", help="Host for vLLM server.")] = None,
    port: Annotated[int | None, typer.Option("--port", help="Port for vLLM server.")] = None,
    vllm_bin: Annotated[str | None, typer.Option("--vllm-bin", help="Path/name of vLLM executable.")] = None,
    extra_arg: Annotated[list[str] | None, typer.Option("--arg", help="Extra argument passed to vllm serve.")] = None,
) -> None:
    """Start a managed vLLM server."""
    paths = _paths()
    base = load_config(paths)
    config = AppConfig(
        host=host or base.host,
        port=port or base.port,
        default_model=model,
        vllm_executable=vllm_bin or base.vllm_executable,
    )
    if not shutil.which(config.vllm_executable):
        console.print(f"vLLM executable was not found: {config.vllm_executable}")
        raise typer.Exit(1)

    save_config(paths, config)
    state = ServerManager(paths, config).start(model, extra_args=extra_arg or [])
    ModelStore(paths).upsert(_record(model))
    console.print(f"Started vLLM for [bold]{model}[/bold] as pid {state.pid}")
    console.print(f"OpenAI-compatible endpoint: http://{state.host}:{state.port}/v1")
    console.print(f"Logs: {state.log_file}")


@app.command()
def run(model: str, prompt: str) -> None:
    """Send a one-shot prompt to the running vLLM server."""
    paths = _paths()
    ModelStore(paths).upsert(_record(model))
    message = [{"role": "user", "content": prompt}]
    try:
        content = VllmClient(load_config(paths)).chat(model, message, stream=False)
    except Exception as exc:  # noqa: BLE001
        console.print(f"Request failed: {exc}")
        raise typer.Exit(1) from exc
    console.print(content)


@app.command()
def chat(model: str) -> None:
    """Open a simple interactive chat loop."""
    messages: list[dict[str, str]] = []
    client = VllmClient(_config())
    console.print(f"Chatting with {model}. Type /bye to exit.")
    while True:
        prompt = typer.prompt("you")
        if prompt.strip() in {"/bye", "/exit", "/quit"}:
            return
        messages.append({"role": "user", "content": prompt})
        try:
            content = client.chat(model, messages, stream=False)
        except Exception as exc:  # noqa: BLE001
            console.print(f"Request failed: {exc}")
            continue
        text = str(content)
        messages.append({"role": "assistant", "content": text})
        console.print(f"[bold]assistant[/bold]: {text}")


@app.command("pull")
def pull_model(model: str) -> None:
    """Record/prefetch a Hugging Face model for vLLM use."""
    ModelStore(_paths()).upsert(_record(model))
    console.print(f"Recorded model [bold]{model}[/bold].")
    console.print("vLLM will fetch weights through Hugging Face when the model is served.")


@app.command("list")
def list_models() -> None:
    """List models known to vllama."""
    records = ModelStore(_paths()).list()
    if not records:
        console.print("No models known to vllama yet.")
        return
    table = Table("Model", "Source", "Path", "Last Used")
    for record in records:
        table.add_row(record.name, record.source, record.path or "-", record.last_used_at or "-")
    console.print(table)


@app.command()
def show(model: str) -> None:
    """Show vllama metadata for a model."""
    record = ModelStore(_paths()).get(model)
    if not record:
        console.print(f"Unknown model: {model}")
        raise typer.Exit(1)
    table = Table("Field", "Value")
    table.add_row("name", record.name)
    table.add_row("source", record.source)
    table.add_row("path", record.path or "-")
    table.add_row("last_used_at", record.last_used_at or "-")
    console.print(table)


@app.command()
def ps(
    logs: Annotated[bool, typer.Option("--logs", help="Show recent vLLM log lines.")] = False,
) -> None:
    """Show managed vLLM server status."""
    status = ServerManager(_paths(), _config()).status()
    if not status.running or not status.state:
        console.print("No managed vLLM server is running.")
        return
    state = status.state
    console.print(f"vLLM running pid={state.pid} model={state.model} url=http://{state.host}:{state.port}/v1")
    if logs:
        console.print(tail_log(state.log_file))


@app.command()
def stop() -> None:
    """Stop the managed vLLM server."""
    stopped = ServerManager(_paths(), _config()).stop()
    console.print("Stopped managed vLLM server." if stopped else "No managed vLLM server was running.")


@app.command("rm")
def remove_model(model: str) -> None:
    """Remove vllama metadata for a model."""
    removed = ModelStore(_paths()).remove(model)
    if removed:
        console.print(f"Removed metadata for {model}.")
    else:
        console.print(f"Unknown model: {model}")
        raise typer.Exit(1)


@app.command()
def tui() -> None:
    """Launch the terminal UI."""
    from vllama.tui import VllamaTui

    VllamaTui().run()


def _record(model: str) -> ModelRecord:
    return ModelRecord(
        name=model,
        source="huggingface",
        path=None,
        last_used_at=datetime.now(UTC).isoformat(),
    )


if __name__ == "__main__":
    app()
