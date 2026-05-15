# Ollama Functionality Reference

Documentation snapshot: 2026-05-15, based on the official Ollama documentation index at <https://docs.ollama.com/llms.txt>, the official OpenAPI spec at <https://docs.ollama.com/openapi.yaml>, official docs pages, and current local CLI help from `ollama` client `0.23.3`.

This file treats "functions" as the documented user-facing capabilities Ollama offers: CLI commands, native REST endpoints, compatibility APIs, SDK calls, Modelfile instructions, cloud/web APIs, integrations, and runtime configuration.

## 1. What Ollama Is For

Ollama is a local and cloud-capable model runner for open models. It provides:

- A CLI for running, downloading, creating, copying, publishing, listing, stopping, and inspecting models.
- A local HTTP API, normally at `http://localhost:11434`, for inference and model management.
- OpenAI-compatible and Anthropic-compatible APIs for tools that already speak those protocols.
- Official Python and JavaScript/TypeScript SDKs.
- Modelfiles for custom models, prompt templates, parameters, adapters, and licenses.
- Cloud models, direct `ollama.com` API access, and authenticated web search/fetch APIs.
- Integrations with coding agents, IDEs, editors, RAG tools, automation tools, and notebooks.

## 2. CLI Commands

The CLI shape is:

```text
ollama [flags]
ollama [command]
```

Global flags from local CLI help:

- `-h`, `--help`: show help.
- `-v`, `--version`: show version information.
- `--verbose`: show response timings.
- `--nowordwrap`: do not wrap words automatically.

### `ollama serve`

Starts the Ollama server. Alias in the local CLI: `ollama start`.

Primary use cases:

