## Traps
- After the reject the disk still has the original file. A model that believes WORKERS=8 is still staged (or that LOG_LEVEL is already debug) ends with the wrong final file.
- Turn 1 is a transition turn and has no expectation.

## Reference solution
1. Turn 1: read, edit both values (2-3 calls).
2. After reject: read the file (original), change only LOG_LEVEL=debug (2 calls).
Final: LOG_LEVEL=debug, WORKERS=2, other lines unchanged.

## Why the answer is unique
The user says to apply only the log level change; the full file content is pinned, so WORKERS=8 or a still-info LOG_LEVEL fails.

## Five alternative phrasings of the task
- In app/.env, switch LOG_LEVEL to debug and bump WORKERS up to 8.
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-adaccf5c
