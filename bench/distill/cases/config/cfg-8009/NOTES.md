## Traps
- TR-DECOY: poetry.lock lists httpcore 1.0.5 right above httpx; reading the wrong block gives a wrong pin.

## Reference solution
1. Read poetry.lock: httpx is 0.27.2.
2. Read requirements.txt: httpx==0.26.0 on line 2.
3. replace_lines line 2 with `httpx==0.27.2`.
4. Read requirements.txt back.
Final answer: one sentence (requirements.txt now pins httpx==0.27.2 to match poetry.lock), then DONE on its own line. Criteria: exact file content; output contains DONE and 0.27.2.

## Why the answer is unique
The lock has exactly one httpx block; the other pins already match or are not mentioned.
