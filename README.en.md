# RWKV-Agent

A local-first RWKV workspace agent. It loads RWKV-7 `.pth` checkpoints directly on a Mac,
runs inference with MLX, and lets the model list, read, and search files in a project
directory you choose, compute, and browse the web, then answer from the actual tool results.
It can also talk to a remote `rwkv_lightning` deployment or any OpenAI-compatible endpoint.

- **No Python at runtime**: Go owns the Conversation, Session, and Agent transactions;
  inference runs in a standalone `librwkv_agent_runtime.dylib` (a pinned RWKV Mobile
  tokenizer/sampler plus the MLX FFI), with no PyTorch, HTTP service, or external process.
- **One API, four front ends**: the CLI, TUI, desktop app, and browser service share the
  same public `api` package.
- **Built-in evaluation bench**: `agent-eval` ships several suites and writes reproducible
  run/trace/summary artifacts; `rwkv-lab` drives the case bank, corpus, and benchmark pipeline.

[中文版](README.md) · [Project index](INDEX.md) · [CLI reference](docs/guides/cli.md) (in Chinese)

## Status

| Area | Status |
| --- | --- |
| Platforms | Source builds work on Apple Silicon, macOS 15+. Linux is only verified in CI with `-tags server` (remote providers); no Windows entry point yet |
| Front ends | CLI / TUI, Wails V3 desktop app, headless browser service |
| Agent | Experimental; tools are read-only — no file writes, no command execution. Eval harness version `rwkv-agent-eval-v22` |
| Distribution | The packaging chain works; upstream licenses must be confirmed and a project license chosen before public distribution |

## Quick start

> For a first run, follow [macOS from scratch](docs/guides/getting-started-macos.md)
> (in Chinese); it covers model preparation, updates, and common errors.

**Requirements**: Apple Silicon Mac (macOS 15+), Xcode (with Swift and the Metal Toolchain),
CMake 3.25+, Ninja, Go 1.26+; the desktop app also needs Node.js 26 (pnpm is provisioned by
the script). Models are RWKV-7 `.pth` checkpoints or converted MLX safetensors directories.

```sh
git submodule update --init --recursive
brew install cmake ninja go

./scripts/build-macos.sh --check   # check the toolchain
./scripts/build-macos.sh           # outputs land in local/dist/
```

**Chat with a model** (loads `.pth` directly, no conversion needed):

```sh
./local/dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./local/sessions/demo.rwkv-session --autosave
```

**Let the agent read your project**:

```sh
./local/dist/rwkv-cli agent \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project \
  --prompt "Read the README and docs, then summarize what is done and what comes next"
```

**Desktop app**:

```sh
./scripts/build-app.sh
open -n "./local/dist/RWKV Agent.app" --args --workspace "$(pwd)"

# No window, browser service only
./local/dist/rwkv-app-server --host 127.0.0.1 --port 8080
```

## Components

| Entry point | What it does |
| --- | --- |
| `rwkv-cli run` | Single-turn generation or a multi-turn REPL; Sessions can be saved and restored |
| `rwkv-cli agent` | Workspace agent; full-screen TUI in an interactive terminal, plain text for scripts and pipes |
| `rwkv-cli agent-eval` | Fixed-suite evaluation writing `run.json` / `trace.jsonl` / `summary.json` |
| `rwkv-cli concurrent` · `bench` | 1–8 concurrent generations from one model in a dashboard; pick a pane to keep chatting |
| `rwkv-cli convert` | `.pth` → MLX safetensors without Python (optional) |
| `rwkv-cli state` | Upload / list / delete States on an `rwkv_lightning` deployment |
| Desktop app (`cmd/rwkv-app`) | Local or remote model setup, persistent conversations, tool trajectories, streamed answers, State management |
| `rwkv-lab` (`cmd/rwkv-lab`) | Dev tooling: `bank` case bank, `corpus` rendering, `run` checks and comparisons, `bench` sweeps, `state` training helpers |

Every flag and behavior is documented in the [CLI reference](docs/guides/cli.md); app storage
and configuration are in [docs/guides/app.md](docs/guides/app.md).

## Core capabilities

**Inference**

- Memory-maps `.pth` straight into MLX without writing a second copy of the weights; the first
  load builds a metadata index of tens to hundreds of KB, rebuilt automatically when the
  checkpoint changes.
- A single-model scheduler with continuous batching: up to 8 active Sessions, each with its own
  sampler and State.
- Uses the official G1 chat template by default; `--thinking off|fast|full` controls the
  thinking prefill.

**Sessions**

- A Session is a set of immutable revisions plus an atomic `CURRENT` pointer. The transcript is
  the source of truth; `state.bin` is only a checksummed acceleration snapshot and is replayed
  from the transcript when missing or incompatible.
- Each turn is generated on a candidate transcript and committed only on full success;
  cancellation or errors never leave half-written messages.

**Agent**

- Default tools: list directories, read files, and literal search inside the workspace, plus
  `calculator`, `data_query`, and `datetime`.
- Optional: `--web` enables Brave search + Tavily fetch (with backoff on 429/5xx);
  `--subagents` enables `spawn_agents`, running 2–8 independent subtasks concurrently
  (subagents cannot spawn further).
- Safety boundary: every path is confined to `--workspace`; absolute paths, `..` traversal,
  and escaping symlinks are rejected, and single-file reads are capped at 64 KiB. A turn is
  committed transactionally only when it succeeds; failures roll the whole turn back.
