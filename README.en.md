# RWKV-Agent

> A local-first RWKV workspace agent. Go owns the Conversation, Session, and Agent
> transactions; a standalone `librwkv_agent_runtime.dylib` performs inference through
> a pinned RWKV Mobile tokenizer/sampler and the MLX FFI. The runtime does not depend
> on Python, PyTorch, an HTTP service, or external processes.
>
> The CLI, TUI, desktop app, and browser service share the same public `api` package.
>
> [中文版](README.md)

## Current Status

- **Usable**: source builds on Apple Silicon, macOS 15+ — CLI/TUI, the Wails V3 desktop app, and a headless server.
- **Experimental**: the read-only Agent framework and evaluation harness (`rwkv-agent-eval-v17`).
- **Platforms**: Windows has no usable entry point yet. Linux `-tags server` builds are verified in CI (remote-provider scenarios); the local MLX model and desktop window are not available there yet.
- **Distribution**: the technical packaging chain works, but upstream licenses must be confirmed and a project license chosen before public distribution.

Feature highlights:

- CLI: `convert` / `run` / `agent` / `agent-eval` / `concurrent` / `bench`
- Inference: direct `.pth` mmap loading, explicit MLX conversion, single-model scheduler, continuous batching (up to 8 active Sessions)
- Sessions: immutable revisions with an atomic `CURRENT` pointer; the transcript is the source of truth
- Agent: read-only workspace tools, `calculator`/`data_query`/`datetime`, optional Brave/Tavily web tools, and `spawn_agents` delegation
- Remote: native `rwkv_lightning` continuation; OpenAI-compatible Chat Completions behind an optional build tag
- Desktop app: Wails V3 + React + Material Design 3, persistent conversations, tool trajectories, web retries
- Evaluation: 5 built-in suites with reproducible trace artifacts

For a first run, follow [macOS from scratch](docs/getting-started-macos.md) (in Chinese).

## Table of Contents

