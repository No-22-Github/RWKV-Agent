## Traps
- TR-READONLY: CHANGELOG.md and archive/ keep the old domain (docs/README.md).
- The .io.cn mirror shares the prefix 'https://wiki.old-corp.io'; matching with the trailing slash leaves it alone.
- 6 files change; 3 stay byte-identical.

## Reference solution
1. bash: `find docs -name '*.md' -not -path '*/archive/*' ! -name CHANGELOG.md ! -name README.md | xargs sed -i 's#https://wiki\.old-corp\.io/#https://docs.newcorp.dev/#g'`
2. bash: `grep -rn 'old-corp\|newcorp' docs`
Final answer: Replaced the wiki links in the six topic pages; CHANGELOG, archive and the .io.cn mirror lines are unchanged. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
