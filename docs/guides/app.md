# RWKV Agent App

The demo application uses Wails V3 beta, TypeScript, React, and Vite with a Material
Design 3 frontend. The desktop and browser-only variants embed the same production
frontend and bind the same public Go API from `api/`.

## Features

- Material Design 3 interface with a navigation drawer, chat session rail, and
  responsive dialogs.
- Persistent conversations per workspace: display messages and the complete committed
  Harness transcript (tool calls and results included) survive restarts and are
  restorable through the public `api`.
- Tool trajectories per message: step, tool, arguments, status, error, subagent
  details, and per-attempt web-provider retries are recorded and rendered in the UI.
- Resilient `web_search`/`web_fetch`: 429/5xx responses and transport errors retry up
  to 5 times with exponential backoff (500 ms base, 5 s cap, jitter), honor
  `Retry-After`, and emit retry events into the trajectory; a gate serializes provider
  requests.
- Uploaded-state management for RWKV Lightning CUDA connections: upload a `.pth`
  state (native picker on the desktop, the browser's file picker in server mode,
  where the file is staged by the app server and forwarded), pick the state a
  connection generates from, and delete states from the shared deployment. The
  app remembers which local file produced each `state_id`; when a deployment
  restart wipes its states, the editor offers a one-click re-upload, and
  connecting with a state the server no longer holds is refused up front. The
  running state is shown next to the model name and in each turn's metadata.