1. [Desktop App](#1-desktop-app)
2. [Quick Start and Build](#2-quick-start-and-build)
3. [CLI Command Overview](#3-cli-command-overview)
4. [Loading and Converting Models](#4-loading-and-converting-models)
5. [REPL and Sessions](#5-repl-and-sessions)
6. [Agent Framework](#6-agent-framework)
7. [Remote Providers](#7-remote-providers)
8. [Agent Evaluation](#8-agent-evaluation)
9. [Concurrency Dashboard](#9-concurrency-dashboard)
10. [Tests and CI](#10-tests-and-ci)
11. [Project Layout](#11-project-layout)
12. [Documentation Map](#12-documentation-map)
13. [Distribution and License](#13-distribution-and-license)

## 1. Desktop App

The repository includes a Wails V3 beta + TypeScript + React + Vite application with a
Material Design 3 frontend. It uses the same public `api` package as the CLI and TUI
and supports both a native macOS window and a Wails server build that starts without
opening a window:

```sh
./scripts/build-app.sh
open -n "./dist/RWKV Agent.app" --args --workspace "$(pwd)"

# Browser-only mode
./dist/rwkv-app-server --host 127.0.0.1 --port 8080
```

Building the app additionally requires Node.js and npm (CI pins Node 24). Key features:

- Configures a local RWKV model (`.pth` or MLX directory) or a remote API (RWKV
  continuation / OpenAI-compatible), displays model status, and lists remote models via
  `GET /v1/models`.
- Persists conversations and recent projects: the complete committed transcript
  (including tool calls and results) is stored per workspace and restored on relaunch.
  Settings and credentials are stored as plaintext JSON in platform XDG/Known Folder
  locations; status events never carry secrets.
- Every message keeps a tool trajectory: call steps, arguments, status, errors, subagent
  details, and per-attempt web retries (429/5xx, up to 5 attempts, exponential backoff,
  honoring `Retry-After`).
- Supports arbitrary HTTP headers (for example Cloudflare Access) and macOS system
  proxy settings.

See [docs/app.md](docs/app.md) for storage details, setup, and development commands.

## 2. Quick Start and Build

Requirements:

- Apple Silicon Mac, macOS 15+
- Xcode (Swift and Metal toolchains)
- CMake 3.25+ and Ninja
- Go 1.26+
- Node.js 24 (only for the desktop app)
- An RWKV-7 `.pth` checkpoint, or a converted MLX safetensors model directory

Initialize the pinned upstream dependency, then check and build:

```sh
git submodule update --init --recursive

brew install cmake ninja go   # CLI dependencies

./scripts/build-macos.sh --check
./scripts/build-macos.sh
```

The default artifacts include only the local RWKV and plain continuation providers and
do not compile or link the OpenAI SDK. Use the optional build when calling upstream
Chat Completions; the pure-Go builds use the same build tag:

```sh
./scripts/build-macos.sh --with-chat-completions
go build ./cmd/rwkv-cli
go build -tags chatcompletions ./cmd/rwkv-cli
```

The build script pins `arm64` and `MACOSX_DEPLOYMENT_TARGET=15.0`, builds the MLX FFI
with direct PTH entry from a pinned revision, and validates the dylib, rpath, Metal
resource, deployment target, and CLI help smoke test. Missing submodules are
initialized automatically. The first build fetches MLX Swift dependencies and later
builds reuse the `build/` cache. Outputs:

```text
dist/
├── rwkv-cli
├── librwkv_agent_runtime.dylib
├── build-manifest.json
├── assets/
│   └── rwkv_vocab_v20230424.txt
└── mlx-swift_Cmlx.bundle/
    └── Contents/Resources/default.metallib
```

`scripts/build-mlx.sh` remains as a compatibility entry point that forwards to
`build-macos.sh`. Installation, running, updates, and troubleshooting are documented in
[docs/getting-started-macos.md](docs/getting-started-macos.md).

## 3. CLI Command Overview

| Command | Purpose |
| --- | --- |
| `convert` | Reads a PyTorch ZIP/pickle checkpoint and writes MLX safetensors (no Python) |
| `run` | Single-turn generation or a multi-turn REPL for `.pth` and MLX directories |
| `agent` | Local-first read-only workspace agent (TUI/plain) |
| `agent-eval` | Fixed-case agent evaluation producing run/trace/summary artifacts |
| `concurrent` | 1–8 concurrent generations with a pick-and-continue dashboard |
| `bench` | `concurrent` rendered as plain output, for scripts and CI |

```text
rwkv-cli convert --input <RWKV .pth> --output <MLX model directory>
rwkv-cli run --model <RWKV .pth or MLX directory> [--prompt <text> | --session <bundle>]
rwkv-cli agent --model <path or remote model ID> [--prompt <task>] [--ui auto|tui|plain]
rwkv-cli agent-eval --model <path or remote model ID> [--suite boundary|smoke|assistant|primitive-orig30|primitive-feedback30]
rwkv-cli concurrent --model <RWKV .pth or MLX directory> [--concurrency 1..8]
rwkv-cli bench --model <RWKV .pth or MLX directory> [--concurrency 1..8]
```

## 4. Loading and Converting Models

### Running `.pth` directly (recommended)

Running no longer requires converting the model first:

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

The runtime mmaps the original `.pth` and loads tensors directly into MLX without
writing a second full copy of the weights. The first load creates a `.rwkvi` metadata
index (usually tens to hundreds of KB) under
`~/Library/Caches/RWKV-Agent/pth-index/v1/`; later loads skip pickle metadata parsing
via the index. The cache key binds the file's absolute path, and the index validates
file size and modification time, so a changed checkpoint is detected and rebuilt in
place. `.pth` models use the bundled RWKV World tokenizer by default; pass
`--tokenizer` only for a custom vocabulary.

### Explicit conversion (optional)

`convert` is kept for deployment flows that need standalone MLX safetensors:

```sh
./dist/rwkv-cli convert \
  --input /absolute/path/to/rwkv7-model.pth \
  --output /absolute/path/to/rwkv7-model-mlx
```

Output defaults to BF16; `--precision fp16` and `--precision fp32` are also available.
An existing destination directory is rejected unless `--overwrite` is passed. The
result contains `config.json`, `model.safetensors`, and
`rwkv_vocab_v20230424.txt`.

## 5. REPL and Sessions

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

Key flags:

```text
--backend auto|rwkvmobile        --provider auto|mlx
--tokenizer <file>               --session <bundle>
--prompt <single turn>           --max-tokens <n>
--temperature <f>                --top-k <n> --top-p <f>
--presence-penalty <f>           --frequency-penalty <f> --penalty-decay <f>
--thinking off|fast|full         --native-state auto|off|required
--autosave
```

The default is the official RWKV G1 chat template `User: ...\n\nAssistant:`.
`--thinking fast` strictly pre-fills `Assistant: <think></think` and continues;
`--thinking full` strictly pre-fills `Assistant: <think`. The trailing `>` is
**deliberately not written into the prompt** and is left for the model to generate:
the RWKV tokenizer merges `>` with the following text, so writing it would start
generation from a token boundary that never occurred in training. The deprecated
`--reasoning[=true|false]` remains compatible with `fast/off`. Do not write pseudo
special tokens such as `<|bos|>` into prompts.

Default decoding follows the current G1 model card chat recommendations:
`temperature=1`, `top-p=0.5`, `presence-penalty=2`, `frequency-penalty=0.1`,
`penalty-decay=0.99`. Model loading shows a lightweight spinner; single-turn generation
and the REPL do not enter the alternate screen, so answers remain selectable, copyable,
and redirectable plain text.

REPL commands:

```text
/state   /history   /save [path]   /load <path>   /reset   /new   /help   /exit
```

Each turn is generated against a candidate transcript and is committed only after the
complete output aligns with the native prefix. Cancellation, terminal write failures,
or native errors never write a partial user/assistant message. During generation the
first `Ctrl-C` cancels the current turn and returns to the prompt; an idle `Ctrl-C`
exits. `SIGTERM` requests cancellation first and then shuts down in Session, Model,
Runtime order.

Sessions use immutable revisions and an atomic `CURRENT` pointer:

```text
demo.rwkv-session/
├── CURRENT
└── revisions/
    └── sha256-.../
        ├── session.json
        ├── transcript.jsonl
        └── state.bin
```

The transcript is the source of truth; `state.bin` is only a codec/size/prefix/checksum
validated MLX State acceleration snapshot. A missing or invalid snapshot is rebuilt by
replaying the transcript. Incompatible models, tokenizers, Initial States, or
non-migratable prompt profiles are rejected. `/load` validates and recovers with a
temporary Conversation and only replaces the current session on success. Old prompt
profiles on the same `rwkv-g1-chat` template are upgraded safely: without an explicit
`--thinking`, the session's original thinking mode is inherited; explicit conflicts or
model/tokenizer mismatches are still rejected. Autosave after migration writes a new
revision and never rewrites the old one.

## 6. Agent Framework

`agent` exercises the vertical local-first agent path: the model lists files, reads
text, searches literal strings, and processes structured data inside a designated
workspace, then answers from real tool results. The plain `agent` registers workspace
tools plus provider-independent `calculator`, `data_query`, and `datetime`. The
mock `weather`, `nearest_transit`, `transit_hours`, and `fx_convert` tools are only
registered in the repeatable `assistant` evaluation suite. Default tools have no
write, command-execution, or real-network capability.

The product default is the G1i-trained Markdown/function transcript: tools are listed
under `System: Tools:`, a tool call is a JSON fenced code block continued after
`Assistant:`, and results are returned as `User: Function output:`. The `inspect`
route ends with a lightweight `submit` that commits the final visible answer and stops
immediately; the `respond` route answers directly. The legacy
`rwkv-g1i-envelope-v1` XML protocol remains available as `--agent-protocol xml` for
A/B compatibility.

Progressive tool exposure is enabled by default: a short Router that never sees tool
schemas first selects zero to two capability bundles among `workspace`, `compute`,
`web`, and `delegate`. `respond` answers without tools; `inspect:BUNDLE[+BUNDLE]`
exposes only the selected bundles' schemas. When the current tools are insufficient,
the model can call the control tool `load_tools` to load another enabled bundle;
naming a hidden tool is rejected by the Harness. `--progressive-tools=false` restores
the fixed full catalog.

```sh
./dist/rwkv-cli agent \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

Interactive terminals enter the full-screen Agent TUI. After the first turn you can
ask follow-ups; the Harness carries the committed user/assistant/tool transcript into
later stages. `/new` or `/reset` clears the multi-turn session and `/exit` quits;
`Ctrl-C` cancels the current turn while running and exits when idle. Passing
`--prompt` submits the first turn automatically; scripts, pipes, and CI automatically
use the plain renderer:

```sh
./dist/rwkv-cli agent \
  --ui plain \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project \
  --prompt "Read README.md and docs, then summarize what is done and what comes next"
```

Common flags:

```text
--max-steps <2..20>                  --progressive-tools[=true|false]
--agent-protocol markdown|xml        --route-max-tokens <n>
--decision-max-tokens <n>            --max-tokens <n>
--workspace <directory>              --thinking off|fast|full
--ui auto|tui|plain                  --prompt <task>
--web                                --subagents
--few-shot                            --route-stage
--trace-prompt-bytes <n>             --duplicate-replay-limit <n>
--duplicate-rescue-threshold <n>     --same-tool-rescue-limit <n>
--brave-endpoint <url>               --tavily-endpoint <url>
--max-active-batch <1..8>            --subagent-max-parallel <2..8>
--subagent-max-steps <n>             --subagent-timeout <duration>
--remote-batch-wait <duration>
```

The Agent uses deterministic decoding by default: `temperature=1`, `top-k=1`,
`top-p=1`, zero presence/frequency penalties, and `penalty-decay=1`. The Router
generates at most 48 tokens, the first tool selection at most 96 tokens, the final
answer at most 1024 tokens, with a limit of 6 Agent steps (the Router is counted
separately). `--few-shot` is an off-by-default experiment that injects example
trajectories at initial decision, after a successful tool result, and at forced-answer
time; measured runs showed strong prompt anchoring, so it is kept only for experiments
and reproduction. `--route-stage` is also off by default and kept as an early scaffold
for small models.

### Optional Web and Subagents

`web_search` (Brave Search) and `web_fetch` (Tavily Extract, up to 4 pages) are
registered only when `--web` is passed and both API keys are provided:

```sh
export BRAVE_API_KEY='...'
export TAVILY_API_KEY='...'

./dist/rwkv-cli agent \
  --web \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

The web providers retry 429/5xx automatically (up to 5 attempts, exponential backoff
from 500 ms capped at 5 s, honoring `Retry-After`) and record each retry in the tool
trajectory events.

`spawn_agents` runs 2–8 independent tasks concurrently, each with its own Session,
State, and transcript, and returns results in input order. Child Agents inherit
workspace, compute, and web capabilities but not `delegate`, so they cannot fan out
recursively. All-failed batches fail the whole tool call; partial success keeps
successful outputs plus per-item errors. Local MLX advances independent Sessions via
continuous batching; RWKV Lightning coalesces compatible continuations into one
`contents[]` request within the aggregation window; Chat Completions issues concurrent
HTTP requests. `continuation.Generator` remains single-request and transport-neutral —
batching only exists at the Provider/runtime layer.

```sh
./dist/rwkv-cli agent \
  --subagents \
  --max-active-batch 4 \
  --subagent-max-parallel 4 \
  --subagent-max-steps 4 \
  --subagent-timeout 2m \
  --remote-batch-wait 10ms \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

### Safety and Recovery

Every tool path must be relative to `--workspace`; absolute paths, `..` traversal, and
symlinks pointing outside the workspace are rejected. Single-file reads are limited to
64 KiB, and search skips `.git`, `build`, `dist`, and `node_modules`. After each tool
attempt the Runner keeps the full assistant/function-output trajectory and lets the
model call a different tool, or `submit` once the evidence is sufficient. Failures
return deterministic recovery hints, and the exact same call is never executed twice.
After duplicate or same-tool-streak thresholds the Runner switches to a submit-only
rescue mode; when evidence is insufficient, the submission must state its limitations.
The whole turn commits transactionally only after `submit` succeeds; generation,
protocol, or step failures roll the turn back. Set `RWKV_AGENT_DEBUG=1` to print raw
model steps when diagnosing protocol errors (it may include local file content and is
off by default).

The CLI `agent` supports in-process multi-turn interaction but does not yet persist its
own transcripts; the desktop app persists conversations and history through the public
`api`. Context compaction, write-file approval, and command execution remain out of
scope. Protocol boundaries, tool permissions, and the state machine are described in
[docs/continuation-and-agent-protocol.md](docs/continuation-and-agent-protocol.md) and
[docs/agent-harness-milestone.md](docs/agent-harness-milestone.md).

## 7. Remote Providers

### rwkv_lightning native continuation

```sh
# Only when the service enables a request-body password: export RWKV_API_PASSWORD='...'
export RWKV_CF_ACCESS_CLIENT_ID='...'      # required for Cloudflare Access deployments
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

./dist/rwkv-cli agent \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --workspace /absolute/path/to/project
```

Notes:

- `--api-url` is the full endpoint; no OpenAI path is appended. The client sends
  `contents`, so `/v1/batch/completions`, `/v1/chat/completions`, and
  `/big_batch/completions` may all provide the semantics (check `GET /openapi.json`).
- `stop_tokens` is a **decoded-text string array** (not integer token IDs). The
  default `--api-stop-tokens text` forwards the current protocol's stop sequences;
  the `cuda` preset serves `rwkv_lightning_cuda` deployments that require integer token
  IDs; `none` omits the field, and `eos` or a comma-separated integer list keep the old
  form.
- `--api-stream` defaults to `true` (SSE, token by token); `--api-stream=false` requests
  one buffered JSON response, which is more reliable on deployments with unstable SSE
  but removes token-level output for interactive `agent` runs.
- With `top-k=1`, `rwkv_lightning` takes the argmax directly, so temperature and top-p
  do not participate in random sampling.
- The password defaults to the `RWKV_API_PASSWORD` environment variable
  (`--api-password-env` changes it). `--api-header-env` is repeatable; credentials never
  appear in command lines or config files. Remote models receive the Agent-composed
  prompt, which may include local file fragments the model explicitly read.

### OpenAI-compatible Chat Completions

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --workspace /absolute/path/to/project \
  --prompt "Read the README and summarize the project"
```

`chat-completions` is implemented with the official `github.com/openai/openai-go/v3`
SDK and isolated from default artifacts by the `chatcompletions` build tag. The default
`--chat-prompt-mode native-chat` sends real system/user/assistant messages and native
`tools`; `wrapped-continuation` puts the fully rendered continuation prompt into one
user message as a fallback for services without native tools. Both modes use
non-streaming responses and always send `parallel_tool_calls: false`. The output budget
defaults to the currently documented `max_completion_tokens`; services that still
accept only the deprecated field can use `--chat-token-limit-field max-tokens`.

For upstreams that enable hidden reasoning by default and share the output budget with
the visible text (for example DeepSeek V4-Flash), disable upstream thinking explicitly:

```sh
export DEEPSEEK_API_KEY='...'

./dist/rwkv-cli agent \
  --completion chat-completions \
  --api-url https://api.deepseek.com/v1/chat/completions \
  --api-key-env DEEPSEEK_API_KEY \
  --model deepseek-v4-flash \
  --chat-thinking disabled \
  --chat-prompt-mode native-chat \
  --chat-token-limit-field max-tokens \
  --workspace /absolute/path/to/project \
  --prompt "Read the README and summarize the project"
```

`--chat-thinking auto` (the default) sends no vendor-specific field; `disabled` /
`enabled` send the `thinking: {"type":"..."}` extension. This is independent of
`--thinking off|fast|full`, which controls the internal RWKV prompt. The bearer token
defaults to `OPENAI_API_KEY` (`--api-key-env` changes it); an explicit `Authorization`
header overrides the bearer token.

Optional real-endpoint integration tests are skipped by default:

```sh
export CHAT_COMPLETIONS_INTEGRATION_URL=https://api.deepseek.com/v1/chat/completions
export CHAT_COMPLETIONS_INTEGRATION_MODEL=deepseek-v4-flash
export CHAT_COMPLETIONS_INTEGRATION_API_KEY='...'
export CHAT_COMPLETIONS_INTEGRATION_THINKING=disabled
export CHAT_COMPLETIONS_INTEGRATION_PROMPT_MODE=native-chat
export CHAT_COMPLETIONS_INTEGRATION_TOKEN_LIMIT_FIELD=max-tokens
go test -tags chatcompletions ./internal/continuation/chatcompletions \
  -run 'TestRemoteChatCompletions(NativeTool)?Integration' -v
```

See [docs/continuation-and-agent-protocol.md](docs/continuation-and-agent-protocol.md)
for the complete mapping details.

## 8. Agent Evaluation

`agent-eval` runs fixed cases with exactly the same Router, prompt, sampling, and
Runner parameters as `agent`:

| Suite | Contents |
| --- | --- |
| `boundary` (default) | 18 read-only cases adapted from [marty1885/primitive-bench](https://github.com/marty1885/primitive-bench) |
| `smoke` | 10 protocol and safety contract regressions |
| `assistant` | 6 weather/transit, cost/FX, provider-unavailable, single-intent, and ambiguous follow-up cases |
| `primitive-orig30` | The upstream `agent_cases_orig30` 30-case pinned snapshot (legacy name `primitive` still accepted) |
| `primitive-feedback30` | The curated 30 cases from the upstream `agent_cases_feedback` at the same commit |

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite boundary \
  --output runs/local-13b-boundary
```

Every case gets an isolated temporary workspace; local inference creates a fresh
Session per case. Use repeatable `--case` flags for subsets, `--cases` for versioned
`schema_version: 3` JSON case files or a trusted Primitive Bench directory,
`--case-timeout` for per-case timeouts, and `--case-parallelism` for concurrency.
`--cases` and `--suite` are mutually exclusive; the output directory must not exist.

Remote evaluation reuses the same entry point:

```sh
./dist/rwkv-cli agent-eval \
  --suite smoke \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --case read_exact_file \
  --case multi_turn_memory \
  --output runs/remote-13b-smoke
```

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent-eval \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --suite primitive-orig30 \
  --output runs/primitive-orig30-external
```

### Primitive Bench dual track

The repository embeds a pinned snapshot of
[`RWKV-Vibe/rwkv-Primitive-Bench`](https://github.com/RWKV-Vibe/rwkv-Primitive-Bench)
at commit `416b073d2c5442ae34bfbf8a3b84ed414b5b85ff`. The JSON is embedded in the CLI,
so local, CI, and external-model evaluations use identical prompts, fixtures, and
scoring contracts without cloning the upstream repository.

Two explicit tool profiles:

- `upstream-compatible` (default) keeps the full per-case upstream tool catalog,
  including `run_lua`, for protocol and Harness cross-comparison.
- `go-native` keeps the same cases, fixtures, `max_turns`, and scorer but replaces
  `run_lua` (where the case provides it) with RWKV-Agent's `calculator` and
  `data_query`, measuring the real Go Agent product without requiring Lua.

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite primitive-orig30 \
  --primitive-profile go-native \
  --output runs/primitive-orig30-local
```

`rwkv_lightning_cuda` deployments require integer `stop_tokens`; the
`--api-stop-tokens cuda` preset keeps the same Harness working. Extra HTTP headers are
read only from environment variables and never written to artifacts. Primitive suites
use each case's original `max_turns` (6–22) and a 1024-token tool-call budget;
`run.json` records the actual profile in `manifest.harness.tool_profile` so the two
tracks cannot be conflated.

Each run atomically writes three files:

- `run.json`: exact case definitions, model fingerprint (when local), Harness/protocol
  versions, prompt configuration, sampling parameters, and runtime environment.
- `trace.jsonl`: raw continuation requests/outputs, usage, phases, Runner events, and
  tool results; passwords and authentication headers are not recorded.
- `summary.json`: per-case/turn failure reasons and answer, route, protocol,
  exact/required/forbidden-tool scoring.

Failing cases still write artifacts, then the command exits non-zero. The default
output is a UTC-timestamped `runs/agent-eval-*` directory.

### Current Baselines

- Primitive `upstream-compatible`: effective v12 baseline 13/30 (7.2B, with one
  network-failed case re-run); the native-G1i protocol branch reached 17/30, versus the
  upstream official archive of 20/30 on the same model.
- Primitive `go-native` (greedy `top-k=1`): official score 23/30 (stable pass set in
  v19/v20); the v21b single run reached 24/30, with `config_precedence_resolve` an
  unstable boundary case (roughly 25–30% pass rate).
- `boundary`/smoke history, v8/v9 fix verification, and failure analysis live in
  [docs/evaluations/](docs/evaluations/).

The complete v12 baseline, v13–v21 evolution, reproduction commands, and policy notes
are in
[docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md).

## 9. Concurrency Dashboard

`concurrent` creates multiple Sessions on one model instance and lets the native
scheduler merge single-token decodes:

```sh
./dist/rwkv-cli concurrent \
  --model /absolute/path/to/rwkv7-model.pth \
  --concurrency 8 \
  --max-tokens 64 \
  --concurrent-prompt "Introduce RWKV in one sentence"
```

On interactive terminals the default is a live dashboard (2×4 or 4×2 panes, degrading
gracefully on narrow terminals) whose header/footer show the provider, native batch,
and aggregate tok/s. After the initial 8 runs complete, click a pane to keep chatting;
this reuses that pane's original `Conversation` and native State rather than
reconstructing a session from rendered text. Render modes:

```text
--ui auto    TUI when the terminal is interactive, otherwise plain (default)
--ui tui     force the TUI; error out clearly if the terminal is insufficient
--ui plain   stable plain-text output for pipes, CI, and scripts
```

`bench` is the `--ui plain` alias of `concurrent`. Dashboard shortcuts: `q`/`Esc`
quit, `Tab`/arrow keys switch panes, `y` copies, `r` reruns, click or `Enter` selects
a pane to continue. Exiting the alternate screen prints one
`Concurrent batch complete: ...` summary line.

All windows receive the same user prompt and decoding parameters, differing only by
seed `42 + session_index`; session numbers are UI-only and never enter the model input.
Greedy `--top-k 1` decoding should therefore produce 8 identical results, while
removing `--top-k 1` yields normal sampling variation. Each Session's callback,
sampler, tokens, cancellation flag, and State are isolated. The MLX FFI supports 16
physical State slots; the CLI currently exposes up to 8 active batch slots with a
bounded FIFO queue for extra requests. For screen recordings, use a terminal of at
least `120×40` cells (`160×24` or wider switches to four columns): capture the
dashboard during generation, then demonstrate pick-and-continue after completion.

## 10. Tests and CI

Without a real model:

```sh
go test ./...
go test -race ./...
./scripts/test-macos-native.sh
```

Go tests cover the 8-way runner, selected-Conversation continuation with cancel
rollback, ANSI-free plain output, CJK/emoji cell widths, responsive layouts, and real
PTY alternate-screen, resize, mouse pick-and-continue, `q` global cancel, and terminal
restore. `test-macos-native.sh` additionally builds an AddressSanitizer variant and
runs the C ABI lifecycle test.

With a converted model:

```sh
RWKV_TEST_MODEL=/absolute/path/to/mlx-model \
./scripts/test-macos-real-model.sh
```

With a `.pth` directly:

```sh
RWKV_TEST_PTH=/absolute/path/to/rwkv7-model.pth \
./scripts/test-macos-real-model.sh
```

The real-model script covers single-turn generation, 8-way greedy State isolation,
4-way cancellation, saving, native State restore, and transcript replay after removing
`state.bin`.

GitHub Actions (`.github/workflows/ci.yml`) runs two jobs:

- Go: race tests for `api/...`, `internal/...`, `cmd/rwkv-cli/...`, plus
  `CGO_ENABLED=0 go build -tags server ./...` and vet to verify the Linux headless
  build.
- Frontend: Node 24, `npm ci`, and `npm test`.

## 11. Project Layout

```text
api/                  Public Agent API shared by CLI/TUI/desktop/browser clients
cmd/rwkv-cli/         CLI and TUI entry point
cmd/rwkv-app/         Wails V3 desktop app (Go backend + React/MD3 frontend)
internal/
  agent/              Agent Harness, progressive tools, tool implementations
  agent/eval/         Evaluation suites and embedded Primitive Bench snapshots
  appstorage/         XDG/Known Folder persistence for the desktop app
  cli/                Command implementations and TUI
  continuation/       Generator abstraction; local/rwkvlightning/chatcompletions adapters
  conversation/       Transcript, revisions, and session bundles
  inference/          Inference core, backend abstraction, scheduling
  native/             MLX FFI, converter, rwkvmobile backend
docs/                 Getting-started, design, protocol, evaluation, and archive docs
native/               C ABI runtime and FFI projects (librwkv_agent_runtime)
scripts/              Build and test scripts
third_party/rwkv-mobile  Pinned tokenizer/sampler upstream (submodule)
archive/              Archived evaluation baselines
```

## 12. Documentation Map

| Category | Documents |
| --- | --- |
| Getting started | [macOS from scratch](docs/getting-started-macos.md) · [Desktop app](docs/app.md) |
| Design | [Inference core design](docs/inference-core-design.md) · [Direct PTH loading](docs/direct-pth-loading.md) |
| Agent | [Continuation and Agent protocol](docs/continuation-and-agent-protocol.md) · [Harness milestone](docs/agent-harness-milestone.md) |
| Evaluations | [docs/evaluations/](docs/evaluations/) (v12 baseline and v13–v21 evolution, API 13B reports, P0 landing report) |
| Reports | [docs/reports/](docs/reports/) (Harness-layer optimization reports, CN/EN) |
| Archive | [docs/archive/](docs/archive/) (legacy implementation plans and validation notes) |

Most deep-dive documents are currently written in Chinese; the full index is
[docs/README.md](docs/README.md).

## 13. Distribution and License

The pinned `rwkv-mobile` revision does not ship a clear LICENSE file at the repository
root. The technical packaging chain works, but before public distribution the licenses
of the upstream sources, the MLX Swift FFI sources, and their dependencies must be
confirmed, and a project license must be chosen for RWKV-Agent.
