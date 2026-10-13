## Traps
- TR-READONLY: v1/legacy stay unchanged per docs/api/README.md.
- /api/v2beta/ starts with /api/v2 but is not /api/v2/; matching the slash keeps it.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find docs/api -name '*.md' -not -path '*/v1/*' | xargs sed -i -E 's#/api/v2/#/api/v3/#g'`
2. bash: `grep -rnF '/api/v3/' docs/api`
Final answer: Done across the in-scope files; the protected folder and the look-alike text are unchanged. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
