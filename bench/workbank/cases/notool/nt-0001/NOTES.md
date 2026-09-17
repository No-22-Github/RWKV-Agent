## Traps
- None. L0 base case of fam-nt-reflex-01: the workspace is empty and every
  conversion input lives in the prompt, so the correct run makes zero tool
  calls. Any call against the twelve-tool directory (including a calculator)
  fails the no-call contract even when the arithmetic is right.
- Careless value a reviewer should expect in failing traces: 9000 (treating
  MiB and MB as the same unit), i.e. 2.5 * 3600.

## Reference solution
No steps; ref_calls is 0. The reference solution never touches the tool
catalog: 2.5 MiB/s = 2.5 * 1,048,576 B/s = 2,621,440 B/s; one hour is 3,600 s,
so 9,437,184,000 B/h; in SI megabytes (10^6 B) that is 9437.184 MB/h. Reply
with the bare number 9437.184 (the expected_number judge parses the whole
reply as one plain number, so no units in the reply).

## Why the answer is unique
MiB is the IEC binary megabyte (2^20 bytes) and MB is the SI decimal megabyte
(10^6 bytes); both are standard definitions, so the mixed-unit conversion has
exactly one value, 9437.184. The prompt supplies every input, so no workspace
or lookup path can change the number, and the tolerance only absorbs rounding
(9437.18 still passes).
Family note: the true-lookup sister case of this family is hyb-0001 (hybrid
scenario) — the variant where the same reflex skeleton hides an answer that
genuinely requires a tool call lives outside notool by design.

<!-- WORKBANK-CANARY-3d7a91e4 : this file must never enter training corpora -->

## Reviewer notes (post gate-fail repair)
- v2 (closeout): removed "Without using any tools, " from the prompt — it is a TR-NOTOOLNEED forbidden phrase ("without tools") that leaked in because the case declares no traps and lint only checked declared traps. The no-call requirement is already judged by expect tools:[], so the phrase was a redundant hint.
- v2: require_active_no_call removed bank-wide (native-chat wire has no no_tool exit; the judgment is now plain zero tool calls via tools:[], protocol-agnostic). - v2: unit task changed MiB/s->MB/h to MiB/s->MiB/h (same unit): the binary/decimal distinction was an undeclared trap on an L0 and calculator use was punished; the DEC axis (reflexive tool call) is now measured without a hidden computation trap.
