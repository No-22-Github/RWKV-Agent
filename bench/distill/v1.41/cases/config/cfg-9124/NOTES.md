## Traps
- TR-READONLY: envs/_template stays as it is; REPLICA_HOST=db-old.internal is a look-alike line the README says to keep (a global `s/db-old.internal/db-new.internal/` changes it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find envs -name db.env | grep -v /_template/ | xargs sed -i 's/^DB_HOST=db-old\.internal$/DB_HOST=db-new.internal/'`
2. bash: `grep -rn HOST envs`
Turn 2:
1. bash: `sed -i 's/^DB_HOST=db-new\.internal$/DB_HOST=db-old.internal/' envs/staging/db.env && sed -i 's/^DB_HOST=db-new\.internal$/DB_HOST=db-dev.internal/' envs/dev/db.env`
2. bash: `grep -rn HOST envs`
Final answers: DONE (turn 1: prod, qa, staging, dev on db-new.internal; turn 2: staging back on db-old.internal, dev on db-dev.internal).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. Switch DB_HOST to db-new.internal everywhere except the template, then revert staging and give dev its own host.
2. Update the database host in all env files, then staging goes back to the old one and dev gets db-dev.
3. Migrate DB_HOST (leave REPLICA_HOST), afterwards undo it for staging and use db-dev.internal for dev.
4. db-old to db-new in envs, except template; then staging old again and dev db-dev.internal.
5. 把各环境的 DB_HOST 迁到新库，之后 staging 改回旧库、dev 改成 db-dev.internal
