## Traps
- TR-READONLY: 项目/归档2023 is frozen (README); docs/build/ and rebuild/ contain build/ as a substring, only the whole line `build/` changes.

## Reference solution
1. bash: `find 项目 -name .gitignore | grep -v /归档2023/ | xargs sed -i 's#^build/$#out/#'`
2. bash: `grep -rn 'build\|out' 项目` to confirm the target files changed and the protected ones did not.
Final answer: DONE (订单, 会员, 报表 and 推送 ignore out/; 归档2023 and the docs/build/ and rebuild/ lines are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 项目里的 .gitignore，把 build/ 这一条换成 out/，历史归档仓库除外。
2. 构建目录改名为 out，请同步各项目的 gitignore（只改整行 build/），README 里点名的别动。
3. 批量把 .gitignore 中的 build/ 替换成 out/，文档站的 docs/build/ 不改，改完回复 DONE。
4. 项目下四个仓库的忽略规则 build/ 要改为 out/，归档2023 保持原样。
5. Rename the ignored build/ entry to out/ in the project .gitignore files, skipping the frozen archive, reply DONE.