- Run the HTTP API on the configured host and port.
- Keep a background model server available for CLI, SDK, and API requests.
- Configure server behavior with environment variables such as `OLLAMA_HOST`, `OLLAMA_MODELS`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_KEEP_ALIVE`, and concurrency settings.

### `ollama run MODEL [PROMPT]`

Runs a model interactively or with a one-shot prompt.

Documented capabilities:

- Chat with a text model.
- Pass a prompt directly on the command line.
- Pipe input into a model.
- Use multiline input in interactive sessions with triple quotes.
- Send local image paths to multimodal models.
- Generate embeddings from embedding models.
- Enable structured output with `--format json`.
- Enable or hide thinking output for thinking-capable models.
- Keep models loaded with `--keepalive`.
- Use embedding-specific controls such as `--dimensions` and `--truncate`.

Local CLI flags include:

- `--format string`: response format, for example `json`.
- `--think string[="true"]`: `true`, `false`, `high`, `medium`, or `low` for supported models.
- `--hidethinking`: hide thinking output when available.
- `--keepalive string`: model keep-alive duration, for example `5m`.
- `--dimensions int`: truncate embedding output dimensions.
- `--truncate`: truncate embedding inputs that exceed context length; set `--truncate=false` to error instead.
- `--insecure`: use an insecure registry.
- `--experimental`: enable experimental agent loop with tools.
- `--experimental-websearch`: enable web search tool in experimental mode.
- `--experimental-yolo`: skip tool approval prompts. Use with caution.
- Experimental image generation flags: `--width`, `--height`, `--steps`, `--seed`, `--negative`.

### `ollama pull MODEL`

Downloads a model from a registry. Also updates a local model when the registry version changes.

Flags:

- `--insecure`: use an insecure registry.

### `ollama push MODEL`

Publishes a model to a registry, usually `ollama.com`. This typically requires sign-in and a properly named model such as `username/model`.

Flags:

- `--insecure`: use an insecure registry.

### `ollama create MODEL`

Creates a custom model from a `Modelfile` or equivalent API request.

Flags from local CLI help:

- `-f`, `--file string`: Modelfile path, default `Modelfile`.
- `-q`, `--quantize string`: quantize to a level such as `q4_K_M`.
- `--draft-quantize string`: quantize a draft model to a given level.
- `--experimental`: enable experimental Safetensors model creation.

### `ollama show MODEL`

Shows model information.

Flags:

- `--license`: show license.
- `--modelfile`: show generated Modelfile.
- `--parameters`: show model parameters.
- `--system`: show system message.
- `--template`: show template.
- `-v`, `--verbose`: show detailed model information.

### `ollama list` / `ollama ls`

Lists local models.

The API response includes model names, modified time, size, digest, and model details such as format, family, parameter size, and quantization level.

### `ollama ps`

Lists currently loaded/running models.

Useful fields include model name, size, digest, expiration time, VRAM size, processor/offload split in CLI output, and context length.

### `ollama stop MODEL`

Stops a running model and unloads it from memory.

### `ollama cp SOURCE DESTINATION`

Copies a model to another local name. This is useful for:

- Giving a model a registry-qualified name before `ollama push`.
- Creating compatibility names such as `gpt-3.5-turbo` or `claude-3-5-sonnet` for tools that expect default provider names.

### `ollama rm MODEL [MODEL...]`

Removes one or more local models.

### `ollama signin`

Signs in to `ollama.com`.

Required for cloud models, private models, model publishing, and some account-backed features.

### `ollama signout`

Signs out from `ollama.com`.

### `ollama launch [INTEGRATION]`

Launches the Ollama menu or configures/starts supported integrations.

Common flags:

- `--model string`: choose a model for the integration.
- `--config`: configure without launching.
- `--restore`: restore an integration to its default profile.
- `-y`, `--yes`: automatically answer yes to confirmation prompts.
- `-- [EXTRA_ARGS...]`: pass arguments through to the launched integration.

Supported integrations in official docs and/or current local CLI help include Claude Code, Cline, Codex, Copilot CLI, Droid, Goose, Hermes Agent, Kimi Code CLI, OpenCode, OpenClaw, Pi, Pool, and VS Code. Other documented integrations may be configured manually.

## 3. Native Ollama REST API

Default local base URL:

```text
http://localhost:11434
```

Direct cloud base URL:

```text
https://ollama.com
```

Cloud API requests require:

```text
Authorization: Bearer $OLLAMA_API_KEY
```

### `POST /api/generate`

Generates a completion from a prompt.

Request fields:

- `model` (required): model name.
- `prompt`: text prompt.
- `suffix`: text after the insertion point for fill-in-the-middle models.
- `images`: base64-encoded images for multimodal models.
- `format`: `"json"` or a JSON schema object for structured outputs.
- `system`: override system prompt.
- `stream`: default `true`; when `false`, returns one complete JSON object.
- `think`: `true`, `false`, or `high`/`medium`/`low` for supported thinking models.
- `raw`: bypass prompt templating.
- `keep_alive`: duration or number controlling how long the model stays loaded.
- `options`: runtime generation options.
- `logprobs`: request token log probabilities when supported.
- `top_logprobs`: number of alternate token probabilities to return.

Response fields include generated `response`, optional `thinking`, `done`, `done_reason`, timing fields, token counts, and optional `logprobs`.

Special uses:

- Send only `model` to preload the model.
- Send `keep_alive: 0` to unload after the request.
- Use `format` for JSON mode or schema-constrained output.
- Use `images` for vision-capable models.

### `POST /api/chat`

Generates the next assistant message in a chat conversation.

Request fields:

- `model` (required): model name.
- `messages` (required): chat history.
- `tools`: function tools the model may call.
- `format`: `"json"` or a JSON schema object.
- `options`: runtime generation options.
- `stream`: default `true`.
- `think`: thinking control for supported models.
- `keep_alive`: model keep-alive duration.
- `logprobs`: request token log probabilities when supported.
- `top_logprobs`: number of top probabilities per token.

Message fields:

- `role`: `system`, `user`, `assistant`, or `tool`.
- `content`: text content.
- `images`: optional base64 images.
- `tool_calls`: tool call requests produced by the model.

Response fields include `message.role`, `message.content`, optional `message.thinking`, optional `message.tool_calls`, `done`, `done_reason`, timings, token counts, and optional `logprobs`.

### `POST /api/embed`

Creates vector embeddings for text.

Request fields:

- `model` (required): embedding model name.
- `input` (required): string or array of strings.
- `truncate`: default `true`; truncate overlong inputs instead of erroring.
- `dimensions`: number of dimensions to generate.
- `keep_alive`: model keep-alive duration.
- `options`: runtime options.

Response fields include `model`, `embeddings`, `total_duration`, `load_duration`, and `prompt_eval_count`.

### `GET /api/tags`

Lists local models and details.

Response includes `models`, each with fields such as `name`, `model`, `remote_model`, `remote_host`, `modified_at`, `size`, `digest`, and `details`.

### `GET /api/ps`

Lists models currently loaded into memory.

Response includes `models`, each with `name`, `model`, `size`, `digest`, `details`, `expires_at`, `size_vram`, and `context_length`.

### `POST /api/show`

Shows model details.

Request fields:

- `model` (required).
- `verbose`: include large verbose fields.

Response may include `parameters`, `license`, `modified_at`, `details`, `template`, `capabilities`, and `model_info`.

### `POST /api/create`

Creates a model.

Request fields:

- `model` (required): target model name.
- `from`: existing model or source to build from.
- `template`: prompt template.
- `license`: string or array of license strings.
- `system`: system prompt.
- `parameters`: model parameter key-value object.
- `messages`: initial message history.
- `quantize`: quantization level such as `q4_K_M` or `q8_0`.
- `stream`: default `true`; stream create status updates.

### `POST /api/copy`

Copies a model.

Request fields:

- `source` (required).
- `destination` (required).

### `POST /api/pull`

Pulls/downloads a model.

Request fields:

- `model` (required).
- `insecure`: allow insecure connections.
- `stream`: stream progress updates, default `true`.

### `POST /api/push`

Pushes/publishes a model.

Request fields:

- `model` (required).
- `insecure`: allow insecure connections.
- `stream`: stream progress updates, default `true`.

### `DELETE /api/delete`

Deletes a model.

Request fields:

- `model` (required).

### `GET /api/version`

Returns the Ollama server version.

Response:

- `version`: version string.

### Runtime Options

The OpenAPI spec explicitly documents these common `options` fields:

- `seed`: random seed for reproducible output.
- `temperature`: randomness.
- `top_k`: top-K token filtering.
- `top_p`: nucleus sampling threshold.
- `min_p`: minimum probability threshold.
- `stop`: string or list of stop sequences.
- `num_ctx`: context length in tokens.
- `num_predict`: maximum generated tokens.

The schema allows additional properties, so model/runtime-specific options may also be accepted.

### Streaming

Native generation, chat, create, pull, and push endpoints can stream newline-delimited JSON (`application/x-ndjson`). Set `stream: false` when you want a single complete JSON response.

Streaming is best for low perceived latency and long generations. Non-streaming is easier for short responses, structured outputs, and simple processing.

### Usage Metrics

Generation/chat responses include useful metrics:

- `total_duration`: total time in nanoseconds.
- `load_duration`: model load time.
- `prompt_eval_count`: input tokens processed.
- `prompt_eval_duration`: prompt evaluation time.
- `eval_count`: output tokens generated.
- `eval_duration`: generation time.

### Errors

Documented status codes:

- `200`: success.
- `400`: bad request, missing parameters, invalid JSON, and similar.
- `404`: missing model or not found.
- `429`: rate limit exceeded.
- `500`: internal server error.
- `502`: bad gateway, for example unreachable cloud model.

Streaming errors may appear during a stream, so streaming clients should check chunks as well as HTTP status.

## 4. OpenAI-Compatible API

Base URL:

```text
http://localhost:11434/v1/
```

An API key may be required by OpenAI SDK clients but is ignored for local Ollama.

### `POST /v1/chat/completions`

Supported features:

- Chat completions.
- Streaming.
- JSON mode.
- Reproducible outputs.
- Vision with base64 image content.
- Tools/function calling.
- Reasoning/thinking control for thinking models.

Supported request fields:

- `model`
- `messages` with text content, base64 image content, and array content parts.
- `frequency_penalty`
- `presence_penalty`
- `response_format`
- `seed`
- `stop`
- `stream`
- `stream_options.include_usage`
- `temperature`
- `top_p`
- `max_tokens`
- `tools`
- `reasoning_effort`: `high`, `medium`, `low`, or `none`.
- `reasoning.effort`: `high`, `medium`, `low`, or `none`.

Not documented as supported:

- `tool_choice`
- `logit_bias`
- `user`
- `n`
- logprobs for this compatibility endpoint
- image URLs; base64 images are supported.

### `POST /v1/completions`

Supported features:

- Text completions.
- Streaming.
- JSON mode.
- Reproducible outputs.

Supported request fields:

- `model`
- `prompt` as a string.
- `frequency_penalty`
- `presence_penalty`
- `seed`
- `stop`
- `stream`
- `stream_options.include_usage`
- `temperature`
- `top_p`
- `max_tokens`
- `suffix`

Not documented as supported:

- `best_of`
- `echo`
- `logit_bias`
- `user`
- `n`
- logprobs for this compatibility endpoint.

### `GET /v1/models`

Lists available models in an OpenAI-style shape.

Notes:

- `created` corresponds to the model's last modified time.
- `owned_by` corresponds to the Ollama username or defaults to `library`.

### `GET /v1/models/{model}`

Retrieves one model in an OpenAI-style shape.

### `POST /v1/embeddings`

Supported request fields:

- `model`
- `input` as a string or array of strings.
- `encoding_format`
- `dimensions`

Not documented as supported:

- array of tokens.
- array of token arrays.
- `user`.

### `POST /v1/images/generations` (experimental)

Generates images with image generation models.

Supported request fields:

- `model`
- `prompt`
- `size`, for example `1024x1024`.
- `response_format`, currently only `b64_json`.

Not documented as supported:

- `n`
- `quality`
- `style`
- `user`

### `POST /v1/responses`

Documented as added in Ollama `v0.13.3`.

Supported features:

- Streaming.
- Tools/function calling.
- Reasoning summaries for thinking models.
- Non-stateful requests only.

Supported request fields:

- `model`
- `input`
- `instructions`
- `tools`
- `stream`
- `temperature`
- `top_p`
- `max_output_tokens`

Not documented as supported:

- `previous_response_id`
- `conversation`
- `truncation`

## 5. Anthropic-Compatible API

Base URL:

```text
http://localhost:11434
```

For tools expecting Anthropic:

```text
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_BASE_URL=http://localhost:11434
```

The token and `anthropic-version` header are accepted locally but not validated or used.

### `POST /v1/messages`

Supported features:

- Messages.
- Streaming.
- System prompts.
- Multi-turn conversations.
- Vision with base64 image content.
- Tools/function calling.
- Tool results.
- Thinking/extended thinking.

Supported request fields:

- `model`
- `max_tokens`
- `messages`
- text content
- base64 image content
- content block arrays
- `tool_use` blocks
- `tool_result` blocks
- `thinking` blocks
- `system` as string or array
- `stream`
- `temperature`
- `top_p`
- `top_k`
- `stop_sequences`
- `tools`
- `thinking`

Supported response fields/events:

- `id`, `type`, `role`, `model`, `content`, `stop_reason`, and `usage`.
- Streaming events: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, `ping`, and `error`.

Not documented as supported:

- `/v1/messages/count_tokens`
- `tool_choice`
- `metadata`
- prompt caching with `cache_control`
- batches API
- citations
- PDF `document` content blocks
- server-sent errors in the same style as Anthropic

Partial support:

- Base64 images are supported; URL images are not.
- Extended thinking accepts `budget_tokens`, but it is not enforced.

## 6. Cloud, Authentication, Web Search, and Web Fetch

### Authentication

Authentication is needed for:

- Running cloud models.
- Publishing models.
- Downloading private models.
- Programmatic direct access to `ollama.com`.
- Web search and web fetch.

Methods:

- `ollama signin` for local CLI/app authentication.
- API keys from <https://ollama.com/settings/keys> for direct API access.
- `OLLAMA_API_KEY` environment variable or `Authorization: Bearer ...` header.

### Cloud Models

Cloud models let Ollama offload larger models to Ollama's cloud service while preserving the local CLI/API workflow.

Ways to use cloud models:

- Sign in with `ollama signin`.
- Pull or reference a cloud model such as a `:cloud` model.
- Use normal CLI, Python, JavaScript, cURL, native API, OpenAI-compatible API, or Anthropic-compatible API flows.

Direct cloud API:

- Host: `https://ollama.com`
- Use `Authorization: Bearer $OLLAMA_API_KEY`.
- Documented examples include `GET /api/tags` and `POST /api/chat`.

