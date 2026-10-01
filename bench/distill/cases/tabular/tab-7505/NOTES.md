## Traps
- TR-DECOY: data/extract_batches.tsv carries "Wildflower Raw" beside the target "Wildflower". Summing the Raw rows (or both) gives 9330.93. August rows are further distractors around the September target.

## Reference solution
1. data_query: {"path":"data/extract_batches.tsv","filter":{"batch_month":"2026-09","honey_type":"Wildflower"},"operation":"sum","field":"wholesale_value"} -> 7899.09.
2. Reply with the number 7899.09 only.

## Why the answer is unique
The decoy 9330.93 is the Wildflower Raw total, but the task names the Wildflower honey, and the README fixes the naming: Wildflower is the standard blend, Raw is a separate jar line. Every row carries exactly one honey type, so no reading mixes them. August rows fail the month condition. The answer is 7899.09.
