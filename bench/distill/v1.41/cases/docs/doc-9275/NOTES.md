## Traps
- TR-READONLY: 术语表.md and 更新日志.md keep the old word. The README itself quotes 「插件」 in its text, so it also still contains the old term: the turn-2 list is 术语表, 更新日志 and README.
- Turn 2 asks about the whole tree, including files that already differed before turn 1.

## Reference solution
Turn 1:
1. bash: `sed -i 's/插件/扩展/g' 文档/入门.md 文档/进阶.md 文档/FAQ.md 文档/发布.md 文档/迁移.md`
2. bash: `grep -rc 插件 文档`
Final answer: DONE (五页已改为扩展).
Turn 2:
1. bash: `grep -rl 插件 文档`
Final answer: 术语表、更新日志、README.

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 改完之后，哪些文件里还留着「插件」？
2. 文档里现在哪几份还含「插件」，列文件名
3. 列出仍然包含「插件」的文档文件
4. 还有哪些文档没换掉「插件」这个词？
5. Which files under 文档 still contain 插件 now?
