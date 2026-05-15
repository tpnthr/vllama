# vllama

`vllama` is an Ollama-like CLI and starter TUI for running models through a local vLLM backend.

The first target is Linux + NVIDIA CUDA. vLLM remains the inference engine; `vllama` provides the usability layer around installation checks, model metadata, server lifecycle, chat commands, and a simple terminal UI.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/tpnthr/vllama/main/install.sh | sh
```

The installer creates `~/.vllama/.venv` with Python 3.12 by default, installs this package from GitHub into it, and symlinks `vllama` into `~/.local/bin`. Override the Python with `VLLAMA_PYTHON=/path/to/python` if needed; vLLM currently requires Python `>=3.10,<3.14`.

For a non-destructive check:

```sh
vllama install --dry-run
```

## Install From A Checkout

```sh
sh scripts/install.sh
```

Use this form when developing from a local clone.

## Typical Usage

Start a vLLM server:

```sh
vllama serve Qwen/Qwen2.5-1.5B-Instruct
```

Run a one-shot prompt:

```sh
vllama run Qwen/Qwen2.5-1.5B-Instruct "Why is the sky blue?"
```

Open an interactive chat loop:

```sh
vllama chat Qwen/Qwen2.5-1.5B-Instruct
```

Track model metadata:

```sh
vllama pull Qwen/Qwen2.5-1.5B-Instruct
vllama list
vllama show Qwen/Qwen2.5-1.5B-Instruct
```

Inspect or stop the managed server:

```sh
vllama ps --logs
vllama stop
```

Launch the starter TUI:

```sh
vllama tui
```

## Notes

- vLLM uses Hugging Face model IDs and cache behavior. `vllama pull` records metadata for now; vLLM downloads model weights when serving if they are not already cached.
- `vllama serve` launches `vllm serve MODEL --host HOST --port PORT`.
- The default OpenAI-compatible endpoint is `http://127.0.0.1:8000/v1`.
- State is stored in `~/.vllama` unless `VLLAMA_HOME` is set.
- This MVP does not delete Hugging Face cache files when `vllama rm` is used; it only removes `vllama` metadata.

## Development

```sh
uv run pytest -q
uv run python -m vllama --help
```
