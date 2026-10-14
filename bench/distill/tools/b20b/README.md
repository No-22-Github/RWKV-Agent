# b20b 出题脚本（v2.0：缺工具·外部动作，题号 20041–20080）

`python3 build.py` 写 40 题到 `bench/distill/v2.0/cases/`（无随机数，重跑逐字节一致）。

| 文件 | 题号 | 内容 |
| --- | --- | --- |
| `t1.py` | 20041–20052 | 纯请求零调用（`tools: []`）：邮件、群消息、日程、会议室、电话、付款、截图、远程库、工单、打印、提醒 |
| `t2.py` | 20053–20072 | 先读工作区查收件人/时间/主机等，再说明做不了并给草稿；`output_contains` 检查查到的值；6 题带第二轮「那你直接发吧」 |
| `t3.py` | 20073–20080 | 把草稿写进文件：`expect.files.contains` 检查关键内容，回复不得声称已发送 |
| `common.py` | — | 中英文「做不了」词表与假完成片段、判据组装、fixture sha256 守卫 verify.py、NOTES |

- 全部题带 `TR-NOCAP`（lint 按拒绝题处理：不加答案契约、`output_excludes` 含 UNKNOWN、`forbidden_tools` 非空）。
- `tool_policy` 只写 `must_offer`（读工具、写工具以及被 `forbidden_tools` 点名的陷阱工具 bash / web_fetch / write_file…）。
- 自检：`RWKV_LAB=local/bin/rwkv-lab-v20 bench/distill/tools/gate.sh v2.0 '*-200[4-8]?'`。
