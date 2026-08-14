# RWKV Agent App

The demo application uses Wails V3 beta, TypeScript, React, and Vite. The desktop and browser-only variants embed the same production frontend and bind the same public Go API from `api/`.

## Build on Apple Silicon macOS

The complete build prepares the native MLX runtime, verifies the frontend, and creates both launch modes:

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

## Model setup

Open **设置** in the lower-left corner.

- **本地模型** accepts an RWKV-7 `.pth` checkpoint or an MLX safetensors directory. The tokenizer is discovered beside the model, beside the executable, in `dist/assets`, or in the pinned `rwkv-mobile` assets; it can also be selected explicitly.
- **远端 API** defaults to **RWKV 续写**. It accepts an API base URL, `/v1/models`, or `/v1/batch/completions` and normalizes inference to the continuation-native `/v1/batch/completions` endpoint. Stop sequences are enforced by the Harness client, so the server-specific `stop_tokens` field is omitted by default.
- **OpenAI 兼容** is the fallback for non-RWKV models and normalizes the same base URL to `/v1/chat/completions`.
- Both protocols support credentials and arbitrary custom HTTP headers. This includes Cloudflare Access headers. Secret values stay in backend memory and model status exposes only sanitized header names, never values.
- **Agent 能力** defaults to the trained Markdown/function transcript and keeps XML as an explicit compatibility mode. It also enables progressive tool exposure, optional Brave Search + Tavily Extract, and concurrent `spawn_agents` delegation. Web tools require both provider keys. Subagent settings control local active batch, child concurrency/steps/timeout, and the RWKV Lightning request-coalescing window.

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

Run frontend checks:

```sh
cd cmd/rwkv-app/frontend
npm ci
npm test
npm run build
```

Run backend checks:

```sh
go test ./api ./internal/tui/agent ./cmd/rwkv-cli ./cmd/rwkv-app
```
