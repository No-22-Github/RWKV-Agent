## Traps
- TR-NEARNAME: HANDBOOK.md links "[Deployment runbook](deploy-runbooks.md)",
  but the repository holds deploy-runbook.md - the two names differ by the
  trailing "s". A reader who matches the link by sight, or who finds
  deploy-runbook.md on disk and stops, reports "deploy-runbook.md" (the file
  that exists) instead of the name the link actually carries. Every other
  target in the handbook (oncall-rota.md, release-notes.md, rollout-notes.md)
  resolves, so only one answer stands.

## Reference solution
1. List the workspace to see the files the project actually holds (1).
2. Read HANDBOOK.md and collect its four link targets (2).
3. Compare each target with the file list; only deploy-runbooks.md is absent (3).
4. Reply deploy-runbooks.md (4).

## Why the answer is unique
The handbook is the only document with links, and it lists four targets. Three
match a file in the repository exactly; deploy-runbooks.md matches nothing,
while its one-character-short sibling deploy-runbook.md does exist and is not
linked anywhere. There is no other near-name in the repository, so the failing
link can only be the one that names deploy-runbooks.md. verify.py recomputes the
unresolved set from case.json's fixture and rejects a fixture with zero or more
than one unresolved target, and it requires the handbook title line.

<!-- WORKBANK-CANARY-71c4a9d2 : this file must never enter training corpora -->
