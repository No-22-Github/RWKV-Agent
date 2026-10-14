## Traps
- TR-READONLY: third_party/ is never bumped.
- The left-pad dependency is also pinned to 1.4.2; s/1.4.2/1.5.0/ would change it.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find packages -name package.json | xargs sed -i 's/^  "version": "1.4.2",$/  "version": "1.5.0",/'`
2. bash: `grep -rn '1\.4\.2\|1\.5\.0' packages third_party`
Final answer: Bumped the version field to 1.5.0 in the five packages; the left-pad pins and third_party stay at 1.4.2. Verified with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
