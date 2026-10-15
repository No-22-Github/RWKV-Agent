## Traps
- TR-DECOY: deploy/example.env has DB_POOL_SIZE=10 (dev defaults). Prod is 24.
Turn 1 requires reading deploy/prod.env (answer 24). Turn 2 is a memory turn: the reply must restate 24 and give 72 without calling any tool (tools: [] + require_active_no_call).

## Reference solution
1. Read deploy/prod.env: DB_POOL_SIZE=24.
2. Reply from memory: 24, tripled is 72.

## Why the answer is unique
Prod value 24 (not the example file's 10); 24 x 3 = 72. Judged on 72 present in the text, plus 24 as a whole token.

## Teacher result
r1: DeepSeek read prod.env correctly (24) but on the memory turn it called a tool again despite the user saying it already found the value, then answered 24 / 72 correctly. Fails tools: [] + require_active_no_call: a real tool-discipline failure, not a scoring problem.

EXAM-CANARY-728f5e2b
