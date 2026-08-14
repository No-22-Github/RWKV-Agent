# Primitive Bench `agent_cases_feedback` curated 30-case snapshot

- Source: <https://github.com/RWKV-Vibe/rwkv-Primitive-Bench/tree/416b073d2c5442ae34bfbf8a3b84ed414b5b85ff/agent_cases_feedback>
- Commit: `416b073d2c5442ae34bfbf8a3b84ed414b5b85ff`
- Imported: 2026-08-14
- Files: 29 unmodified JSON cases plus one audited correction selected from the
  upstream 112-case `agent_cases_feedback` suite

The selection complements `agent_cases_orig30` with binding, aggregation,
policy, configuration-format, encoding, and transformation tasks while avoiding
close duplicates of the existing prompt-injection, config-precedence, and JSONL
aggregation cases.

Selected upstream files:

- Weak binding and regression floor: `004`, `005`, `006`, `007`, `010`
- Entity and temporal binding: `014`, `015`, `016`, `021`
- Aggregation and rule calculation: `034`, `035`, `036`, `040`, `045`, `048`,
  `050`
- Policy, abstention, and verification: `053`, `054`, `059`, `062`, `066`,
  `069`
- Engineering formats: `076`, `077`, `086`, `091`
- Encoding and transformation: `100`, `101`, `108`, `110`

RWKV-Vibe describes its repository as a modification of
[`marty1885/primitive-bench`](https://github.com/marty1885/primitive-bench) and
credits Marty / marty1885 for the original task design and harness ideas. The
selected JSON files preserve the upstream snapshot byte-for-byte except
`036_weighted_vote_winner.json`. Its original rows made Oak, Pine, and Maple tie
at 6 while accepting only Oak, so RWKV-Agent changes Oak's second weight from 4
to 5. The corresponding upstream fix is
[`RWKV-Vibe/rwkv-Primitive-Bench#1`](https://github.com/RWKV-Vibe/rwkv-Primitive-Bench/pull/1).
RWKV-Agent supplies its own loader, isolated tool implementations, Runner, and
scorer integration.

No license file was present in the source repository at the pinned commit. This
provenance notice records origin and does not replace an upstream license grant.
