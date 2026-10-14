## Traps
- TR-READONLY: *-current.log is live (README).
- The 6th and 7th stay where they are.
- 15 files change; 13 stay byte-identical.

## Reference solution
1. bash: `for s in api auth billing; do mkdir -p logs/$s/old; mv logs/$s/$s-2026-09-0[1-5].log logs/$s/old/; done`
2. bash: `find logs -type f | sort`
Final answer: Moved 1-5 September logs into logs/<service>/old/ for api, auth and billing; the 6th/7th and the -current.log files stay. Listed the tree to confirm. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