Local-only mode:

- Set `OLLAMA_NO_CLOUD=1`, or set `disable_ollama_cloud` in `~/.ollama/server.json`:

```json
{
  "disable_ollama_cloud": true
}
```

Disabling cloud also disables cloud models and web search.

### `POST https://ollama.com/api/web_search`

Performs a web search.

Request fields:

- `query` (required): search query.
- `max_results`: optional, default `5`, maximum `10`.

Response:

- `results`: array of result objects with `title`, `url`, and `content`.

SDK aliases:

- Python: `ollama.web_search(...)`
- JavaScript: `ollama.webSearch(...)`

### `POST https://ollama.com/api/web_fetch`

Fetches a single web page by URL.

Request fields:

- `url` (required): page URL.

Response:

- `title`: page title.
- `content`: extracted page content.
- `links`: discovered links.

SDK aliases:

- Python: `ollama.web_fetch(...)`
- JavaScript: `ollama.webFetch(...)`

## 7. Model Capabilities

### Text Generation

Available through:

- CLI: `ollama run`
- Native API: `/api/generate`
- Native API: `/api/chat`
- OpenAI compatibility: `/v1/chat/completions`, `/v1/completions`, `/v1/responses`
- Anthropic compatibility: `/v1/messages`
- Python and JavaScript SDKs.

