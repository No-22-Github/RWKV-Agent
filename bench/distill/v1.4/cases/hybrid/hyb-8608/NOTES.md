## Traps
- TR-DECOY: The page also shows the previous 1.25 (the file's current value) and the large letter rate 2.70; the history blog is from 2023.

## Reference solution
1. Read the basis https://harbormail.example/rates: the new value is 1.35.
2. Read config/postage.ini: line 2, `standard_letter = 1.25`, is the one to change.
3. replace_lines line 2 with `standard_letter = 1.35`; the rest of the line stays.
4. Read config/postage.ini back to confirm.
Final answer example: standard_letter in config/postage.ini is now 1.35 EUR, per the Harbor Mail rates page (from 2026-09-15); large_letter stays 2.70. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.

## Five alternative phrasings of the task
1. Harbor Mail rates
2. Harbor Mail standard letter postage
3. Harbor Mail domestic rates 2026
4. Harbor Mail price list
5. Harbor Mail postage increase
