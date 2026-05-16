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

Run a one-shot prompt. If no compatible server is already listening,
`vllama` starts `vllm serve` for that model and waits for it to become ready:

```sh
vllama run Qwen/Qwen2.5-1.5B-Instruct "Why is the sky blue?"
```

Open an interactive chat loop. This also auto-starts vLLM when needed:

```sh
vllama chat Qwen/Qwen2.5-1.5B-Instruct
```

Start a vLLM server manually when you want explicit control:

```sh
vllama serve Qwen/Qwen2.5-1.5B-Instruct
```

Pass vLLM flags to an auto-started server with repeated `--arg` options:

```sh
vllama chat nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4 \
  --arg --trust-remote-code \
  --arg --max-model-len --arg 8192 \
  --arg --max-num-seqs --arg 1 \
  --arg --kv-cache-dtype --arg fp8 \
  --arg --reasoning-parser --arg nemotron_v3
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
- `vllama run` and `vllama chat` auto-start `vllm serve MODEL --host HOST --port PORT` when the configured endpoint is not already serving the requested model.
- `vllama serve` launches `vllm serve MODEL --host HOST --port PORT` directly.
- The default OpenAI-compatible endpoint is `http://127.0.0.1:8000/v1`.
- State is stored in `~/.vllama` unless `VLLAMA_HOME` is set.
- This MVP does not delete Hugging Face cache files when `vllama rm` is used; it only removes `vllama` metadata.

## Development

```sh
uv run pytest -q
uv run python -m vllama --help
```