### Chat

Chat uses a message array with roles and supports system prompts, multi-turn history, tool messages, images, structured outputs, thinking, streaming, and keep-alive controls.

### Streaming

Streaming is available in native API calls, OpenAI-compatible calls, Anthropic-compatible calls, and SDKs. Native API streaming uses newline-delimited JSON. SDKs return sync or async iterators/generators depending on language and mode.

### Structured Outputs

Ollama supports JSON mode and JSON schema-constrained output.

Native API:

- `format: "json"`
- `format: { ...JSON schema... }`

OpenAI compatibility:

- `response_format`

Best practices from docs:

- Include the schema in the prompt as well as in the `format` field.
- Use Pydantic in Python or Zod in JavaScript for schema reuse and validation.
- Lower temperature, often to `0`, for deterministic structured output.

Important limitation:

- The structured outputs docs state that Ollama Cloud currently does not support structured outputs.

### Thinking

Thinking-capable models can return a separate reasoning trace.

Controls:

- Native API: `think: true`, `think: false`, or `think: "low" | "medium" | "high"`.
- CLI: `--think`, `--think=false`, `--think=low`, `--hidethinking`.
- Interactive CLI: `/set think` and `/set nothink`.
- OpenAI compatibility: `reasoning_effort` or `reasoning.effort`.
- Anthropic compatibility: `thinking`.

