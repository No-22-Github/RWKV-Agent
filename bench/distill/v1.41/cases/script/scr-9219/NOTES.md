## Traps
- TR-READONLY: tools/legacy scripts run on a rescue image without env (tools/README.md).
- TR-DECOY: release.sh writes a hook through a heredoc that contains its own `#!/bin/bash` line, which must not change.

## Reference solution
1. bash: `find tools -name '*.sh' | grep -v /legacy/ | xargs sed -i '1s|^#!/bin/bash$|#!/usr/bin/env bash|'`
2. bash: `grep -rn '#!' tools` to confirm the target files changed and the protected ones did not.
Final answer: DONE (build, deploy, lint and release start with #!/usr/bin/env bash; the legacy scripts and the heredoc line are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. tools 下的脚本解释器行统一换成 #!/usr/bin/env bash（仅第一行），legacy 目录保持不变，检查后回复 DONE。
2. 批量修改 shebang：tools/*.sh 第 1 行的 #!/bin/bash → #!/usr/bin/env bash，heredoc 里的内容别碰，完成后回复 DONE。
3. 请把 tools 里除救援脚本外的所有 .sh 的首行改成 #!/usr/bin/env bash，README 有说明，核对后回复 DONE。
4. 更新 tools 脚本的 shebang 为 env 形式，只动首行，tools/legacy 不动，改完确认并回复 DONE。
5. tools 目录各脚本第一行换成 #!/usr/bin/env bash，其余行包括脚本里写入的钩子内容都保持原样，检查后回复 DONE。
