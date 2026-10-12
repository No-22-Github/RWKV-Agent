## Traps
- TR-READONLY: env/prod.env switches at the Saturday maintenance window (env/README.md).
- TR-DECOY: REPLICA_DB_HOST=db-old.internal contains DB_HOST=db-old.internal as a substring and is migrated by the DBAs; an unanchored sed would change it.

## Reference solution
1. bash: `find env -name '*.env' | grep -v prod.env | xargs sed -i 's/^DB_HOST=db-old.internal$/DB_HOST=db-new.internal/'`
2. bash: `grep -rn DB_HOST env` to confirm the target files changed and the protected ones did not.
Final answer: DONE (dev, test, staging and qa now use db-new.internal; prod.env and every REPLICA_DB_HOST are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. env 里的 .env 文件把 DB_HOST 换成 db-new.internal，README 里标注暂缓的别改，改完确认并回复 DONE。
2. 批量修改 env/*.env 的 DB_HOST（db-old.internal → db-new.internal），副本主机那一项不属于本次，检查后回复 DONE。
3. 各环境的数据库主机地址要切到 db-new.internal，只改 DB_HOST 这个键；env/README.md 说不动的保持原样，完成后回复 DONE。
4. 把 env 目录下 DB_HOST=db-old.internal 全部换成新地址 db-new.internal，prod 暂时跳过，核对后回复 DONE。
5. 更新 env 下的环境文件：DB_HOST 指向 db-new.internal，其余键不变，按 README 的说明排除例外，然后回复 DONE。
