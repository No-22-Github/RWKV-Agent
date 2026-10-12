## Traps
- TR-DECOY: `# 需要 python 环境` and `echo "python ready"` mention python but do not call it; python3 lines are already right. TR-READONLY: 脚本/第三方 is untouched (脚本/README.md); indented calls keep their indentation.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep -lE '^[[:space:]]*python ' 脚本/*.sh | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `grep -lE '^[[:space:]]*python ' 脚本/*.sh | xargs sed -i -E 's/^([[:space:]]*)python /\1python3 /'`
2. bash: `grep -n 'python' 脚本/*.sh`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 有多少个脚本直接用 python 命令？把它们都改成 python3
2. 统计以 python 命令开头的脚本个数，然后把这些命令换成 python3
3. 脚本目录里调用 python（而非 python3）的 .sh 有几个？替换成 python3
4. 数一数还在用 python 命令的脚本，再把这些行里的 python 改成 python3（注释和 echo 不动）
5. How many scripts call plain python at the start of a line? Switch those calls to python3.
