## Traps
- TR-DECOY: [retention_cold] has keep_days = 90 and conf/backup.ini.bak says 7.

## Reference solution
1. read_file conf/backup.ini
Final answer: [retention] 段 keep_days 为 14 天（冷备份段是 90，.bak 里的 7 是旧值）。

## Why the answer is unique
The user names conf/backup.ini; only its live line holds the answer. [retention_cold] has 90 and the .bak copy has 7.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash.

## Five alternative phrasings of the task
1. 看 conf/backup.ini：普通备份保留几天（[retention] 段的 keep_days）？
2. conf/backup.ini 的 [retention] keep_days 是多少？
3. 按 conf/backup.ini，备份默认保留多少天？
4. 帮我读一下 conf/backup.ini，[retention] 里写的保留天数。
5. conf/backup.ini 规定的保留期限是几天？看 [retention] 段。
