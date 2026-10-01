# doc-8006 (p13 holdout, eval-only)

## Traps
- TR-SUPERSEDE: docs/onboarding.md and the IT notice disagree about the VPN group name; the notice is dated 2026-09-21 and says the old name stopped working on 2026-09-28, so the notice governs and the doc line must use partners-vpn. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read notices/vpn-rename-2026-09.md for the new group name (ref call 1).
2. Read docs/onboarding.md and locate the VPN line (ref call 2).
3. Replace `contractors-vpn` with `partners-vpn` on that line, touching nothing else (ref call 3).

## Why the answer is unique
The new name is stated exactly once in the notice, the old name appears exactly once in the doc, and the needles span from the doc's first line through the replaced line, plus the two lines that follow it, so any other edit - renaming in the wrong place, rewrapping the sentence, touching the notice - produces a different end state. The `equals` pin keeps the notice byte-for-byte.
