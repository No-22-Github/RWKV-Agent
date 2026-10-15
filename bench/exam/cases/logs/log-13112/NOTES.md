## Traps
- 固定时钟 2026-09-16，“昨天”=09-15。nginx 在 09-15 有 3 次 restarted；另有 reload（不算重启）、php-fpm 的重启（不是 nginx）、09-14 和 09-16 的 nginx 重启（日期不对）。数全部 nginx restarted 会得到 6。
- 第 2 轮：tools: [] + require_active_no_call，复述 3，并算出一周 3×7=21。

## Reference solution
1. 读 ops.log 数 09-15 的 nginx restarted（1 步）：3。
2. 第 2 轮不调工具：3，一周 21。共 1 步。

## Why the answer is unique
“重启”=restarted，reload 是重载；日期限昨天；服务限 nginx。一周按 7 天。

## Teacher result
r1 DeepSeek 第 1 轮正确（3 次）；第 2 轮题面明确说“不用再翻日志了”，它仍调用 calculator 算 3*7，违反 tools: [] / require_active_no_call。内容 3 与 21 都对，失分只在选工具，与 nt-12002 同类。保留判分。

EXAM-CANARY-85461788