Documented thinking model families include Qwen 3, GPT-OSS, DeepSeek-v3.1, and DeepSeek R1. GPT-OSS uses `low`, `medium`, or `high` levels.

### Tool Calling

Tool calling lets a model request function calls and then consume tool results.

Supported flows:

- Single tool call.
- Parallel tool calls.
- Multi-turn agent loop.
- Streaming with tools.
- Python SDK can pass Python functions directly as tools.
- JavaScript SDK can pass JSON-schema tool definitions.
- Native API uses `tools` on `/api/chat` and message role `tool` for results.

Tool definitions use:

- `type: "function"`
- `function.name`
- `function.description`
- `function.parameters` as JSON Schema.

### Vision

Vision-capable models accept images.

Supported paths:

- CLI: pass a local image path in `ollama run` prompts.
- Native generate/chat API: pass base64-encoded images.
- OpenAI compatibility: base64 image content; image URLs are not documented as supported.
- Anthropic compatibility: base64 image content; URL images are not documented as supported.
- Structured outputs can be combined with vision.

### Embeddings

Embeddings are available through:

- CLI: `ollama run embedding-model "text"` or pipe input.
- Native API: `POST /api/embed`.
- OpenAI compatibility: `POST /v1/embeddings`.
- SDKs: `embed`.

The docs recommend embedding models such as `embeddinggemma`, `qwen3-embedding`, and `all-minilm`.

Useful controls:

- Batch input with an array of strings.
- `dimensions` for dimensional truncation.
- `truncate` for overlong inputs.
- Cosine similarity for most semantic search use cases.
- Use the same model for indexing and querying.

### Web-Augmented Workflows

Ollama offers authenticated web search and fetch APIs on `ollama.com`, plus deeper Python/JavaScript integrations. The docs describe using them to build search agents and long-running research tasks.

### Image Generation

