# Primitive Bench `agent_cases_orig30` snapshot

- Source: <https://github.com/RWKV-Vibe/rwkv-Primitive-Bench/tree/0350023f99a31133fb30eb32dacf779f196827d4/agent_cases_orig30>
- Commit: `0350023f99a31133fb30eb32dacf779f196827d4`
- Imported: 2026-08-12
- Updated: 2026-09-07, synced from `416b073d2c5442ae34bfbf8a3b84ed414b5b85ff`
  (upstream rewrote 14 case prompts and raised 024's `max_turns` from 12 to 16);
  the prior snapshot is archived byte-for-byte at
  `archive/primitive-orig30-snapshot-416b073d/`, and scores recorded against
  that prior snapshot are not comparable with this one
- Files: the 30 JSON cases named `001_arithmetic.json` through
  `030_markdown_release_notes.json`

RWKV-Vibe describes its repository as a modification of
[`marty1885/primitive-bench`](https://github.com/marty1885/primitive-bench) and
credits Marty / marty1885 for the original task design and harness ideas. This
snapshot preserves the upstream JSON byte-for-byte; RWKV-Agent supplies its own
loader, isolated tool implementations, Runner, and scorer integration.

No license file was present in the source repository at the pinned commit. This
provenance notice records origin and does not replace an upstream license grant.
