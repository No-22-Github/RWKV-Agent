## Traps
- TR-DECOY: ADR-015 has the same four bullet keys, and its Deciders and Supersedes values equal ADR-014's old ones.
- replace_lines must cover the whole run of 4 lines (start_line 3, end_line 6) and content must have 4 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read docs/adr/decisions.md; the target lines are 3-6.
2. replace_lines start_line 3, end_line 6 with:
   - Status: accepted
   - Date: 2026-09-10
   - Deciders: platform team, SRE
   - Supersedes: ADR-009
3. Read docs/adr/decisions.md back to confirm.
Final answer, one sentence then DONE on its own line: Updated docs/adr/decisions.md lines 3-6 (4 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
