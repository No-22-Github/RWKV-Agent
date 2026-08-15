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
- Local model (`.pth` or MLX directory) or remote RWKV continuation / OpenAI-compatible
  Chat Completions configuration, remote model listing via `GET /v1/models`, arbitrary
  HTTP headers, and macOS system proxy support.

## Build on Apple Silicon macOS

The complete build prepares the native MLX runtime, verifies the frontend, and creates
both launch modes. In addition to the native toolchain, the build requires Node.js and
npm (CI pins Node 24):

```sh
./scripts/build-app.sh
```

The outputs stay together with the native runtime and Metal resources in `dist/`:

```text
dist/RWKV Agent.app/
dist/rwkv-app
dist/rwkv-app-server
dist/librwkv_agent_runtime.dylib
dist/mlx-swift_Cmlx.bundle/
dist/assets/rwkv_vocab_v20230424.txt
```

Launch the native Wails window:

```sh
open -n "./dist/RWKV Agent.app" --args --workspace "$(pwd)"
```

The bundle contains the Wails executable, native MLX runtime, Metal resources,
and tokenizer. For a non-default workspace during development, the unpackaged
executable remains available:

```sh
./dist/rwkv-app --workspace /absolute/path/to/workspace
```

Launch the same application without creating a native window, then open it in a browser:

```sh
./dist/rwkv-app-server --host 127.0.0.1 --port 8080 --workspace /absolute/path/to/workspace
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
    Provider:          api.ProviderRWKVLightning,
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

`ProviderLocal` uses the native MLX continuation, `ProviderRWKVLightning` uses
the RWKV continuation endpoint, and `ProviderChatCompletions` is the compatibility
adapter. `Status`, `Event`, `Step`, and `Result` are transport-safe public types;
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

- **本地模型** accepts an RWKV-7 `.pth` checkpoint or an MLX safetensors directory. The tokenizer is discovered beside the model, beside the executable, in `dist/assets`, or in the pinned `rwkv-mobile` assets; it can also be selected explicitly.
- **远端 API** defaults to **RWKV 续写**. It accepts an API base URL, `/v1/models`, or `/v1/batch/completions` and normalizes inference to the continuation-native `/v1/batch/completions` endpoint. Stop sequences are enforced by the Harness client, so the server-specific `stop_tokens` field is omitted by default.
- **OpenAI 兼容** is the fallback for non-RWKV models and normalizes the same base URL to `/v1/chat/completions`.
- Both protocols support credentials and arbitrary custom HTTP headers. This includes Cloudflare Access headers. The desktop app saves these values in the local plaintext `settings.json`; model status exposes only sanitized header names, never values.
- **Agent 能力** defaults to the trained Markdown/function transcript and keeps XML as an explicit compatibility mode. It also enables progressive tool exposure, optional Brave Search + Tavily Extract, and concurrent `spawn_agents` delegation. Web tools require both provider keys. Subagent settings control local active batch, child concurrency/steps/timeout, and the RWKV Lightning request-coalescing window.
- On macOS, the desktop process uses `HTTP_PROXY`/`HTTPS_PROXY` when present and otherwise reads the explicit HTTP, HTTPS, or SOCKS proxy from `scutil --proxy` at startup. System proxy exceptions and local addresses bypass the proxy. Restart the app after changing macOS proxy settings; PAC auto-configuration is not evaluated yet.

Each child Agent gets an independent Session and transcript. Local MLX uses
continuous batching, RWKV Lightning coalesces compatible continuations into one
`contents[]` request, and Chat Completions uses concurrent HTTP requests. Child
Agents do not receive the delegation tool, so batches cannot recursively fan out.

Use **测试并获取模型** to make an authenticated `GET /v1/models` request. Select a returned model and use **连接 API** to configure Agent conversations.

## Development

Regenerate Wails TypeScript bindings after changing `AppService` or public `api` types:

```sh
cd cmd/rwkv-app
go run github.com/wailsapp/wails/v3/cmd/wails3@v3.0.0-beta.8 generate bindings -clean -ts
```

Run frontend checks (use Node 24 to match CI):

```sh
cd cmd/rwkv-app/frontend
npm ci
npm test
npm run build
```

Run backend checks:

```sh
go test ./...
go vet ./...
```