OpenAI-compatible `POST /v1/images/generations` is documented as experimental. Local CLI help also exposes experimental image-generation flags on `ollama run`.

## 8. Modelfile Functions

A `Modelfile` is a blueprint for creating and sharing customized models.

Format:

```text
# comment
INSTRUCTION arguments
```

### `FROM` (required)

Defines the base model or source.

Supported patterns:

- Existing Ollama model: `FROM llama3.2`
- Safetensors model directory: `FROM /path/to/safetensors/directory`
- GGUF file: `FROM ./model.gguf`

### `PARAMETER`

Sets model runtime parameters.

Documented parameters:

- `num_ctx`: context window size.
- `repeat_last_n`: how far back to check for repetition.
- `repeat_penalty`: repetition penalty strength.
- `temperature`: randomness.
- `seed`: random seed.
- `stop`: stop sequence; may be specified multiple times.
- `num_predict`: maximum tokens to generate.
- `top_k`: top-K filtering.
- `top_p`: nucleus sampling.
- `min_p`: minimum probability threshold relative to the most likely token.

### `TEMPLATE`

Defines the prompt template sent to the model.

Template variables:

- `{{ .System }}`: system message.
- `{{ .Prompt }}`: user prompt.
- `{{ .Response }}`: assistant response insertion point.

Templates use Go template syntax.

### `SYSTEM`

Sets the system message used by the template.

### `ADAPTER`

Applies a LoRA or QLoRA adapter.

Supported documented inputs:

- Safetensors adapter directory.
- GGUF adapter file.

The adapter should match the base model used to create it.

### `LICENSE`

Embeds the model license text.

### `MESSAGE`

Adds message history examples to steer behavior.

Roles:

- `system`
- `user`
- `assistant`

### `REQUIRES`

Specifies the minimum Ollama version required by the model.

### Importing and Quantizing Models

Ollama can import:

- Safetensors adapters.
- Safetensors full models.
- GGUF models.
- GGUF adapters.

Documented supported model/import families include Llama, Mistral/Mixtral, Gemma, and Phi3 in the import docs.

Quantization:

- `ollama create --quantize q4_K_M mymodel`
- API field: `quantize`
- Documented quantization levels include `q8_0`, `q4_K_S`, and `q4_K_M`.

Model sharing:

- Rename with `ollama cp mymodel username/mymodel`.
- Publish with `ollama push username/mymodel`.
- Others can use `ollama run username/mymodel`.

## 9. Official SDK Functions

The official SDKs are designed around the Ollama REST API.

### Python SDK

Common functions documented by the Python docs/readme and capabilities pages:

- `chat(...)`
- `generate(...)`
- `list()`
- `show(...)`
- `create(...)`
- `copy(...)`
- `delete(...)`
- `pull(...)`
- `push(...)`
- `embed(...)`
- `ps()`
- `web_search(...)`
- `web_fetch(...)`

Client types:

- `Client`: configurable sync client.
- `AsyncClient`: async client.

Other behavior:

- `stream=True` returns a stream/generator.
- Errors raise `ollama.ResponseError`.
- Cloud direct access is configured with `Client(host="https://ollama.com", headers={...})`.

### JavaScript/TypeScript SDK

Common functions documented by the JavaScript README and capabilities pages:

- `ollama.chat(request)`
- `ollama.generate(request)`
- `ollama.pull(request)`
- `ollama.push(request)`
- `ollama.create(request)`
- `ollama.delete(request)`
- `ollama.copy(request)`
- `ollama.list()`
- `ollama.show(request)`
- `ollama.embed(request)`
- `ollama.webSearch(request)`
- `ollama.webFetch(request)`
- `ollama.ps()`
- `ollama.version()`
- `ollama.abort()`

Client configuration:

- `new Ollama({ host, fetch, headers })`
- Browser import: `ollama/browser`
- `stream: true` returns an `AsyncGenerator`.

## 10. Server Configuration and Environment Variables

Server variables from docs and local CLI help:

