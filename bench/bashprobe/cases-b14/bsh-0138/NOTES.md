## Traps
- TR-READONLY: 法务/ is changed by legal separately.
- 星河科技园 is a place name that contains the old company name; a plain s/星河科技/星河智能/ turns it into 星河智能园.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 官网文案 -name '*.md' -not -path '*/法务/*' ! -name README.md | xargs sed -i 's/星河科技园/@@园@@/g; s/星河科技/星河智能/g; s/@@园@@/星河科技园/g'`
2. bash: `grep -rn 星河 官网文案`
Final answer: 五个页面里的公司名已改为星河智能，地名星河科技园保留，法务协议没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
