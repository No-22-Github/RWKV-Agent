## Traps
- TR-READONLY: 旧版 stay unchanged per 打印模板/README.md.
- Decoy line `备用纸张=A4` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 打印模板 -name '设置.ini' -not -path '*/旧版/*' | xargs sed -i 's|^纸张=A4$|纸张=A5|'`
2. bash: `grep -rn '纸张' 打印模板`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
