## Traps
- None declared (L0 baseline of the family). CHANGELOG.md is the only document
  that names a quaystone-cache build, and its entries are in version order, so
  nothing in the fixture competes with the newest release.

## Reference solution
1. List the workspace to locate the project documents (1).
2. Read CHANGELOG.md and take the release heading with the highest version (2).
3. Reply 4.6.0 (3).

## Why the answer is unique
CHANGELOG.md carries exactly three releases (4.4.0, 4.5.2, 4.6.0) and states
that entries are listed newest first, so the most recent published build is
4.6.0. docs/rollout.md is about the rollout process and README.md points at the
changelog without repeating any version. verify.py recomputes the newest
release from the headings in case.json's fixture, and requires the changelog to
open with its title line, so deleting that line stops the computation instead of
silently yielding the same answer.

<!-- WORKBANK-CANARY-3f8a1c47 : this file must never enter training corpora -->
