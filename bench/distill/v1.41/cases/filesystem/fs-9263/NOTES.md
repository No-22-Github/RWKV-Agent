## Traps
- TR-READONLY: 文档站/发布镜像 keeps its names. TR-DECOY: 旧笔记.markdown.bak is a backup, not a .markdown page; 参考/变更.md is already .md.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `for f in $(find 文档站 -name '*.markdown' | grep -v /发布镜像/); do mv "$f" "${f%.markdown}.md"; done`
2. bash: `find 文档站 -type f`
Final answer: DONE (六个页面改为 .md，发布镜像未动).
Turn 2:
1. bash: `for n in 导入 导出; do mv 文档站/指南/$n.md 文档站/指南/$n.markdown; done`
2. bash: `find 文档站 -type f`
Final answer: DONE (导入、导出改回 .markdown，安装等仍为 .md).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 文档站里的 .markdown 全部改成 .md（镜像除外），然后导入页和导出页再改回去
2. 把文档页统一成 .md 扩展名，指南里的导入导出两页之后恢复 .markdown
3. markdown 扩展名换成 md，导入和导出页因为旧生成器要还原
4. .markdown → .md，发布镜像不动；导入、导出两个文件撤销
5. Rename .markdown pages to .md except the mirror, then restore .markdown for the import and export guides.
