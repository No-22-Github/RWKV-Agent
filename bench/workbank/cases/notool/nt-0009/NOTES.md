## Traps
- None. L0 base case of fam-nt-boundary-03: the request names one carrier
  profile outright and hands over every input it needs (retry_limit: 8,
  3 upstreams, plus the standard's rule), so the correct run is a single
  multiplication with nothing left to ask. Calls are still recorded as call
  discipline (no_call_accuracy / active_no_call) rather than as task success,
  so a correct figure reached after a reflexive look at the workspace still
  answers the question and is still recorded as having broken the zero-call
  contract.
- Careless values a reviewer should expect in failing traces: the retry_limit
  itself (8) reported as the budget, or the upstream count (3), or one of the
  other profiles' budgets from notes/freeze_inputs.txt (warehouse 12, returns
  35). The deliberate wrong behaviour for this control is not a wrong number
  but a stall: replying with a question about which carrier profile to use,
  which is the correct move for the sibling case nt-0010 and the wrong move
  here, because this request names profiles/dispatch.yaml.

## Reference solution
No steps; ref_calls is 0. Apply the rule the request states to the figures it
states: the dispatch profile's retry budget is its retry_limit (8) multiplied
by its upstream count (3), so 8 * 3 = 24. Reply with 24; the judge accepts the
bare number and the number with its unit ("24 retries"). The workspace extract
(notes/freeze_inputs.txt) and profiles/dispatch.yaml echo the same two figures,
so they are call decoys, not required sources.

## Why the answer is unique
The standard's rule and both of its inputs are stated in the request, and the
request points at exactly one profile, so the product is fixed at 24 whichever
way the model reads the workspace. The registered decoy path is a stall rather
than a number: a reply that asks which profile to use does not contain the
figure and does not satisfy the request, because no competing referent exists —
only profiles/dispatch.yaml is named. The two other profiles' figures
(warehouse 6 x 2, returns 5 x 7) belong to files the request never mentions, so
they cannot be defended as the intended target. The answer contract's UNKNOWN
exit is a wrong exit here: nothing about the arithmetic is unknown.

Family note: the sibling case nt-0010 keeps the same skeleton but withholds the
identity of the target, which is where asking becomes the correct move; this
case is the control that separates "needs a question" from "only looks like it
might".

<!-- WORKBANK-CANARY-2f6c81ad : this file must never enter training corpora -->
