## Traps
- TR-DECOY: `payments_legacy/` sits next to `payments/` and holds a frozen copy of the same settlement module, with three LEDGER-PINNED lines that read exactly like the ones in scope. Counting annotated lines over the whole workspace gives 7 instead of 4.

## Reference solution
1. List the workspace: the two top-level packages are `payments/` and `payments_legacy/` (call 1).
2. Read `payments/__init__.py`: one annotated line, "exports stay pinned to the 2024-11 cutover calendar" (call 2).
3. Read `payments/window.py`: one annotated line, "the ledger rejects bookings dated past the epoch window" (call 3).
4. Read `payments/settlement.py`: two annotated lines, "booking still goes through the frozen calendar object" and "the slip layout is fixed by the ledger contract" (call 4). The payments package therefore holds 1 + 1 + 2 = 4 annotated lines.

## Why the answer is unique
The count is 4. The question asks for annotated lines inside the payments package, and in Python a package is the directory that carries its `__init__.py` together with its submodules, so the payments package is exactly `payments/__init__.py`, `payments/window.py` and `payments/settlement.py`; the prompt names no other package. `payments_legacy/` is a separate top-level package with its own `__init__.py`, nothing in `payments/` imports it and it imports nothing from `payments/`, and its own docstring records that it is a frozen copy kept beside `payments/` for audit reference only. A line in `payments_legacy/settlement.py` therefore cannot be a line of the payments package, so the workspace-wide total of 7 answers a question that was not asked. Inside `payments/` each of the four annotated lines carries the marker exactly once and no other line mentions it, so 4 is the only count the prompt admits.
