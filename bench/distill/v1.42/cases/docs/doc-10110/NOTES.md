## Traps
- TR-READONLY: 模板.md keeps its draft marker.
- Turn 2 adds the header to the four reviewed files only, not to 已发布/考勤.md.
- 4 files change; 3 stay byte-identical.

## Reference solution
1. bash: `find 制度 -name '*.md' ! -name 模板.md ! -name 说明.md | xargs sed -i '/^（草稿，待审）$/d'`
2. bash: `for f in 制度/入职指南.md 制度/报销流程.md 制度/请假制度.md 制度/IT支持.md; do sed -i '1i <!-- 2026-09 审定 -->' "$f"; done`
3. bash: `grep -rn -e 草稿 -e 审定 制度`
Final answer: 四份制度的草稿标记已删除并在首行加了审定注释，模板和已发布目录未改，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