- MiSS adapter management for the same connections, independent of the state
  (a connection can use an adapter, a state, both, or neither): upload a local
  MiSS package (`adapter-final.pth` or a checkpoint's `training.pth`) under an
  adapter ID, pick the adapter a connection binds via `adapter_id`, and
  unregister it. Uploads use the same pickers as states. Registrations live in
  the server's RAM, so the desktop app remembers which local file produced each
  one and offers a one-click re-upload after a restart. Registering a package
  that already sits on the inference host is a CLI-only operation:
  `rwkv-cli adapter register --path …` (also `adapter list` / `adapter delete`). Connecting is refused when the chosen adapter is gone or the
  deployment has no `/v1/adapters` (an old build would ignore `adapter_id` and
  answer as the base model). The running adapter has its own chip next to the
  state chip.
- One "格式预设" selector replaces the protocol and thinking selectors: 标准（不思考）
  = `g1k`, 深度思考 = `g1k-think` (the wire v2.0 MiSS adapters were trained on),
  Markdown 工具调用（实验）. Fast thinking and the profile-less legacy `xml-v1` only
  appear while a saved connection still uses them. Sampling presets show Chinese
  names; the CLI `--sampling` name is in the hint.
- Thinking is visible: the runner streams `thinking_delta` events, the chat shows
  the last two lines of the current step's thought while it runs, and the tool
  activity card interleaves an expandable "思考" row per step with the tool calls
  (thought → call → thought → answer). The trajectory view splits it out too,
  including g1k-think's withheld `<think` opening.
- Local model (`.pth` or MLX directory) or remote RWKV continuation / OpenAI-compatible
  Chat Completions configuration, remote model listing via `GET /v1/models`, arbitrary
  HTTP headers, and macOS system proxy support.

## Build on Apple Silicon macOS

The complete build prepares the native MLX runtime, verifies the frontend, and creates
both launch modes. In addition to the native toolchain, the build requires Node.js 26
with npm. It uses the exact pnpm version declared in the frontend's `packageManager`
(also used by CI). If that version is not on PATH, the script installs and reuses it
under `local/build/toolchain/` without changing your global pnpm:

```sh
./scripts/build-app.sh
```

The native runtime and frontend build run concurrently; both must succeed before
the desktop executables are built. Unchanged MLX products and prepared PTH loader
sources keep their timestamps so repeated builds can reuse Ninja's compiled
objects and linked runtime. Builds skip frontend tests by default; TypeScript
checking and all builds still run. Run frontend tests separately with:

```sh
./scripts/test-app.sh
```

The outputs stay together with the native runtime and Metal resources in `local/dist/`:

```text
local/dist/RWKV Agent.app/
local/dist/rwkv-app
local/dist/rwkv-app-server
local/dist/librwkv_agent_runtime.dylib
local/dist/mlx-swift_Cmlx.bundle/
local/dist/assets/rwkv_vocab_v20230424.txt
```

Launch the native Wails window:

```sh
open -n "./local/dist/RWKV Agent.app" --args --workspace "$(pwd)"
```

The bundle contains the Wails executable, native MLX runtime, Metal resources,
and tokenizer. For a non-default workspace during development, the unpackaged
executable remains available:

```sh
./local/dist/rwkv-app --workspace /absolute/path/to/workspace
```

Launch the same application without creating a native window, then open it in a browser:

```sh
./local/dist/rwkv-app-server --host 127.0.0.1 --port 8080 --workspace /absolute/path/to/workspace
open http://127.0.0.1:8080
```

The server binary is compiled with Wails V3's `server` build tag. It keeps Wails bindings and event streaming while replacing native windows with an HTTP server.

## Public Agent API

The CLI, TUI, desktop window, and browser server all use the exported
`github.com/no22/RWKV-Agent/api` package. A client owns one `Service`, configures
one model source, and creates isolated multi-turn `Session` values:

```go
service, err := api.NewService(api.Options{Workspace: "/path/to/repository"})
status, err := service.Configure(ctx, api.Config{
    Provider:          api.ProviderRWKVLightningCUDA,
    Endpoint:          "https://example.com",
    Model:             "rwkv7-model",
    Headers:           map[string]string{"CF-Access-Client-Id": clientID},
    EnableWeb:         true,
    BraveAPIKey:       braveKey,
    TavilyAPIKey:      tavilyKey,
    EnableSubagents:   true,
    MaxActiveBatch:    4,
    RemoteBatchWaitMS: 10,
}, nil)
session, err := service.NewSession(ctx)
result, err := session.Run(ctx, "Read README.md and return its first line.")
```

`ProviderLocal` uses local inference, `ProviderRWKVLightningPython` uses Python
Lightning raw continuation, `ProviderRWKVLightningCUDA` uses CUDA batch continuation,
and `ProviderChatCompletions` uses standard Chat Completions with native tool support.
The ambiguous `rwkv-lightning` provider is no longer accepted. `Status`, `Event`, `Step`, and `Result` are transport-safe public types;
secret values are deliberately absent from `Status`. Progressive tool exposure
is enabled by default; set `ProgressiveTools` to an explicit false pointer only
for fixed-catalog compatibility.

## Persistent application storage

The app uses `github.com/adrg/xdg` for configuration, durable data, application
state, and cache locations. It persists:

- the complete model/provider configuration in `settings.json`, including API
  keys, service passwords, web-provider keys, and custom HTTP header values;
- display messages and the complete committed Harness transcript for each
  conversation, including tool calls and tool results;
- the last workspace, recent workspaces, and the active conversation for each
  workspace;
- a dedicated cache directory for application-level disposable data.

Writes use a temporary file followed by an atomic replacement. Directories
created on POSIX systems use mode `0700` and JSON files use `0600`. Credentials
are intentionally stored as plaintext JSON in this version; they are not sent
through Wails status events, but any process or account that can read the user's
configuration file can read them.

The default locations are:

| Platform | Configuration | Conversations | Application state | Cache |
| --- | --- | --- | --- | --- |
| Linux | `~/.config/RWKV-Agent/settings.json` | `~/.local/share/RWKV-Agent/conversations/` | `~/.local/state/RWKV-Agent/app-state.json` | `~/.cache/RWKV-Agent/` |
| macOS | `~/Library/Application Support/RWKV-Agent/settings.json` | `~/Library/Application Support/RWKV-Agent/conversations/` | `~/Library/Application Support/RWKV-Agent/app-state.json` | `~/Library/Caches/RWKV-Agent/` |
| Windows | `%LOCALAPPDATA%\RWKV-Agent\settings.json` | `%LOCALAPPDATA%\RWKV-Agent\conversations\` | `%LOCALAPPDATA%\RWKV-Agent\app-state.json` | `%LOCALAPPDATA%\cache\RWKV-Agent\` |

On Windows, the XDG library resolves the `LocalAppData` Known Folder instead of
assuming that `%LOCALAPPDATA%` contains a particular path. These files remain
local to the Windows user profile and do not roam with `%APPDATA%`. Windows ACLs
provide the effective access control; POSIX mode bits such as `0600` are not a
substitute for ACLs there. Atomic replacement uses Go's Windows rename path,
which requests replacement of the existing destination, so subsequent saves do
not require deleting the old settings file first.

The standard `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, and
`XDG_CACHE_HOME` environment variables override these defaults on every desktop
platform, including Windows. Passing `--workspace` explicitly overrides the
remembered workspace. At startup, saved settings hydrate the UI but the app does
not load a local model or contact a remote provider until the user reconnects.

Deleting the cache directory is safe for application-level disposable data.
Deleting `settings.json` removes saved provider settings and plaintext
credentials; deleting `app-state.json` forgets recent/active projects; deleting
the conversations directory removes chat history. Existing `.rwkvi` inference
indexes keep their current behavior and are outside this persistence change.

## Model setup

Open **设置** in the lower-left corner.

- **本地模型** accepts an RWKV-7 `.pth` checkpoint or an MLX safetensors directory. The tokenizer is discovered beside the model, beside the executable, in `local/dist/assets`, or in the pinned `rwkv-mobile` assets; it can also be selected explicitly.
- **远端 API** defaults to **RWKV 续写**. It accepts an API base URL, `/v1/models`, or `/v1/batch/completions` and normalizes inference to the continuation-native `/v1/batch/completions` endpoint. Stop sequences are enforced by the Harness client, so the server-specific `stop_tokens` field is omitted by default.
- **OpenAI 兼容** is the fallback for non-RWKV models and normalizes the same base URL to `/v1/chat/completions`.
- Both protocols support credentials and arbitrary custom HTTP headers. This includes Cloudflare Access headers. The desktop app saves these values in the local plaintext `settings.json`; model status exposes only sanitized header names, never values.
- **Agent 能力** for a **new** connection defaults to the `g1k` wire profile (the format the training corpus is rendered in and the product evaluation runs), the `g1k-agent` sampling preset, XML protocol with thinking off, and loop-rescue limits 2/3/3. Web search/fetch, weather (keyless Open-Meteo) and bash are on; sub-agents stay off. Saved connections are never rewritten: one without a profile keeps its legacy XML defaults (`xml-v1` wire, greedy sampling) until you change it. The defaults live in `api.NewConfigDefaults` and are mirrored by `NEW_CONFIG_DEFAULTS` in `providerManager.ts`. Markdown/function protocol and progressive tool routing remain explicit options (choosing Markdown drops the profile; choosing XML again restores `g1k`). With a profile set, the thinking selector is written as a `thinking=fast|full` wire override. Optional Brave Search + Tavily Extract and concurrent `spawn_agents` delegation are unchanged. Web tools no longer need both keys to be enabled: without keys they stay in the tool list and a call answers "not configured, fill in the key in settings" (the Runner marks the tool unavailable for that turn). Subagent settings control local active batch, child concurrency/steps/timeout, and the RWKV Lightning request-coalescing window.
- On macOS, the desktop process uses `HTTP_PROXY`/`HTTPS_PROXY` when present and otherwise reads the explicit HTTP, HTTPS, or SOCKS proxy from `scutil --proxy` at startup. System proxy exceptions and local addresses bypass the proxy. Restart the app after changing macOS proxy settings; PAC auto-configuration is not evaluated yet.

Each child Agent gets an independent Session and transcript. Local MLX uses
continuous batching, RWKV Lightning coalesces compatible continuations into one
`contents[]` request, and Chat Completions uses concurrent HTTP requests. Child
Agents do not receive the delegation tool, so batches cannot recursively fan out.

Use **测试并获取模型** to make an authenticated `GET /v1/models` request. Select a returned model and use **连接 API** to configure Agent conversations.

## Shared assembly with the evaluation

The tool list and the harness options of a session are built by
`internal/agent/product` (`product.Tools` and `product.HarnessOptions`), and the
product evaluation (`agent-eval --harness app`) calls the same functions with
fixture backends (fixture web/weather providers, fixed clock). The `api` package
only converts `api.Config` into `product.ToolSet`/`product.Backends`/
`product.HarnessConfig`. The tool order is fixed in one place: file reads
(`list_files`, `read_file`, `search_text`), editing (`read_lines`, `write_file`,
`replace_lines`, `append_file`), local compute (`calculator`, `data_query`,
`datetime`), `web_search`, `web_fetch`, `get_weather`, `bash`, `spawn_agents`.
Editing is offered only when writes go to a staged workspace. The bash tool is
registered only when the just-bash sidecar is found (it is bundled next to the
app executable by `scripts/build-app.sh`); without it the session still opens
with read-only file tools and no bash. `api/parity_test.go` compares the two
paths byte for byte: control prompt, response prompt, session-time message, tool
order and per-tool schema hashes. The App-only system text (the `<session_time>`
message, the no-workspace hint, the staged-files notice, the user's task
contract) is produced by the same package, so the evaluation can include it.

## File change review

The App uses one just-bash OverlayFs per conversation, including when the bash
capability is disabled. `bash`, `read_file`, `read_lines`, `list_files`,
`search_text`, `data_query`, `write_file`, `replace_lines`, and `append_file`
share that view. Child Agents share their parent's overlay. Writes never reach
the workspace until the user confirms them in the file change panel.

At the end of each turn (also after an error or stop), file cards and a compact,
collapsible change summary appear below that response. The summary shows added
and removed line counts, animates expansion and collapse, and supports individual
or grouped save/discard actions. Use **查看改动** to open a diff directly.
Open a file card to inspect HTML previews, code, or diffs in the right pane. The
viewer lets you switch between the response's files and slides over the right edge without resizing the conversation or hiding
navigation. It animates both opening and closing, supports Escape and clicking
outside to dismiss, and respects reduced motion; narrow windows show it full
screen. Directory decisions include their children; saving a new file also creates its staged parent directories. Binary
and large files offer downloads of the exact original and proposed contents.

The App checks both the reviewed snapshot and the current disk contents before
applying a change. External edits cause a conflict instead of being overwritten.
Unresolved changes remain in memory across turns. Resolve them before switching
conversations, workspaces, connections, or regenerating a turn. Closing the App
or losing the sidecar process discards unconfirmed changes. Read-only artifact
snapshots and save/discard status remain attached to the response for later
inspection; reopening a conversation never restores its pending workspace edits.
Normal files use atomic replacement; applying a batch is not one filesystem
transaction, and I/O failures can leave a partly applied
batch with the remaining changes still awaiting review.

The sidecar is now required for App workspace sessions, so desktop builds require
Bun even when bash is disabled. API integrations can call `NewStagedSession`,
`Session.FileChanges`, and `Session.ResolveFileChanges`; an API session enabling
bash also shares an overlay across its file tools. Evaluation-only native file
tool constructors retain their direct disk behavior unless supplied a staged
`WorkspaceFS`.

## Development

Regenerate Wails TypeScript bindings after changing `AppService` or public `api` types:

```sh
cd cmd/rwkv-app
go run github.com/wailsapp/wails/v3/cmd/wails3@v3.0.0-beta.8 generate bindings -clean -ts
```

Run frontend checks with Node 26 and pnpm 11, matching CI:

```sh
cd cmd/rwkv-app/frontend
pnpm install --frozen-lockfile
pnpm test
pnpm run build
```

Run backend checks:

```sh
go test ./...
go vet ./...
```
