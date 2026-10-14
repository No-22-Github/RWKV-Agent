## Traps
- TR-READONLY: sql/generated/ is tool output.
- refunds.sql already has the header; adding it again is wrong.
- 4 files change; 3 stay byte-identical.

## Reference solution
1. bash: `for f in sql/reports/*.sql; do grep -q '^-- owner: data-platform$' "$f" || sed -i '1i -- owner: data-platform' "$f"; done`
2. bash: `head -n 1 sql/reports/*.sql`
Final answer: Added the owner header to the four report files that lacked it; refunds.sql already had it and generated/ is untouched. Checked the first line of each. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
