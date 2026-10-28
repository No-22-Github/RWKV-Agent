# rwkv_lightning 接口怪癖

不同部署版本行为不一，先拍 `/v1/models` 和状态接口，记下模型 id 和引擎版本；跑完再拍一次，模型可能被静默替换。

## 请求体

- 批续写接口 `/v1/batch/completions` 的字段是 **`contents`（字符串数组）**，传 `prompt` 会报 `Empty prompts list`。这是裸续写，prompt 自己拼。
- `/v1/chat/completions` 传 `messages` 会套服务端 chat 模板和 think 前缀——要精确控制字节就别用它。
- `stop_tokens` 的类型随部署变：旧 Python 版是字符串（`["\nUser:"]`），CUDA 版是整数（`[0, 24281]`）。传错类型会返回 HTTP 500 空响应。
  排查顺序：不传 → 文本 → 整数。
- `/big_batch/completions` 只认 temperature，且**单飞**：第二个并发请求返回 409。提前关掉 SSE 会把锁挂住（clean 接口也不可靠），必须把 SSE 读到 `[DONE]`。
- CUDA 版不逐行报告结束：某行采到 EOS 后只是不再出 chunk。客户端用"同批其他行已走了很多步而本行无输出"判定结束。
- 跑满 max_tokens 时 finish_reason 可能仍是 `stop`，按生成数 ≥ 98% 上限判撞顶。

## 网络

- 前面挂 Cloudflare 时，Python `urllib` 默认 UA 会被拦成无 body 的 403，带 `User-Agent: curl/8.x` 就通。urllib 偶尔拿到空 body，改用 `http.client`/`httpx`/curl。
- Cloudflare 有约 100 秒超时（524/502）和 100MB 请求体上限（413）；大文件上传用 `curl --http1.1`。

## 并发与吞吐

- **服务端不拒绝超额请求，显存不够就整个进程崩**（段错误），不是返回 429。客户端必须自己限并发，从小往上加。
- 共享端点上多个客户端各开高并发会出现 502 海啸；所有客户端的总并发要合计。
- 同卡多请求轮流解码，吞吐主要看批大小（单请求约百 tok/s，批 64 约数千 tok/s）。
- 合批后瓶颈在预填充。新版有前缀缓存（只缓存整段 prompt），同一会话多步能命中（3 万 token 预填 6.5s → 0.17s），
  跨请求共享的系统提示吃不到。多卡网关要带 `session_id`（或 `X-RWKV-Session-Id` 头）才会粘在同一张卡上命中缓存。

## state / adapter

- CUDA 后端用 `state_id` 加载上传的 state；Python 后端不支持。
- 上传必须**串行**，并且在开跑前完成。
- 网关上传可能只落到一张卡：验收不能只看 list，要用同一 id 并发 9+ 个请求全部 200。
- 未知 adapter 应返回 400；老版本会**悄悄忽略** adapter_id 按基模回答——对照实验一定先验证 adapter 真的生效。
- 服务重启后上传的 state/adapter 全部清空；按路径注册时路径相对服务进程工作目录。
- transcript 才是事实源，state 只是可丢弃的加速附件：不能跨模型、跨分词器、跨模板版本复用；不兼容就报错，不要"尽量加载"。
