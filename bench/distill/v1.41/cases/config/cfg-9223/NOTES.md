## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value (db-prod-01.internal).

## Reference solution
1. read_file on the named file.
Final answer: DB_HOST 是 db-prod-02.internal（.bak 备份里是 db-prod-01，不是当前值）。

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. 生产环境数据库主机是哪个？config/prod.env 里写着。
2. config/prod.env 的 DB_HOST 是什么？
3. 看一下 config/prod.env，数据库连的是哪台机器？
4. prod.env 里配置的 DB_HOST 值是多少？
5. 告诉我 config/prod.env 里数据库主机名。
