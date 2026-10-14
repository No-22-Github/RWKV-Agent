## Traps
- TR-READONLY: pg_dump备份.sql is an untouched backup (说明.md).
- TR-DECOY: public_id (a column) and the comment word 公开/public must not be rewritten; only the `public.` qualifier is.

## Reference solution
1. bash: `ls 数据库/视图/*.sql | grep -v pg_dump | xargs sed -i 's/public\./app./g'`
2. bash: `grep -rn 'public\|app\.' 数据库` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four view files reference app.base_table; pg_dump备份.sql, public_id and the comments are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 视图 SQL 里的 public.xxx 全部改成 app.xxx，备份别动，public_id 这种列名不算。
2. 把模式前缀 public. 换成 app.（四个视图文件），pg_dump 备份保持原样。
3. 数据库/视图 下的 SQL 同步新的模式名 app，改完回复 DONE，说明.md 里点名的不改。
4. 批量替换 `public.` 为 `app.`，注意列名 public_id 和备份文件。
5. Switch the schema qualifier from public. to app. in the view SQL files, except the dump backup, reply DONE.
