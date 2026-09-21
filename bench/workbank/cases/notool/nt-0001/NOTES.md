## Traps
- None. L0 base case of fam-nt-reflex-01: the workspace is empty and every
  conversion input lives in the prompt, so the correct run makes zero tool
  calls. Calls are reported as call discipline (no_call_accuracy /
  active_no_call), not as task success, so a correct figure reached after a
  reflexive calculator call still answers the question correctly and is
  still recorded as having broken the zero-call contract.
- Careless value a reviewer should expect in failing traces: 150 (converting
  per second to per minute, 2.5 * 60), or any figure that applies the
  binary/decimal conversion this case deliberately does not ask for.

## Reference solution
No steps; ref_calls is 0. The reference solution never touches the tool
catalog: the rate is asked for in the same unit it is given in, so one hour of
2.5 MiB/s is 2.5 * 3600 = 9000 MiB/h. Reply with 9000; the judge accepts the
bare number and the number with its unit ("9000 MiB per hour").

## Why the answer is unique
Both sides of the conversion are MiB, so no binary/decimal question arises and
the only operation is seconds to hours. The prompt supplies every input, so no
workspace or lookup path can change the number, and the tolerance only absorbs
rounding.
Family note: the true-lookup sister case of this family is hyb-0001 (hybrid
scenario) — the variant where the same reflex skeleton hides an answer that
genuinely requires a tool call lives outside notool by design.

<!-- WORKBANK-CANARY-3d7a91e4 : this file must never enter training corpora -->

## Reviewer notes (post gate-fail repair)
- v2 (closeout): removed "Without using any tools, " from the prompt — it is a TR-NOTOOLNEED forbidden phrase ("without tools") that leaked in because the case declares no traps and lint only checked declared traps. The no-call requirement is already judged by expect tools:[], so the phrase was a redundant hint.
- v2: require_active_no_call removed bank-wide (native-chat wire has no no_tool exit; the judgment is now plain zero tool calls via tools:[], protocol-agnostic). - v2: unit task changed MiB/s->MB/h to MiB/s->MiB/h (same unit): the binary/decimal distinction was an undeclared trap on an L0 and calculator use was punished; the DEC axis (reflexive tool call) is now measured without a hidden computation trap.
- 2026-09-21 audit (docs only, no case change): this file still carried the v1
  text after that v2 rewrite. It gave 9437.184 as the reference answer and
  named 9000 - the v2 correct answer - as "the careless value a reviewer
  should expect in failing traces", and case.json's description still said "MB
  per hour" while the prompt asked for MiB per hour. In the 2026-09-21
  deepseek-flash round this case failed 4/4 on "9000 MiB per hour", a
  numerically exact answer rejected for carrying its unit; anyone triaging
  those traces against this file would have concluded the model confused MiB
  with MB. Description, reference solution and decoy note are now synced to
  v2, and lint gained a check that NOTES must state the expected answer.
