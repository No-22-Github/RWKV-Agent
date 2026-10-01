## Traps
- TR-DATEFMT: three rows use DD/MM/YYYY slash dates (README: day/month/year). Ferris Home Care ends 02/08/2026 = 2 Aug and Tortoise Cloud ends 04/08/2026 = 4 Aug (both active in July and August); Quill Events starts 03/08/2026 = 3 Aug (active in August, not July). Reading slash dates as month-first drops Ferris and Tortoise from both months and adds Quill to July: naive counts are 21 for August and 23 for July.

## Reference solution
1. Read subs-export.csv and the README date convention (turn 1).
2. Turn 1: active in August = period covers a day of August → 23 subscriptions (includes Ferris, Tortoise, Quill).
3. Turn 2: their combined MRR = 3576.00.
4. Turn 3: same rule for July → 24 subscriptions (Ferris and Tortoise still in; Quill out; the five July churns in).
5. Turn 4: growth plan among the July-active 24 → 9.

## Why the answer is unique
The README fixes both the slash-date convention and the active-in-month definition, so every membership decision is forced; the three slash rows flip exactly one membership each way between the readings and the naive 21/23 contradicts the stated convention. MRR sums over the fixed member set are unique. Answers are uniquely 23, 3576.00, 24, 9.

## Five alternative phrasings
- How many subscribers were active in August
- What was the total MRR of the August actives
- Same count but for July 2026
- How many of the July actives are on growth
- Count active subscriptions for July under the ledger rules
