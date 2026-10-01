## Traps
- TR-DECOY: masters/raw-takes.csv holds the unedited takes EP-043-raw at 921 MB and EP-045-raw at 873 MB. Scanning both files for the biggest number reports 921; README says raw takes are never the master of record and are excluded from the audit, so the biggest published master is EP-043 at 655 MB.

## Reference solution
1. List masters/: episode-log.csv and raw-takes.csv.
2. Read README.md: only episode-log.csv rows are masters of record; raw takes are excluded.
3. Read masters/episode-log.csv: the largest size_mb is EP-043 at 655; raw-takes.csv exists for the unedited takes.


> v2（2026-10-01）：判据改写——output_contains 只留专有名词事实，数量事实移入 output_contains_any 并给多种自然写法（原「数字+量词」锚串对自然语言终答过严）。

## Why the answer is unique
The decoy 921 is a raw take. README states raw takes are never the master of record and are excluded from the audit, so no raw-takes.csv row can be the answer; among published masters the size column peaks at 655 on EP-043, ahead of 604 and 587. The file's role is stated in the README line naming raw-takes.csv as the unedited-takes register. Scope rule plus the size column pin all three facts, leaving no second reading.
