# NOTES — code-0009 (L0, locate_definition)

## Traps
- (none — L0 base case of fam-code-edge-03; plain read-only navigation)

## Reference solution
1. list_files — see the dispatch/, routing/ and ops/ layout.
2. search_text for "is_handoff_open" — the definition in dispatch/handoff.py plus an import and a call in routing/planner.py.
3. read dispatch/handoff.py to confirm the `def` line and report `dispatch/handoff.py:12`.

## Why the answer is unique
The workspace holds exactly one `def is_handoff_open(` (verify.py proves it with the same anchored regex). The other occurrences are the import and the call site in routing/planner.py, neither of which is a definition, and the constant names in dispatch/handoff.py are not the function. The prompt fixes the reply shape as `<relative path>:<line number>`, so "defined" can only mean the `def` keyword line and the answer is byte-identical to the expectation.

Answer: `dispatch/handoff.py:12`.

## Reviewer notes
- Sabotage coupling: among the rank-9 fixtures (only `.py` files and the extensionless `readme`) the alphabetically first non-empty file is dispatch/handoff.py, so verify_all deletes its first line (the module docstring) and the def shifts from line 12 to 11 — the computed location changes and the expectation is provably derived from the fixture. All `__init__.py` placeholders are empty so they are skipped by the probe.
- Constant values (405, 1185, 96, 275) were chosen to differ from the rest of the code family for the fixture-number-set dedup check.

<!-- WORKBANK-CANARY-3f8a1c04 : this file must never enter training corpora -->