- The tool-call format (XML / Markdown / G1K, …) is described by a separate wire layer and can
  be switched with `--profile`; see the [wire configuration guide](docs/guides/wire-configuration.md)
  and the [tool and wire format overview](docs/design/tool-and-wire-formats.md) (in Chinese).

**Remote providers**

| `--completion` | Backend |
| --- | --- |
| `local` | Local MLX inference (default) |
| `rwkv-lightning-cuda` | C++/CUDA Lightning, raw continuation on `/v1/batch/completions`; supports reusing an uploaded State with `--state-id` |
| `rwkv-lightning-python` | Python Lightning, raw continuation on `/v1/chat/completions` |
| `chat-completions` | OpenAI-compatible Chat Completions; needs `-tags chatcompletions` or `build-macos.sh --with-chat-completions` |

Credentials are read only from environment variables (`--api-key-env`,
`--api-header-env HEADER=ENV`) and never appear in command-line arguments, config files, or eval
artifacts. Examples and per-backend differences are in the
[CLI reference · remote providers](docs/guides/cli.md#5-远程-provider).

## Evaluation

```sh
./local/dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite boundary \
  --output local/runs/local-boundary
```

| Suite | Contents |
| --- | --- |
| workbank (`--cases bench/workbank/cases`) | **Primary exam**: 148 real agent tasks, each scored by its own `verify.py` |
| `bfcl-product` | 60 product cases adapted from BFCL semantics: deliberate no-call, asking for missing arguments, multi-turn decisions |
| `boundary` (default) | 18 read-only tasks adapted from primitive-bench |
| `smoke` / `assistant` | Protocol and safety-contract regressions; mock weather, transit, and currency scenarios |
| `primitive-orig30` / `primitive-feedback30` | Pinned, embedded Primitive Bench snapshots |

Formal runs should follow the [benchmark protocol](docs/evaluations/benchmark-protocol.md)
(format, budgets, sampling presets, concurrency limits, and the `rwkv-lab run check` gate).
Results and conclusions live in [docs/evaluations/](docs/evaluations/); scores from different
harness or case-bank versions are not directly comparable.

## Tests

```sh
go test ./...                       # no real model needed
go test -race ./...
./scripts/test-macos-native.sh      # C ABI lifecycle + AddressSanitizer

RWKV_TEST_PTH=/absolute/path/to/rwkv7-model.pth ./scripts/test-macos-real-model.sh
```

CI (`.github/workflows/ci.yml`) runs Go race tests, the Linux `-tags server` build and vet, and
the frontend `pnpm test` + `pnpm build`.

## Layout

```text
api/                     Public Agent API shared by CLI / TUI / app / browser service
cmd/
  rwkv-cli/              CLI and TUI entry point
  rwkv-app/              Wails V3 desktop app (Go backend + React frontend)
  rwkv-lab/              Case bank, corpus, and benchmark tooling
internal/
  agent/                 Agent harness, wire layer, tools; agent/eval/ holds the eval suites
  continuation/          Generator abstraction with local / rwkvlightning / chatcompletions adapters
  conversation/          Transcripts, revisions, and session bundles
  inference/  native/    Inference core, scheduling, MLX FFI / converter
  lab/                   Implementation of the rwkv-lab subcommands
  cli/  tui/  appstorage/ …
native/                  C ABI runtime (librwkv_agent_runtime)
bench/                   Tracked data: workbank and distill case banks, teacher scripts, frozen baselines (see bench/README.md)
docs/                    Docs: guides/ usage, design/ design and contracts, evaluations/, distill/, archive/
scripts/                 Build, test, and BFCL scripts
third_party/rwkv-mobile  Pinned tokenizer/sampler upstream (submodule)
local/                   Machine-local outputs (builds, models, runs), not tracked
```

## Documentation

Most documents are written in Chinese.

| Looking for | Go to |
| --- | --- |
| First run and troubleshooting | [getting-started-macos.md](docs/guides/getting-started-macos.md) |
| Every command's flags | [cli.md](docs/guides/cli.md) |
| Desktop app and public API | [app.md](docs/guides/app.md) |
| Tool-call formats and wire configuration | [tool-and-wire-formats.md](docs/design/tool-and-wire-formats.md) · [wire-configuration.md](docs/guides/wire-configuration.md) |
| Inference core and direct `.pth` loading | [inference-core-design.md](docs/design/inference-core-design.md) · [direct-pth-loading.md](docs/design/direct-pth-loading.md) |
| Continuation interface and agent protocol | [continuation-and-agent-protocol.md](docs/design/continuation-and-agent-protocol.md) |
| Benchmark protocol and results | [benchmark-protocol.md](docs/evaluations/benchmark-protocol.md) · [docs/evaluations/](docs/evaluations/) |
| Distillation corpus workflow | [distill-workflow.md](docs/distill/distill-workflow.md) |
| Where the data lives | [bench/README.md](bench/README.md) |
| All documents | [INDEX.md](INDEX.md) · [docs/README.md](docs/README.md) |

## License

The pinned `rwkv-mobile` revision has no explicit LICENSE file at its root. Before public
distribution, the licensing of the upstream sources, the MLX Swift FFI, and their dependencies
must be confirmed, and a project license chosen for RWKV-Agent.
