## Traps
- TR-READONLY: replica-* folders carry the same line and are excluded by config/README.md.
- connect_ms = 100 also ends in '= 100'; only the max_connections line changes.
- 5 files change; 3 stay byte-identical.

## Reference solution
1. bash: `find config -name db.ini -not -path '*/replica-*' | xargs sed -i 's/^max_connections = 100$/max_connections = 200/'`
2. bash: `grep -rn connections config`
Final answer: Raised max_connections to 200 in the five service db.ini files; replica folders and connect_ms untouched, verified with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
