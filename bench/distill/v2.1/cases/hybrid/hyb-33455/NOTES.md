## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
先只留 3 条记录；之后恢复 3 条注释到原位，不恢复空行。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 hosts.txt 里的注释行和空行都删掉，只留主机记录。
2. 麻烦问下：把 hosts.txt 里的注释行和空行都删掉，只留主机记录。
3. 把 hosts.txt 里的注释行和空行都删掉，只留主机记录。（简单说就行）
4. 你好，把 hosts.txt 里的注释行和空行都删掉，只留主机记录。
5. 还有件事：把 hosts.txt 里的注释行和空行都删掉，只留主机记录。
