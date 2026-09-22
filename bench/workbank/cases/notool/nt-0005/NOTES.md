## Traps
- None. L0 base case of fam-nt-explain-02: a single deterministic unit
  conversion whose only input is stated in the prompt, so the correct run
  makes zero tool calls. Calls are reported as call discipline
  (no_call_accuracy / active_no_call) rather than as task success, so a
  correct figure reached after a reflexive calculator call still answers the
  question and is still recorded as having broken the zero-call contract.
- Careless values a reviewer should expect in failing traces: 75 (converting
  per hour to per minute, 1.25 * 60), or 0.0521 (per-minute rate, 1.25 / 24),
  or any figure that carries the rate into a different unit base.

## Reference solution
No steps; ref_calls is 0. The answer is a restatement in the same unit base:
an hour is 24 hours per day, so 1.25 TiB per hour over a day is
1.25 * 24 = 30 TiB per day. Reply with 30; the judge accepts the bare number
and the number with its unit ("30 TiB per day"). The workspace note
(jobs/archive_notes.txt) repeats the same 1.25 TiB per hour premise, so it is
a call decoy, not a required source.

## Why the answer is unique
Both the given and the requested unit are TiB, so no binary/decimal question
arises and the only operation is hours to days, whose length is fixed at 24.
The prompt supplies every input, and the workspace note records the same
rate, so no second reading can produce another figure; the tolerance only
absorbs rounding. The answer contract's UNKNOWN exit is a wrong exit here
because nothing about the conversion is unknown.

<!-- WORKBANK-CANARY-4b7e2a91 : this file must never enter training corpora -->
