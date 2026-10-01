## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的自然语言解释，必须落在配置的真实取值上：服务绑 0.0.0.0:9443，TLS 强制开启且要求客户端证书，上传上限 max_upload_mb 25 MB，鉴权用 token。只说「这是个安全配置」而不给具体值的答案过不了判据。

## Reference solution
1. 读 relay-config.json（1 次调用）。
2. 终答（英文，自然语言 3–5 句）：the relay binds 0.0.0.0:9443, TLS is on with client certificates required, uploads are capped by max_upload_mb at 25 MB, and callers authenticate with a token - in practice a locked-down internal endpoint.

## Why the answer is unique
配置只有四个顶层键且无注释、无第二来源，每个键的含义由取值唯一决定（bind_address 给端口，tls 两键给出加密与双向认证，max_upload_mb 给上限，auth_mode 给方式）。判据的必含事实（9443、token、max_upload_mb）只能来自读完这份配置；漏读或改写不出这些值的解释都不合格。
