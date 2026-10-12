## Traps
- TR-READONLY: 脚本集/lib holds sourced fragments (no shebang) and gets no line. The line goes second, right after the shebang.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find 脚本集 -name '*.sh' | grep -v /lib/ | xargs sed -i '1a set -eu'`
2. bash: `head -n 3 脚本集/*.sh`
Final answer: DONE (五个脚本第二行是 set -eu，lib 未动).
Turn 2:
1. bash: `sed -i '2{/^set -eu$/d}' 脚本集/清理.sh 脚本集/巡检.sh`
2. bash: `head -n 3 脚本集/*.sh`
Final answer: DONE (清理、巡检没有 set -eu，其余三个有).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 给脚本集里的脚本第二行统一加 set -eu（lib 除外），然后清理和巡检两个去掉
2. 按约定给脚本加严格模式那行，之后清理.sh、巡检.sh 里撤销
3. 批量在 shebang 下面插入 set -eu，清理与巡检不要
4. 给独立脚本加 set -eu，再把清理、巡检的那行删掉
5. Add set -eu as line two of every standalone script, then remove it from the cleanup and inspection scripts.
