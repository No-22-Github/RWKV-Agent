## Traps
- 记忆题：第 2 轮 tools: [] + require_active_no_call，不许再调工具（即便读文件也算违规）。答案需同时出现原值 24 与翻倍值 48。
- 干扰值：prefetch_count 8（翻倍 16）、max_retries 3、retry_delay_sec 30；答 8/16 或 30/60 都错。

## Reference solution
1. 第 1 轮读 config/queue.yaml（1 步），报告 worker_concurrency=24。
2. 第 2 轮不调工具：复述 24，翻倍 48。共 1 步。

## Why the answer is unique
worker_concurrency 仅一行，值 24；翻倍 48。verify.py 打印第 1 轮的值 24（单一对象），第 2 轮判 24 与 48 同时出现。

EXAM-CANARY-9005b3ae
