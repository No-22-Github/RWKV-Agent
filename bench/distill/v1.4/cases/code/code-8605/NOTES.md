## Traps
- TR-DECOY: pydantic-core (2.20.1) sits on the next line of the lock and would be wrong.

## Reference solution
1. Read the basis requirements.lock: the new value is 2.8.2.
2. Read pyproject.toml: line 4, `pydantic==2.5.3`, is the one to change.
3. replace_lines line 4 with `pydantic==2.8.2`; the rest of the line stays.
4. Read pyproject.toml back to confirm.
Final answer example: pyproject.toml now pins pydantic==2.8.2 as in requirements.lock; httpx was left untouched.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
