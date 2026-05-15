#!/usr/bin/env sh
set -eu

REPO_URL="${VLLAMA_REPO_URL:-https://github.com/tpnthr/vllama.git}"
VLLAMA_HOME="${VLLAMA_HOME:-$HOME/.vllama}"
VLLAMA_BIN_DIR="${VLLAMA_BIN_DIR:-$HOME/.local/bin}"
VLLAMA_PYTHON="${VLLAMA_PYTHON:-3.12}"

printf '%s\n' "vllama installer"
printf '%s\n' "repository: $REPO_URL"
printf '%s\n' "home: $VLLAMA_HOME"

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

venv_python_is_vllm_compatible() {
  "$1" - <<'PY'
import sys

raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)
PY
}

VENV_PYTHON="$VLLAMA_HOME/.venv/bin/python"
if [ -x "$VENV_PYTHON" ]; then
  if venv_python_is_vllm_compatible "$VENV_PYTHON"; then
    printf '%s\n' "Using existing compatible Python environment: $VENV_PYTHON"
  else
    printf '%s\n' "Existing vllama environment uses a Python version vLLM does not support; replacing it."
    uv venv "$VLLAMA_HOME/.venv" --python "$VLLAMA_PYTHON" --seed --clear
  fi
elif [ -e "$VLLAMA_HOME/.venv" ]; then
  printf '%s\n' "Existing vllama environment is incomplete; replacing it."
  uv venv "$VLLAMA_HOME/.venv" --python "$VLLAMA_PYTHON" --seed --clear
else
  uv venv "$VLLAMA_HOME/.venv" --python "$VLLAMA_PYTHON" --seed
fi
uv pip install --python "$VLLAMA_HOME/.venv/bin/python" "git+$REPO_URL"

ln -sf "$VLLAMA_HOME/.venv/bin/vllama" "$VLLAMA_BIN_DIR/vllama"

printf '%s\n' ""
printf '%s\n' "vllama installed at $VLLAMA_BIN_DIR/vllama"
printf '%s\n' "If needed, add this to your shell profile:"
printf '%s\n' "  export PATH=\"$VLLAMA_BIN_DIR:\$PATH\""
printf '%s\n' ""
printf '%s\n' "Next:"
printf '%s\n' "  vllama install --dry-run"
printf '%s\n' "  vllama install"
printf '%s\n' "  vllama serve Qwen/Qwen2.5-1.5B-Instruct"
printf '%s\n' "  vllama run Qwen/Qwen2.5-1.5B-Instruct \"Why is the sky blue?\""
