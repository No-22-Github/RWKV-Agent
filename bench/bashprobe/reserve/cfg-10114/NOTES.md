## Traps
- TR-READONLY: 测试店 stay unchanged per 门店配置/README.md.
- Decoy line `备注=小票抬头=星河便利 为旧版` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 门店配置 -name '收银.ini' -not -path '*/测试店/*' | xargs sed -i 's|^小票抬头=星河便利$|小票抬头=星河便利（新）|'`
2. bash: `grep -rn '小票抬头' 门店配置`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
