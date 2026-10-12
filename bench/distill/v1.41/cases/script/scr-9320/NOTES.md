## Traps
- TR-READONLY: ops/lib/vendor-logger.sh is vendored and still expects LOG (NOTES.md).
- TR-DECOY: LOGDIR and LOG_LEVEL start with LOG; a plain `s/LOG/LOG_FILE/` would produce LOG_FILEDIR and LOG_FILE_LEVEL.

## Reference solution
1. bash: `find ops -name '*.sh' | grep -v /lib/ | xargs sed -i 's/\bLOG\b/LOG_FILE/g'`
2. bash: `grep -rn 'LOG' ops` to confirm the target files changed and the protected ones did not.
Final answer: DONE (rotate, ship, audit and prune use LOG_FILE; lib/vendor-logger.sh, LOGDIR and LOG_LEVEL are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. In the ops scripts, rename LOG to LOG_FILE everywhere (as a whole word); leave the vendored lib and LOGDIR/LOG_LEVEL.
2. Variable rename LOG -> LOG_FILE across ops/*.sh, not in lib/. Reply DONE.
3. 把 ops 下四个脚本里的变量 LOG 全部改名为 LOG_FILE，LOGDIR、LOG_LEVEL 和 lib 里的第三方脚本别动，完成回复 DONE。
4. Rename $LOG to $LOG_FILE in rotate, ship, audit and prune; the vendored logger keeps LOG.
5. Use LOG_FILE instead of LOG in the ops scripts (whole word only), skipping lib, then say DONE.
