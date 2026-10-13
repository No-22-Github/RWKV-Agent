## Traps
- TR-READONLY: 合同/模板/ keeps its file name (OA references it).
- 12 files change; 2 stay byte-identical.

## Reference solution
1. bash: `for f in 合同/2025/*' '*.pdf 合同/2026/*' '*.pdf; do d="${f%/*}"; b="${f##*/}"; mv "$f" "$d/${b// /_}"; done`
2. bash: `find 合同 -type f | sort`
Final answer: 2025、2026 两个目录里的合同文件名空格都换成了下划线，模板目录没动，已列出确认。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