- `OLLAMA_HOST`: server bind address, default commonly `127.0.0.1:11434`.
- `OLLAMA_MODELS`: model storage path.
- `OLLAMA_ORIGINS`: comma-separated allowed CORS origins.
- `OLLAMA_CONTEXT_LENGTH`: default context length unless otherwise specified.
- `OLLAMA_KEEP_ALIVE`: default duration models stay loaded.
- `OLLAMA_MAX_LOADED_MODELS`: maximum concurrently loaded models.
- `OLLAMA_NUM_PARALLEL`: maximum parallel requests per model.
- `OLLAMA_MAX_QUEUE`: queued request limit before rejecting overload.
- `OLLAMA_MAX_TRANSFER_STREAMS`: maximum parallel transfer streams for Safetensors pulls/pushes.
- `OLLAMA_NO_CLOUD`: disable cloud features and web search.
- `OLLAMA_DEBUG`: additional debug output.
- `OLLAMA_NOPRUNE`: do not prune model blobs on startup.
- `OLLAMA_SCHED_SPREAD`: schedule models across all GPUs.
- `OLLAMA_FLASH_ATTENTION`: enable Flash Attention.
- `OLLAMA_KV_CACHE_TYPE`: K/V cache type, documented values include `f16`, `q8_0`, and `q4_0`.
- `OLLAMA_LLM_LIBRARY`: bypass LLM library autodetection.
- `OLLAMA_GPU_OVERHEAD`: reserve VRAM per GPU in bytes.
- `OLLAMA_LOAD_TIMEOUT`: model load stall timeout.

CLI interaction variables:

- `OLLAMA_EDITOR`: editor for interactive prompt editing.
- `OLLAMA_NOHISTORY`: do not preserve readline history.

Network/proxy:

- `HTTPS_PROXY`: proxy for model pulls.
- Avoid `HTTP_PROXY` for Ollama pulls, because model pulls use HTTPS and `HTTP_PROXY` can interfere with client-server connections.

GPU selection and hardware variables:

- `CUDA_VISIBLE_DEVICES`: restrict Nvidia GPUs or force CPU with invalid ID.
- `ROCR_VISIBLE_DEVICES`: restrict AMD ROCm GPUs.
- `HSA_OVERRIDE_GFX_VERSION`: AMD ROCm target override.
- `GGML_VK_VISIBLE_DEVICES`: select Vulkan GPUs or disable with `-1`.
- `OLLAMA_VULKAN=1`: enable experimental Vulkan support.
- `JETSON_JETPACK=5` or `6`: select JetPack version in Docker on Jetson.

Configuration locations and behavior:

- Model storage defaults:
  - macOS: `~/.ollama/models`
  - Linux: `/usr/share/ollama/.ollama/models`
  - Windows: `C:\Users\%username%\.ollama\models`
- Ollama public key defaults:
  - macOS: `~/.ollama/id_ed25519.pub`
  - Linux: `/usr/share/ollama/.ollama/id_ed25519.pub`
  - Windows: `C:\Users\<username>\.ollama\id_ed25519.pub`
- Disable cloud with `~/.ollama/server.json`:

```json
{
  "disable_ollama_cloud": true
}
```

## 11. Context Length, Memory, and Concurrency

Context length is the number of tokens available to the model in memory.

The context length docs state defaults are based on VRAM:

- Less than 24 GiB VRAM: 4k context.
- 24 to 48 GiB VRAM: 32k context.
- 48 GiB VRAM or more: 256k context.

Cloud models use their maximum context length by default.

Ways to set context:

- App settings slider.
- `OLLAMA_CONTEXT_LENGTH=64000 ollama serve`
- API `options.num_ctx`.
- Modelfile `PARAMETER num_ctx`.

Tasks such as web search, agents, and coding tools should generally use at least 64k tokens when hardware allows.

Concurrency behavior:

- Ollama can load multiple models concurrently if memory/VRAM allows.
- A single model can process parallel requests if memory allows.
- Parallel requests multiply context memory requirements: required RAM scales roughly by `OLLAMA_NUM_PARALLEL * OLLAMA_CONTEXT_LENGTH`.
- Busy servers queue requests until `OLLAMA_MAX_QUEUE`, then reject excess work.

Model residency:

- Default keep-alive is documented as 5 minutes in the FAQ.
- Use `ollama stop MODEL` to unload.
- Use API `keep_alive` to control per-request residency.
- `keep_alive: -1` keeps a model loaded.
- `keep_alive: 0` unloads immediately.

## 12. Deployment and Hardware Support

### Platforms

Ollama has docs for:

