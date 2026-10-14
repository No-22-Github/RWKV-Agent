## Traps
- TR-READONLY: 已下线 stay unchanged per 小程序/页面配置/README.md.
- Decoy line `  "backgroundColor": "#ffffff",` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 小程序/页面配置 -name 'page.json' -not -path '*/已下线/*' | xargs sed -i 's|^  "navigationBarBackgroundColor": "#ffffff",$|  "navigationBarBackgroundColor": "#1677ff",|'`
2. bash: `grep -rn '"navigationBarBackgroundColor"' 小程序/页面配置`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
