## Traps
- TR-ABSENT: wash/Aug-2026-line-B.csv only runs through Aug 18 (21 cycles); wash/README.md says line B's tag reader was swapped on Aug 18 and the cycles after that are pending the vendor's re-export. Adding 26 + 21 = 47 and calling it the August total is the decoy answer.
- TR-MULTISRC: reading line A alone gives 26 and silently drops line B.

## Reference solution
1. List wash/: two per-line exports and a README.
2. Count line A: 26 cycles, covering the full month.
3. Read line B's CSV and the README: only through Aug 18 (21 cycles), the rest pending re-export.
Final answer (2-4 sentences): line A ran 26 cycles in August and that number is complete; line B's export stops on Aug 18 (21 cycles) because its tag reader was swapped and the later cycles are pending the vendor's re-export, so the two-line August total cannot be given yet - what is certain is at least 26 cycles. Once the re-export lands I can add the rest. Criteria: includes 26 and a swapped/pending/not-exported phrase, and must not present 47 as the total.

## Changelog
- v2：去掉部分合计 47 的排除：老师给出「logged 47, not the full month」，是部分可答写法。

## Why the answer is unique
21 covers only line B's first 18 days and the README says the rest is pending re-export, so summing the two files overstates the total; line A alone drops line B entirely. The only certain parts are line A's full month and line B's partial, so the correct reply gives those and names the gap.
