## Traps
- TR-DECOY: unopened items have 30 days; opened software has 14. 30 days from Sept 1 would be Oct 1.
Turn 1 requires reading docs/returns.md (14 days). Turn 2 is a memory turn (tools: [], require_active_no_call): Sept 1 + 14 days = Sept 15.

## Reference solution
1. Read docs/returns.md: opened software 14 days from purchase.
2. Answer from memory: 15 September 2026.

## Why the answer is unique
"14 days from purchase" with purchase on 1 Sept gives 15 Sept; a reply of Sept 14 would not match the accepted forms. The policy is the only source and it counts from purchase.

## Teacher result
r1: DeepSeek answered turn 1 correctly (14 days) but on the memory turn it called tools (datetime / file, two erroring) before answering, and wrote the year as 2025. Fails require_active_no_call: a real tool-discipline failure; the year is not judged.

EXAM-CANARY-7a7edb58
