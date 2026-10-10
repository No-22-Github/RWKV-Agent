## Traps
- TR-DECOY: requests-oauthlib (2.0.0) is listed right before requests in the lock.

## Reference solution
1. Read the basis poetry.lock: the new value is 2.32.3.
2. Read requirements.txt: line 2, `requests==2.31.0`, is the one to change.
3. replace_lines line 2 with `requests==2.32.3`; the rest of the line stays.
4. Read requirements.txt back to confirm.
Final answer example: requirements.txt now pins requests==2.32.3, the version in poetry.lock.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
