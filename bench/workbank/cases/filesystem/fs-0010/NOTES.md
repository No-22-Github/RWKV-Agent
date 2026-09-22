## Traps
- TR-DECOY: exports/campus_north_log.txt and exports/archive/campus_north_log.txt share their file name in two folders and both open with "Campus North export log", but their last line differs (2026-03-12 vs 2026-03-15), so their stored bytes are not identical. A model that finds duplication by file name, or stops at the first pair that looks like a copy, reports exports/campus_north_log.txt (the recorded decoy); the byte-identical pair is the two .csv extracts.

## Reference solution
1. list_files the workspace and see the export tree with its two folders (call 1)
2. read exports/registrar_midterm_2026.csv (call 2)
3. read exports/midterm_export_final.csv; the bytes match the first extract (call 3)
4. answer exports/midterm_export_final.csv, one of the two identical copies (call 4)

## Why the answer is unique
Grouping every file by exact stored bytes leaves exactly one group with more than one member: the two .csv extracts exports/registrar_midterm_2026.csv and exports/midterm_export_final.csv. The two campus_north_log.txt files differ on their last line, and every other file is unique. The README audit rule fixes the criterion as identical bytes, so the answer is one of the two identical paths. verify.py regroups the fixture by content and returns the lexicographically first path of the single multi-member group.

<!-- WORKBANK-CANARY-a1d6f0c3 : this file must never enter training corpora -->
