## Traps
- Turn 3 resets the patch bump: 2.7.4 -> minor = 2.8.0 (not 2.8.5, not 2.7.5 kept). Turn 4 needs both 2.7.4 and 2.8.0 from memory.
- Turn 5 heading must read 2.8.0 and sit above the 2.7.4 entry.

## Reference solution
1. read: 2.7.4; 2. set 2.7.5; 3. set 2.8.0; 4. answer from memory; 5. insert heading.

## Why the answer is unique
Minor bump resets patch to 0: 2.8.0; package.json is pinned entirely; changelog gets a 2.8.0 heading above 2.7.4.

## Five alternative phrasings of the task
- What version is package.json on right now?
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-b12c1ea4
