## Traps
- TR-READONLY: 归档/2024版 stay unchanged per 培训资料/README.md.
- 钉钉号 also starts with 钉钉 but is a personal account id; only 钉钉群 changes.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 培训资料 -name '*.md' -not -path '*/归档/*' | xargs sed -i -E 's/钉钉群/企业微信群/g'`
2. bash: `grep -rnF '企业微信群' 培训资料`
Final answer: 已全部改完，保护范围和容易误伤的写法都保留，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
