# vllama Design

## Goal

Build `vllama`, an Ollama-like CLI/TUI experience for Linux + NVIDIA systems that uses vLLM as the inference backend.

## Scope

The first version targets a single Linux host with NVIDIA CUDA and a local vLLM server process. It provides friendly commands for install checks, model metadata, server lifecycle, chat/run requests, and a starter TUI. It does not fork vLLM or reimplement model inference.

## Architecture

`vllama` is a Python package. The CLI is implemented with Typer, terminal rendering with Rich, TUI with Textual, and HTTP calls with httpx. vLLM is launched as a supervised subprocess via `vllm serve MODEL`; vLLM's OpenAI-compatible API remains the primary backend API.

State lives under `~/.vllama` by default:

- `config.toml`: host, port, default model, and vLLM executable.
- `models.json`: friendly metadata for models the user has pulled or served.
- `server.json`: currently managed server PID/model/port metadata.
- `logs/`: vLLM stdout/stderr logs.

## Commands

- `vllama install`: check Linux/NVIDIA/uv/vLLM readiness and optionally install vLLM with uv.
- `vllama serve MODEL`: start `vllm serve MODEL`.
- `vllama run MODEL [PROMPT]`: one-shot chat completion via the vLLM OpenAI-compatible API.
- `vllama chat MODEL`: interactive terminal chat loop.
- `vllama pull MODEL`: prefetch model assets through Hugging Face tooling when available, and record metadata.
- `vllama list`: show locally known model metadata.
- `vllama show MODEL`: show metadata for one model.
- `vllama ps`: show managed server status.
- `vllama stop`: stop the managed server.
- `vllama rm MODEL`: remove vllama metadata for a model without deleting Hugging Face cache files.
- `vllama tui`: launch a starter Textual TUI.

## Error Handling

Commands fail with actionable messages when vLLM, uv, NVIDIA tooling, or the server is unavailable. Server process state is checked before stale metadata is trusted. HTTP errors from vLLM are surfaced with status code and message.

## Testing

Unit tests cover config persistence, model metadata, vLLM command construction, server manager state transitions with fake process runners, and CLI behavior with Typer's test runner. Network and vLLM execution are isolated behind small interfaces so local tests do not require a GPU.
