#!/usr/bin/env sh
set -eu

VLLAMA_HOME="${VLLAMA_HOME:-$HOME/.vllama}"
VLLAMA_BIN_DIR="${VLLAMA_BIN_DIR:-$HOME/.local/bin}"
PROJECT_ROOT="${VLLAMA_SOURCE:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"

printf '%s\n' "vllama installer"
printf '%s\n' "home: $VLLAMA_HOME"
printf '%s\n' "source: $PROJECT_ROOT"

mkdir -p "$VLLAMA_HOME" "$VLLAMA_BIN_DIR"

if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' "uv was not found; installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  if [ -f "$HOME/.local/bin/uv" ]; then
    PATH="$HOME/.local/bin:$PATH"
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' "uv installation did not put uv on PATH. Add ~/.local/bin to PATH and rerun." >&2
  exit 1
fi

VLLAMA_PYTHON="${VLLAMA_PYTHON:-python3}"
uv venv "$VLLAMA_HOME/.venv" --python "$VLLAMA_PYTHON" --seed
uv pip install --python "$VLLAMA_HOME/.venv/bin/python" "$PROJECT_ROOT"

ln -sf "$VLLAMA_HOME/.venv/bin/vllama" "$VLLAMA_BIN_DIR/vllama"

printf '%s\n' ""
printf '%s\n' "vllama installed at $VLLAMA_BIN_DIR/vllama"
printf '%s\n' "If needed, add this to your shell profile:"
printf '%s\n' "  export PATH=\"$VLLAMA_BIN_DIR:\$PATH\""
printf '%s\n' ""
printf '%s\n' "Next:"
printf '%s\n' "  vllama install --dry-run"
printf '%s\n' "  vllama serve Qwen/Qwen2.5-1.5B-Instruct"
printf '%s\n' "  vllama run Qwen/Qwen2.5-1.5B-Instruct \"Why is the sky blue?\""
