## Traps
- TR-READONLY: packages/vendor-fork/.gitignore is synced from upstream (NOTES.md); web's existing `.env` line is a different entry and the new line is still appended.

## Reference solution
1. bash: `for f in $(find packages -name .gitignore | grep -v /vendor-fork/); do echo .env.local >> "$f"; done`
2. bash: `tail -n 2 packages/*/.gitignore` to confirm the target files changed and the protected ones did not.
Final answer: DONE (core, web, cli and docs end with .env.local; vendor-fork is unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. Append .env.local to each .gitignore in packages, except the one NOTES.md protects.
2. Every packages/*/.gitignore should end with a .env.local line; leave the upstream-synced one alone. Reply DONE.
3. packages 下各包的 .gitignore 末尾加一行 .env.local，NOTES.md 里点名的不改，完成后回复 DONE。
4. Make the four package .gitignore files ignore .env.local by adding it as the last line, skip the vendor fork, say DONE.
5. 给 packages 里的 .gitignore 都追加 .env.local（vendor-fork 除外），改完回复 DONE。
