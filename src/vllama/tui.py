from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from vllama.config import AppPaths, load_config
from vllama.models import ModelStore
from vllama.server import ServerManager


class VllamaTui(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #status {
        height: 3;
        padding: 1 2;
    }
    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="status")
        yield DataTable(id="models")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#models", DataTable)
        table.add_columns("Model", "Source", "Last Used")
        self._refresh()

    def action_refresh(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        paths = AppPaths()
        config = load_config(paths)
        status = ServerManager(paths, config).status()
        status_text = (
            f"Running: {status.state.model} pid={status.state.pid} http://{status.state.host}:{status.state.port}/v1"
            if status.running and status.state
            else "No managed vLLM server is running"
        )
        self.query_one("#status", Static).update(status_text)

        table = self.query_one("#models", DataTable)
        table.clear()
        for record in ModelStore(paths).list():
            table.add_row(record.name, record.source, record.last_used_at or "-")

