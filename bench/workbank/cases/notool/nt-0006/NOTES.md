## Traps
- TR-NOTOOLNEED: the question is wrapped in a concrete service (the Meridian
  API gateway, a partner-integration guide, a quota) so it reads like a
  workspace lookup, but "which HTTP status code tells a client it sent too
  many requests" is fixed by the HTTP specification and needs no call at all.
  The costly behaviour is reaching for the workspace or abstaining with
  UNKNOWN; the careless wrong VALUE, when the model answers from a near-miss
  memory of overload handling, is 503 (Service Unavailable), recorded in
  trap_decoys. The gateway code map in the workspace is the call decoy: it
  lists the vendor's own private identifiers (GW-7104 for quota_exceeded), so
  a model that reads it still has no HTTP status code to copy.

## Reference solution
No steps; ref_calls is 0. Reply the bare number 429 (Too Many Requests, RFC
6585) directly from stable protocol knowledge. The correct pass criterion is
the answer alone: under scorer v3 the turn's `tools: []` no longer fails a
turn, it only feeds the no_call_accuracy / active_no_call call-discipline
metrics, so a correct figure reached after a reflexive call still passes.
UNKNOWN fails the expected_number check.

## Why the answer is unique
429 is the single status code the HTTP specification defines for a client
that has sent too many requests in a given amount of time; no fixture value
feeds the answer. The registered decoy 503 is wrong here for a specific
reason: RFC 9110 defines it as a server-side temporary unavailability, not as
a client quota violation, so a server that is merely over its request budget
has not failed. The gateway's own identifiers (GW-7104 and friends) are
vendor-private strings, not HTTP codes, so the decoy file cannot support any
HTTP-code answer; and the answer contract's UNKNOWN exit is wrong because the
fact does not depend on the workspace.

<!-- WORKBANK-CANARY-c3f08d6e : this file must never enter training corpora -->
