## Traps
- TR-READONLY: 笔记/归档 keeps its names (笔记/说明.md); 清单.txt.bak merely contains .txt in its name; 草稿 is renamed twice in total (to .md, then back).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `for f in $(find 笔记 -name '*.txt' | grep -v /归档/); do mv "$f" "${f%.txt}.md"; done`
2. bash: `find 笔记 -type f`
Turn 2:
1. bash: `for f in 笔记/草稿/*.md; do mv "$f" "${f%.md}.txt"; done`
2. bash: `find 笔记 -type f`
Final answers: DONE (turn 1: .txt -> .md outside 归档; turn 2: 草稿 files are .txt again).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. 笔记里的 txt 全部换成 md（归档除外），然后草稿文件再换回 txt
2. 把笔记改成 Markdown 扩展名，草稿目录之后恢复成 txt
3. 统一 .md 后，草稿因为脚本要求改回 .txt
4. txt 改 md，归档不动；草稿再还原
5. Rename the notes from .txt to .md except the archive, then turn the drafts back into .txt.
