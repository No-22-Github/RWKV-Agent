## Traps
- TR-AMBIG: the first turn asks to settle "the quarterly reconciliation" for the Meadowford account, and usage/consumption.csv holds three billing periods (2025-Q4, 2026-Q1, 2026-Q2) with nothing in the request that identifies which one. README.md says reconciliations are usually opened against the most recent period, which makes 2026-Q2 the conspicuous pick: committing to it gives 52940 x 1.42 = 75174.80, recorded in trap_decoys. Committing to 2025-Q4 instead gives 68515.00; 75174.80 is the one the workspace points at hardest. Turn 1 is judged on whether the reply asks — no dedicated "should ask" expectation type exists, so the proxy is output_contains_any over interrogative and request-for-identifier phrasing (a question mark, "which", "period"/"quarter", "specify", "confirm", "let me know", "unclear"), the same proxy the frozen nt-0010 and the other multi-turn cases use. A bare guess fails turn 1 even when the guessed period is the one the second turn later names.

## Reference solution
1. list_files the Meadowford workspace; usage/consumption.csv holds three billing periods (1)
2. read_file usage/consumption.csv; no period is identified by the request, so the turn-1 reply asks which period to settle (2)
3. web_search for Tarnbrook Water's wholesale charges (3)
4. web_fetch the schedule; the Meadowford rate is GBP 1.42 per cubic metre (4); the second turn names 2026-Q1, whose volume is 41370 m3, so 41370 x 1.42 = 58745.40; answer 58745.40

## Why the answer is unique
Turn 1 has no unique answer by construction and is not scored as one: the account carries three equally placed billing periods and nothing in the workspace picks one: the request names none, the zone notices name none, and README.md says a reconciliation is opened against the period the desk names when it asks. So the request for the period that is meant is the only reply the evidence supports. (v1's README said reconciliations are "usually opened against the most recent billing period on file", which licensed the very guess turn 1 is meant to separate out - a solver could answer 2026-Q2 and cite the workspace for it. The sentence is gone in v2, and the decoy survives without it: 2026-Q2 is still the most recent row in the ledger.) Turn 2 is determinate: it names 2026-Q1, and the ledger holds exactly one row for that period (41370 m3) while the schedule holds exactly one Meadowford rate (GBP 1.42), so the product is fixed at 58745.40. The registered decoy 75174.80 is wrong for a concrete reason: it is the 2026-Q2 charge (52940 m3), a period the second turn explicitly rules out — it is the answer to "what would the most recent quarter come to", which is not the question the second turn asks. The 2025-Q4 figure 68515.00 is a second wrong commit and is not the recorded decoy because the workspace does not point at it. The answer contract is appended only to the second turn, so UNKNOWN is not an available exit on turn 1.

## Five alternative phrasings of the task
1. tarnbrook water wholesale charges schedule
2. tarnbrook water meadowford zone rate
3. tarnbrook water wholesale rate per cubic metre
4. tarnbrook water published wholesale tariffs
5. tarnbrook water business charges

## Grading note
Turn 1 accepts a clarifying reply, not any reply that happens to name a
period. v1's lexicon carried the bare nouns "period" and "quarter", so
"For the 2026-Q2 period, the amount is 75,174.80." - a solver that picked a
period itself and answered - scored as though it had asked. v2 uses the same
lexicon as nt-0010: "?", which, specif, confirm, clarif, unclear, ambiguous,
need to know, need the. The README's "usually opened against the most recent
billing period" is what makes the unasked guess defensible, which is why
turn 1 has to judge the asking and not the wording.

<!-- WORKBANK-CANARY-6ad08f23 : this file must never enter training corpora -->
