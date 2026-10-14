## Traps
- TR-READONLY: 旧话术/2023版 stay unchanged per 客服话术/README.md.
- The fax number contains 400-800-1234 as a substring (…12340); an unbounded replace corrupts it.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 客服话术 -name '*.md' -not -path '*/旧话术/*' | xargs sed -i -E 's/400-800-1234([^0-9]|$)/400-800-5678\1/g'`
2. bash: `grep -rnF '400-800-5678' 客服话术`
Final answer: 已全部改完，保护范围和容易误伤的写法都保留，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
