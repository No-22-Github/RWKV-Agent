## Traps
- TR-READONLY: 文档/CHANGELOG.md is history and keeps its old link (README).
- TR-DECOY: ../旧指南说明/ starts with ../旧指南 but is another directory; the match must include the closing slash.

## Reference solution
1. bash: `ls 文档/*.md | grep -v CHANGELOG | grep -v README | xargs sed -i 's#\](\.\./旧指南/#](../指南/#g'`
2. bash: `grep -rn '指南' 文档` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four pages link to ../指南/; CHANGELOG.md and the ../旧指南说明/ link are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 文档里所有指向 ../旧指南/ 的链接改成 ../指南/，变更记录不动。
2. 旧指南 目录改名为 指南，请同步更新 文档 中安装、配置、排错、升级四页的链接。
3. 批量改写 markdown 相对链接 ](../旧指南/ → ](../指南/，相似名字的目录别误伤。
4. 把文档页面里的旧指南链接换成指南，CHANGELOG 里的历史链接保持原样，完成回复 DONE。
5. Update the markdown links that point to the renamed directory 旧指南 (now 指南) in the four doc pages, skip the changelog.
