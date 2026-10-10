## Traps
- TR-DECOY: The cancel and seats answers use similar Yes./No refund/Proration sentences.
- replace_lines must cover the whole run of 2 lines (start_line 4, end_line 5) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read docs/billing-faq.md; the target lines are 4-5.
2. replace_lines start_line 4, end_line 5 with:
   Yes. The change applies immediately.
   The price difference is prorated for the rest of the cycle.
3. Read docs/billing-faq.md back to confirm.
Final answer, one sentence: Updated docs/billing-faq.md lines 4-5 (2 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
