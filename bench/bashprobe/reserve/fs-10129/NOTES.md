## Traps
- TR-READONLY: 素材/外部/ keeps the partner's original name.
- Turn 2 renames only 主图/ files.
- 15 files change; 5 stay byte-identical.

## Reference solution
1. bash: `for f in $(find 素材 -name '*.PNG' -not -path '*/外部/*'); do mv "$f" "${f%.PNG}.png"; done`
2. bash: `for f in 素材/主图/图*.png; do mv "$f" "素材/主图/主图_${f##*/图}"; done`
3. bash: `find 素材 -type f | sort`
Final answer: 扩展名已统一为 .png，主图目录的文件已改成 主图_NN.png，外部目录未改，已列出确认。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
