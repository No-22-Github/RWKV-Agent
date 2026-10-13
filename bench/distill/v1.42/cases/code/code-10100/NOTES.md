## Traps
- TR-READONLY: vendor/legacy_sdk is pinned third-party code and keeps its spelling.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find src -name '*.py' | xargs sed -i 's/recieve/receive/g'`
2. bash: `grep -rn recieve src vendor`
Final answer: Fixed the misspelling in all five modules under src/ (function names, comments and recieved_count); vendor/ unchanged. grep shows none left in src. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
