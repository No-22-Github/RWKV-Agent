## Traps
- TR-DECOY: notes.tmp.bak ends in .bak, not .tmp; projects/_trash is not a project. TR-READONLY: *.keep.tmp stay (projects/README.md), other projects' .tmp files stay; turn 1 counts every file ending in .tmp, pinned ones included.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for p in alpha beta gamma delta omega; do echo "$(find projects/$p -name '*.tmp' | wc -l) $p"; done`
Turn 2 (edit, reply DONE):
1. bash: `for f in $(find projects/omega -name '*.tmp' | grep -v '\.keep\.tmp$'); do mv $f projects/_trash/omega/; done`
2. bash: `find projects/omega projects/_trash/omega -type f`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Which project holds the most .tmp files? Move them (pinned ones excepted) into its folder under projects/_trash.
2. Find the project with the biggest pile of .tmp files and sweep them into the trash folder, pinned files excepted.
3. Count .tmp files per project; for the winner move every unpinned .tmp, cache ones included, to projects/_trash/<project>/.
4. Pick the project with the most temp files and relocate them to its _trash folder, but leave *.keep.tmp and the other projects.
5. projects 里哪个项目的 .tmp 文件最多？把它的 .tmp 挪进 projects/_trash 下对应目录，置顶的 .keep.tmp 留下
