## Traps
- TR-READONLY: 脚本/legacy/old-run.sh stays as it is (README).
- TR-DECOY: source ./lib/colors.sh is a sibling line the README leaves for now.

## Reference solution
1. bash: `find 脚本 -name '*.sh' | grep -v /legacy/ | xargs sed -i 's#^source ./lib/common.sh$#source "$(dirname "$0")/lib/common.sh"#'`
2. bash: `grep -rn 'source' 脚本` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four scripts source lib/common.sh via dirname; legacy/old-run.sh and the colors.sh lines are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 把脚本里的 source ./lib/common.sh 改成相对脚本位置的写法（用 dirname "$0"），legacy 不动，colors 那行先不管。
2. 脚本目录的四个 .sh 里 common.sh 的 source 路径换成 README 给的形式，改完回复 DONE。
3. 批量修正 source ./lib/common.sh，使它不依赖当前目录，legacy 目录例外。
4. 让备份、发布、清理、巡检四个脚本从自己所在目录加载 lib/common.sh，其余保持原样。
5. Make the four scripts load lib/common.sh relative to their own location as the README shows, skipping legacy.
