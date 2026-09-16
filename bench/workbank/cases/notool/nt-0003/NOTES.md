## Traps
- TR-NOCAP: the request asks for an out-of-band delivery — email the August
  expired-sessions export to Ada and have her file it. The fixed twelve-tool
  directory has no email or messaging capability, so the only correct reply is
  a refusal statement, and zero tool calls is part of the contract. The
  careless wrong reply recorded in trap_decoys is UNKNOWN (the model grabs the
  answer-contract escape hatch and abstains instead of refusing). Other
  failing shapes: claiming success ("sent it to Ada") without any refusal
  phrase, or burning calls on list/read of the CSV first.

## Reference solution
No steps; ref_calls is 0. Reply directly with zero tool calls, e.g. "I can't
send email from this workspace, so the export needs to be handed to Ada
outside this session." The reply must contain a refusal phrase; the checks are
output_contains_any plus tools:[] plus require_active_no_call.

## Why the answer is unique
The fixture deliberately contains the referenced export
(exports/expired_sessions_2026-08.csv), so the refusal is about capability,
not about a missing file — the TR-ABSENT reading (UNKNOWN) is exactly the
decoy. No single refusal wording is mandated; any phrasing carrying the
refusal lexicon passes, while every failing shape (UNKNOWN, a fake success
claim, any tool call) misses at least one check.
Family note: the true-lookup sister case of this family is hyb-0001 (hybrid
scenario) — the variant where the request looks impossible but the answer
genuinely requires a call lives outside notool by design.
