# NOTES — code-0003 (L1, find_callers, TR-DECOY)

## Traps
- TR-DECOY: release_stale_inventory_holds has exactly 3 live call sites (auth/bootstrap.py line 1 cold-start wiring, sweep_and_notify in inventory/holds.py, settle_batch in billing/settlement.py), but two more paren-shaped mentions exist: a commented-out retired call at the bottom of inventory/holds.py and the callee name with parens inside the log.info message string in billing/settlement.py. A grep-and-count pass that skips only the def line yields the decoy 5 (6 if the def line is counted too).

## Reference solution
1. search_text for "release_stale_inventory_holds" — six mention lines across auth/bootstrap.py, billing/settlement.py, inventory/holds.py.
2. read inventory/holds.py — the def plus the internal caller in sweep_and_notify; the commented legacy call at the bottom is not code.
3. read billing/settlement.py — the settle_batch call is live; the second mention sits inside the log.info format string.
4. read auth/bootstrap.py — the module-level cold-start line is a real invocation, completing the count of 3.

## Why the answer is unique
"Call sites that invoke the function" admits only actual call expressions. verify.py parses each .py fixture with ast and counts Call nodes named release_stale_inventory_holds: comments and string literals are not call expressions, and the def is a FunctionDef, so the count is exactly 3. Every other mention is visibly a comment or a log format string, so no second consistent reading produces a different number.

## Reviewer notes
- Fixture coupling to the bank's sabotage test: the expected count 3 must not appear as a numeric token anywhere in the fixture (otherwise verify_all's number+1 corruption would be undetectable), and the alphabetically first non-empty file must lose a counted line when its first line is deleted — hence auth/bootstrap.py opens with the module-level call (an idiomatic import-for-side-effect wiring module) and the empty auth/__init__.py sorts before it and is skipped. This placement is load-bearing, not sloppiness.
- Constants were chosen to avoid any bare "3"/"3.0"/"03" token: 45, 30, 15, 6, 8, 20, 2026-02.
