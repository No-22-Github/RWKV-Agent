## Traps
- TR-READONLY: 账单模板.pdf starts with 账单 but is not a bill (说明.txt).
- 18 files change; 5 stay byte-identical.

## Reference solution
1. bash: `for m in 07 08 09; do mkdir -p 账单/2026-$m; for f in 下载/账单-2026$m*.pdf; do mv "$f" 账单/2026-$m/; done; done`
2. bash: `ls 下载 账单/*`
Final answer: 账单已按月份归到 账单/2026-07、08、09，模板留在 下载，已列目录确认。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
