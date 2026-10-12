## Traps
- TR-READONLY: notes/归档 files are referenced by name elsewhere (notes/README.txt).
- TR-DECOY: 会议-0901.markdown.bak ends in .bak, not .markdown.

## Reference solution
1. bash: `for f in $(find notes -name '*.markdown' | grep -v /归档/); do mv "$f" "${f%.markdown}.md"; done`
2. bash: `find notes -type f` to confirm the target files changed and the protected ones did not.
Final answer: DONE (four notes now end in .md; the archive file and the .bak backup keep their names).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. notes 里的 .markdown 笔记统一改成 .md 后缀，归档目录和备份文件别动，检查后回复 DONE。
2. 请把 notes（含子目录）中以 .markdown 结尾的文件重命名为 .md，README.txt 里提到的例外保持原名，完成后回复 DONE。
3. 新站点只认 .md，帮我把 notes 下的 .markdown 文件全部换后缀，不要改文件内容，核对后回复 DONE。
4. 批量重命名：notes/**/*.markdown → *.md，但 notes/归档 不动，.bak 也不属于笔记，改完确认并回复 DONE。
5. notes 目录里把文件后缀 .markdown 改为 .md，按 README 的说明跳过归档，然后检查并回复 DONE。
