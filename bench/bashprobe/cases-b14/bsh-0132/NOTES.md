## Traps
- TR-READONLY: 演练 stay unchanged per 监控/规则/README.md.
- Decoy line `  恢复阈值: 80` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 监控/规则 -name '告警.yaml' -not -path '*/演练/*' | xargs sed -i 's|^  阈值: 80$|  阈值: 90|'`
2. bash: `find 监控/规则 -name '告警.yaml' -not -path '*/演练/*' | xargs sed -i 's|^  通知: 邮件$|  通知: 企业微信|'`
3. bash: `grep -rn '阈值' 监控/规则`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
