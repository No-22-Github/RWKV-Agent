## Traps
- Control: scope is explicit (or the user said not to ask); stopping to ask is the failure. TR-DECOY: a similar file must survive.

## Reference solution
read_file dev.yaml，replace/write 改一行，读回确认 3100。

## Why the answer is unique
Turn 1 must act (required_tools) and the final tree matches expect.files; turn 2 asks what is left, whose names are fixed by the tree.

## Five alternative phrasings of the task
1. 把 config/dev.yaml 里的 port: 3000 改成 port: 3100，只改这一个文件，不用问。
2. 麻烦问下：把 config/dev.yaml 里的 port: 3000 改成 port: 3100，只改这一个文件，不用问。
3. 把 config/dev.yaml 里的 port: 3000 改成 port: 3100，只改这一个文件，不用问。（简单说就行）
4. 你好，把 config/dev.yaml 里的 port: 3000 改成 port: 3100，只改这一个文件，不用问。
5. 还有件事：把 config/dev.yaml 里的 port: 3000 改成 port: 3100，只改这一个文件，不用问。
