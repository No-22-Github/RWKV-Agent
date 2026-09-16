## Traps
- TR-NOTOOLNEED: the prompt wraps the question in a concrete-sounding service
  (the Meridian ingest gateway, a security reviewer, an onboarding), so it
  reads like a workspace or documentation lookup, but the default HTTPS port
  is stable world knowledge and the workspace is empty. The costly wrong
  behaviour is calling search/read-style tools or abstaining with UNKNOWN;
  the careless wrong VALUE, when the model answers from near-miss knowledge,
  is 80 (the HTTP default port), recorded in trap_decoys.

## Reference solution
No steps; ref_calls is 0. Reply the bare string 443 directly from stable
knowledge with zero tool calls. Any call against the twelve-tool directory
fails the tools:[] / require_active_no_call contract, and UNKNOWN fails the
output_equals check.

## Why the answer is unique
443 is the single IANA default port for HTTPS; no fixture value feeds the
answer (files is empty by design), so no second reading of the workspace can
produce another value. The answer contract's UNKNOWN exit is a decoy path
here: the fact does not depend on the workspace, so abstaining is wrong.
Family note: the true-lookup sister case of this family is hyb-0001 (hybrid
scenario) — the variant where an identically framed question can only be
answered by actually querying lives outside notool by design.

<!-- WORKBANK-CANARY-b58c20f7 : this file must never enter training corpora -->
