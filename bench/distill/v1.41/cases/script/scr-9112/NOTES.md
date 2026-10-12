## Traps
- perl is not installed, so `perl 脚本/failcount.pl` exits 127; the script has to be reproduced by hand.
- TR-DECOY: FAIL-RETRY and sync-v2 look like FAIL and sync; the script compares fields exactly, a prefix match gives 19.

## Reference solution
1. bash: `perl 脚本/failcount.pl` -> exit 127.
2. read_file 脚本/failcount.pl: counts lines of 日志/*.log whose 2nd field is FAIL and 3rd field is sync.
3. bash: `cat 日志/*.log | awk '$2=="FAIL" && $3=="sync"' | wc -l`
Final answer: failcount.pl 会输出「sync 失败次数: 6」（perl 不可用，我按脚本逻辑用 awk 复算）。

## Why the answer is unique
Fields are space separated and compared exactly in the script.

## Alternative phrasings
1. 跑一下 脚本/failcount.pl，sync 模块失败了多少次？
2. failcount.pl 打印的 sync 失败次数是几？
3. 执行脚本目录里的 failcount.pl，把它输出的次数告诉我。
4. 帮我运行 failcount.pl，得到的 sync 失败次数是多少？
5. 用 failcount.pl 统计一下 sync 失败总数。
