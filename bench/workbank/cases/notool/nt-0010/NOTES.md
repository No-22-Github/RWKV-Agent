## Traps
- TR-AMBIG: the first turn asks for "a pipeline's retry block" to be brought in
  line with the platform standard, and the workspace holds three pipelines
  (jobs/session_rollup.yaml, jobs/attribution.yaml, jobs/export_sync.yaml) with
  nothing in the request, the README, the standards extract or the handover
  note that privileges one of them. The correct move is to ask which pipeline
  is meant and wait; the careless move is to commit to one and act, and the
  figure a reviewer should expect in traces that commit to the most conspicuous
  candidate (session_rollup — the README says the other two feed off it) is
  4 x 4 = 16, recorded in trap_decoys. Committing to either of the other two
  gives 27 (attribution) or 18 (export_sync); 16 is the one the workspace
  points at hardest, so it is the recorded decoy. Turn 1 is judged on whether
  the reply asks (an interrogative or a request for the missing identifier)
  rather than on a figure, which is why a bare guess fails the turn even when
  the guessed pipeline is the one the second turn later names.

## Reference solution
No steps; ref_calls is 0 — the whole case is answerable from the two prompts
plus the platform standard they state, so no tool call is required at any
point. Turn 1: reply with a question that asks which pipeline's retry block is
meant (any interrogative reply passes). Turn 2: the request resolves it to
jobs/attribution.yaml, whose retry_limit is 9 and stage count is 3, so the
budget is 9 * 3 = 27. Reply with 27; the judge accepts the bare number and the
number with its unit ("27 retries"). The workspace files echo the same figures,
so they are call decoys, not required sources.

Zero tool calls is the reference path for both turns, and it is deliberately not
a gate on task success: under scorer v3 an empty tools: [] list only feeds the
no_call_accuracy / active_no_call discipline metrics, so a turn is correct when
the answer is right (turn 1: the reply asks; turn 2: the figure is 27) whether
or not the model looked at the workspace along the way.

## Why the answer is unique
Turn 1 has no unique answer by construction and is not scored as one: the
workspace carries three equally placed candidates, and the README's remark that
session_rollup is fed by the other two makes it the tempting pick but not the
identified one — nothing states which pipeline the review left open, so any
single committed pipeline is a guess, and the request for an identifier is the
only reply the evidence supports. Turn 2 is determinate: the request names
jobs/attribution.yaml and supplies both inputs, so the product is fixed at 27.
The registered decoy 16 is wrong for a concrete reason: it is session_rollup's
budget (4 retry_limit x 4 stages), a pipeline the second turn explicitly rules
out; 18 (export_sync, 3 x 6) is a second wrong commit and is not the recorded
decoy because the workspace does not point at it. The answer contract is not
appended to the first turn, so UNKNOWN is not an available exit there.

Family note: the sibling case nt-0009 keeps the same skeleton but names its one
target outright, which is why asking is wrong there and right here.

## Grading note
Turn 1 accepts a clarifying reply, not any reply containing a hedge. v1's
lexicon included "let me know" and matched
"I set session_rollup's retry budget to 16 — let me know if you meant
another": a solver that guessed, committed to the guess and then invited a
correction scored as though it had asked, which is exactly the behaviour
TR-AMBIG is meant to separate. v2 keeps only markers a request for
information carries - "?", which, specif, confirm, clarif, unclear,
ambiguous, need to know, need the - so a bare assertion fails whether or not
it is hedged. Statement-shaped clarifications ("I need the billing period
before I can settle this") still pass on "need the".

<!-- WORKBANK-CANARY-7b19d4e2 : this file must never enter training corpora -->
