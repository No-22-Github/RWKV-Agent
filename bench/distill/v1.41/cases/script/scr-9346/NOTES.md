## Traps
- TR-DECOY: `# !/bin/sh` (space) and a shebang on line 2 are not shebangs; `#!/bin/bash` is one. TR-READONLY: scripts/vendor is untouched (scripts/README.md). Turn 3 removes exactly the first line of the three ci-* scripts, which had no shebang originally.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in scripts/*.sh; do head -n 1 $f | grep -q '^#!' || echo $f; done | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `for f in scripts/*.sh; do head -n 1 $f | grep -q '^#!' || sed -i '1i #!/bin/sh' $f; done`
2. bash: `head -n 1 scripts/*.sh`
Turn 3 (edit, reply DONE):
1. bash: `for f in scripts/ci-*.sh; do sed -i '1d' $f; done`
2. bash: `head -n 1 scripts/*.sh`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Count the scripts in scripts whose first line is not a shebang, give them #!/bin/sh, then undo it for the ci scripts.
2. Which top-level .sh files have no #! line? Add one, but the ci-* files must end up as they were.
3. How many scripts need a shebang? Insert #!/bin/sh at the top of each, afterwards strip it from ci-lint, ci-test and ci-deploy.
4. Find shell scripts starting without #!, fix them with #!/bin/sh and revert the ci ones.
5. scripts 下有多少个脚本第一行没有 #!？都补上 #!/bin/sh，再把 ci- 开头的撤掉
