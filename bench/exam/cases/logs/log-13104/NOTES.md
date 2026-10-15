## Traps
- 第 1 轮“15 号”=2026-09-15，5xx 最多的是 billing-api（8 次）；第 2 轮用户纠正为 14 号=2026-09-14，答案是 order-gateway（7 次，billing-api 只有 2 次）。
- 复读第 1 轮的结论（billing-api）会失败：第 2 轮要求回答第一行（结论行）出现 order-gateway（output_first_line_contains_any）。不用 output_excludes：r1 盲解里 DeepSeek 的正确回答会在表格中列出 billing-api 的次数作对比，output_excludes 会误伤正确答案。也不能用 09-16 的数据：今天最多的是 user-center（6 次）。

## Reference solution
1. 读 logs/access.log 或用 search_text 找 2026-09-15 的 5xx（1–2 步），数各服务。
2. 第 2 轮：改看 2026-09-14（1 步）。共 3 步。

## Why the answer is unique
日志每行 `日期 时间 服务 状态码 路径`，5xx 指状态码 5 开头；14 号各服务 5xx 次数 7/3/2/1，最大值唯一。
- 日期改用明确的“15 号/14 号”：r1/r2 盲解中 DeepSeek 在 bash 里跑 `date` 得到真实系统日期（2026-10-15），把“昨天/前天”算成 10 月，完全没碰到 9 月日志。固定时钟只对 datetime 工具生效，bash 的 date 不受控，这是评测环境问题（已记入交付报告），不是题目要考的能力，所以本题回避相对日期。

EXAM-CANARY-e501b086
