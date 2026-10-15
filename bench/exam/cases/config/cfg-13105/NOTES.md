## Traps
- 第 1 轮问 staging（18），第 2 轮用户纠正为 prod，答案 64。要求第 2 轮回答第一行（结论行）出现 64（output_first_line_contains_any），复读旧答案 18 或拿别的数字充当答案都会失败。不用 output_excludes：r1 盲解里 DeepSeek 的正确回答写了“对比一下：staging 是 18，prod 是 64”，output_excludes 会误伤正确答案（题有问题，已修）。

## Reference solution
1. 读 deploy/staging.env（1 步）。
2. 第 2 轮：读 deploy/prod.env（1 步）。共 2 步。

## Why the answer is unique
prod.env 里 DB_POOL_SIZE=64，仅此一处；其他数值字段名不同。

EXAM-CANARY-e1330098
