## Traps
- TR-READONLY: 说明/archive-2022.md is a snapshot (README).
- TR-DECOY: http://old.docs.example.com and http://docs.example.org are other hosts without https; `s/http:/https:/` would break them.

## Reference solution
1. bash: `ls 说明/*.md | grep -v archive | grep -v README | xargs sed -i 's#http://docs\.example\.com#https://docs.example.com#g'`
2. bash: `grep -rn 'http' 说明` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four pages use https://docs.example.com; the archive and the old.docs and docs.example.org links are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 把文档里 docs.example.com 的 http 链接全改成 https，别的域名和存档不动。
2. 说明下四个页面中的 http://docs.example.com 换成 https://docs.example.com，改完回复 DONE。
3. 批量把 docs.example.com 升级为 https 链接，旧站镜像和示例站保持 http，存档文件原样。
4. 统一该域名的链接协议为 https（四页），README 点名的例外别改。
5. Switch the docs.example.com links to https in the four pages, skipping the archive and the other hosts.
