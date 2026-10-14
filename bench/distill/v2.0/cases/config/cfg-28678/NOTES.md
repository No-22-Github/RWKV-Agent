## Traps
- TR-DECOY: The images row recommends 86400 and has the same old TTL as scripts.

## Reference solution
1. Read the basis reviews/cdn-2026-09.md: the new value is 21600.
2. Read infra/cdn.yaml: line 4, `  - path: /static/js
    ttl: 3600`, is the one to change.
3. replace_lines line 4 with `  - path: /static/js
    ttl: 21600`; the rest of the line stays.
4. Read infra/cdn.yaml back to confirm.
Final answer example: infra/cdn.yaml now has ttl 21600 for /static/js, the review's recommendation; /static/img stays at 3600.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
