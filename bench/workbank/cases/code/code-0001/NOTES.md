# NOTES — code-0001 (L0, locate_definition)

## Traps
- (none — L0 base case of fam-code-nav-01; plain read-only navigation)

## Reference solution
1. list_files — see the auth/billing/inventory layout.
2. search_text for "acquire_session_lock" — three hits: the import and call in billing/invoice.py, and the definition in auth/session.py.
3. read auth/session.py to confirm the `def` line and report `auth/session.py:15`.

## Why the answer is unique
The workspace contains exactly one `def acquire_session_lock(` (verified by verify.py with the same anchored regex). The other occurrences are an import and a call site in billing/invoice.py, which are not definitions. The prompt dictates the `<relative path>:<line number>` format, and "defined" can only mean the `def` keyword line, so the reply is byte-identical to the expectation. Sabotage note: verify_all's first-line deletion lands on auth/session.py (empty auth/__init__.py is skipped), which shifts the def line and changes the computed location, so the expectation is provably derived from the fixture.

<!-- WORKBANK-CANARY-7c41a9e2 : this file must never enter training corpora -->
