## Traps
- TR-NEARNAME: the Hangzhou edge node appears as qcd-hz2 in the three rows before the 09:20 config switch and as qcd-hz-b afterwards; the README says both names are the same machine. Counting only the new name gives 6 and hands the win to qcd-bj1 (8), which is the decoy; merged, qcd-hz-b has 9.

## Reference solution
1. Turn 1: read README.md (qcd-hz2 was renamed to qcd-hz-b on 09-20, same machine), read logs/cdn-edge.log, count cache=ERR rows per node with qcd-hz2 merged into qcd-hz-b: qcd-hz-b 9, qcd-bj1 8. Answer: qcd-hz-b.
2. Turn 2: restrict to 12:00:00 and later: qcd-bj1 7, qcd-hz-b 4. Answer: qcd-bj1.
3. Turn 3: qcd-bj1's first ERR at or after 12:00:00 is 13:07:12. Answer: 13:07.

## Why the answer is unique
The README removes any ambiguity about the two spellings: one node, renamed mid-week, so the merge is mandatory, and no third candidate comes close (other edges do not appear). In the afternoon window the ranking flips because all three legacy-name rows fall in the morning, and the first afternoon error for qcd-bj1 is unambiguously its earliest ERR timestamp after noon.
