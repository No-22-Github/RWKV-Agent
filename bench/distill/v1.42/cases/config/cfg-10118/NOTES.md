## Traps
- TR-READONLY: 沙箱 stay unchanged per 渠道配置/README.md.
- Decoy line `退款回调地址=https://pay.old.example.cn/notify` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 渠道配置 -name '支付.conf' -not -path '*/沙箱/*' | xargs sed -i 's|^回调地址=https://pay\.old\.example\.cn/notify$|回调地址=https://pay.example.cn/v2/notify|'`
2. bash: `grep -rn '回调地址' 渠道配置`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