- macOS.
- Linux.
- Windows.
- Docker.

### Docker

CPU-only:

```text
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

Nvidia GPU:

```text
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

AMD GPU:

```text
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:rocm
```

Vulkan:

```text
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 -e OLLAMA_VULKAN=1 --name ollama ollama/ollama
```

### Hardware

Documented acceleration paths:

- Nvidia GPUs with compute capability 5.0+ and driver 531+.
- AMD Radeon/Instinct/Ryzen AI via ROCm on supported platforms.
- Apple GPUs via Metal.
- Experimental Vulkan support on Windows and Linux.

Operational features:

- `ollama ps` shows whether models are loaded on CPU, GPU, or split.
- Multi-GPU scheduling loads a model on one GPU when it fits, otherwise spreads across GPUs.
- Flash Attention can reduce memory usage for larger context windows.
- Quantized K/V cache can reduce context memory with possible precision tradeoffs.

## 13. Integrations

Official docs list integrations across these categories.

Coding agents:

- Claude Code.
- Codex CLI.
- Copilot CLI.
- OpenCode.
- Droid.
- Goose.
- Pi.
- Pool.

Assistants:

- OpenClaw.
- Hermes Agent.
- NemoClaw.

IDEs and editors:

- VS Code.
- Cline.
- Roo Code.
- JetBrains.
- Xcode.
- Zed.

Chat/RAG:

- Onyx.

Automation:

- n8n.

Notebooks:

- marimo.

Integration mechanisms vary:

- Some are launched through `ollama launch`.
- Some are configured manually through OpenAI-compatible, Anthropic-compatible, or native Ollama API settings.
- Some cloud/coding tools recommend large context windows, often at least 64k tokens.

## 14. Source Links Reviewed

Primary source index and specs:

- Official docs index: <https://docs.ollama.com/llms.txt>
- OpenAPI spec: <https://docs.ollama.com/openapi.yaml>
- Main docs: <https://docs.ollama.com/>
- GitHub repository README: <https://github.com/ollama/ollama>

Key docs pages:

- CLI reference: <https://docs.ollama.com/cli>
- API introduction: <https://docs.ollama.com/api/introduction>
- Generate: <https://docs.ollama.com/api/generate>
- Chat: <https://docs.ollama.com/api/chat>
- Embeddings API: <https://docs.ollama.com/api/embed>
- Model management APIs: <https://docs.ollama.com/api/tags>, <https://docs.ollama.com/api/ps>, <https://docs.ollama.com/api/create>, <https://docs.ollama.com/api-reference/show-model-details>, <https://docs.ollama.com/api/copy>, <https://docs.ollama.com/api/pull>, <https://docs.ollama.com/api/push>, <https://docs.ollama.com/api/delete>, <https://docs.ollama.com/api-reference/get-version>
- Streaming: <https://docs.ollama.com/api/streaming>
- Usage metrics: <https://docs.ollama.com/api/usage>
- Errors: <https://docs.ollama.com/api/errors>
- OpenAI compatibility: <https://docs.ollama.com/api/openai-compatibility>
- Anthropic compatibility: <https://docs.ollama.com/api/anthropic-compatibility>
- Authentication: <https://docs.ollama.com/api/authentication>
- Cloud: <https://docs.ollama.com/cloud>
- Web search/fetch: <https://docs.ollama.com/capabilities/web-search>
- Structured outputs: <https://docs.ollama.com/capabilities/structured-outputs>
- Thinking: <https://docs.ollama.com/capabilities/thinking>
- Tool calling: <https://docs.ollama.com/capabilities/tool-calling>
- Vision: <https://docs.ollama.com/capabilities/vision>
- Embeddings capability: <https://docs.ollama.com/capabilities/embeddings>
- Context length: <https://docs.ollama.com/context-length>
- Modelfile reference: <https://docs.ollama.com/modelfile>
- Importing models: <https://docs.ollama.com/import>
- Docker: <https://docs.ollama.com/docker>
- Hardware support: <https://docs.ollama.com/gpu>
- FAQ: <https://docs.ollama.com/faq>
- Integrations overview: <https://docs.ollama.com/integrations>
- Python SDK: <https://github.com/ollama/ollama-python>
- JavaScript SDK: <https://github.com/ollama/ollama-js>
