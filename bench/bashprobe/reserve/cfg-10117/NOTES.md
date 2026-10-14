## Traps
- TR-READONLY: third_party/pdf-render stay unchanged per apps/README.md.
- Decoy line `# FROM node:18-alpine used before 2026` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find apps -name 'Dockerfile' -not -path '*/third_party/*' | xargs sed -i 's|^FROM node:18-alpine$|FROM node:20-alpine|'`
2. bash: `grep -rn 'FROM node' apps`
Final answer: Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
