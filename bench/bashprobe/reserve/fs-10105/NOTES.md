## Traps
- TR-READONLY: pinned-scan-* files carry first-half dates but stay (README.txt).
- Scans from July-December stay in inbox.
- 9 files change; 10 stay byte-identical.

## Reference solution
1. bash: `mkdir -p archive/2025H1 && for f in inbox/scan-2025-0[1-6]-*.pdf; do mv "$f" archive/2025H1/; done`
2. bash: `ls inbox archive/2025H1`
Final answer: Moved the first-half-2025 scans to archive/2025H1; July-December scans and the pinned ones are still in inbox. Listed both folders to confirm. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
