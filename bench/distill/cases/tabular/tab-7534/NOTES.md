## Traps
- TR-NEARNAME (recovery case, the recovery behaviour is the point): the prompt only says "the honey the co-op will actually pay for"; no column is called that. The register keeps a near-name pair, gross_kg (weight as delivered) and settled_kg (weight after moisture correction that the payment is worked out from). A first aggregate over a guessed column name fails with an error like `field "..." is missing`; a filter over a missing column returns matched_rows 0. The model recovers from the error or the empty result: issue one data_query without operation and select to list the real headers (or spend the single allowed read_file on the header), then re-query with settled_kg. README states settled_kg is what the payment is worked out from.
- Aggregating gross_kg instead gives 4832.20; the correct answer is the settled_kg total 4543.45.

## Reference solution
1. Read README.md: gross_kg is the delivered weight; settled_kg is what the co-op pays on.
2. Query: {"path":"data/honey_intake_2026-09.csv","filter":{"intake_month":"2026-09"},"operation":"sum","field":"settled_kg"}, which gives 4543.45. (If the first guessed column errors: send one data_query without operation and select to see the headers, then re-query.)
3. Final answer: 4543.45 alone.

## Why the answer is unique
The decoy 4832.20 is the gross_kg total, i.e. the unprocessed delivered weight. The prompt asks for the honey the co-op pays for, and README ties the payment to settled_kg; the two columns differ on every row, so answering from gross_kg does not hold up. August rows are excluded by the month filter. The answer is 4543.45 alone.
