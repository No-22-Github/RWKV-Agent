## Traps
- none: L0 baseline. The minutes hold exactly one "Action items" section with three open items and a single meeting date; there is no second minutes file, no done markers, and no conflicting wording.
## Reference solution
1. list_files (1)
2. read_file Minutes-2026-06-08-hr-operations.md (2)
3. write_file tasks/todo.md: header "# Open action items - 2026-06-08" (date read from the minutes title) plus the three item lines (3)
## Why the answer is unique
The minutes contain a single "Action items" section; the meeting date appears once, in the title. The prompt pins the header format and asks the model to keep each item's wording, so the contains substrings in expect.files are unambiguous. verify.py recomputes the expected todo from the fixture and derives the ISO date from the minutes title line, so corrupting that line is detected (verify exits non-zero).

<!-- WORKBANK-CANARY-7c2e91af : this file must never enter training corpora -->
