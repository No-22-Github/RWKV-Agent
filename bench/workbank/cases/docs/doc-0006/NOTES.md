## Traps
- TR-DECOY: CHANGELOG.md opens with "## 5.0.0-rc.3 - preview - 2026-09-02", a
  preview build that carries both the highest version number and the latest
  date, so it is the most conspicuous entry in the file. A reader who takes the
  top entry, or the numerically highest version, answers "5.0.0-rc.3" (or drops
  the suffix and answers "5.0.0"). The changelog's own channel legend says
  preview builds stay in the sandbox estate and only shipped builds are run by
  customers, so the newest shipped release is 4.8.1.

## Reference solution
1. List the workspace to locate the project documents (1).
2. Read CHANGELOG.md and note that entries are tagged with a release channel (2).
3. Discard the preview entry and take the newest shipped entry, 4.8.1 (3).

## Why the answer is unique
The changelog records two shipped releases (4.8.0, 4.8.1) and one preview build.
The channel legend at the head of the file is a rule, not a hint: preview builds
are confined to the sandbox, so the newest build customers receive is 4.8.1.
"5.0.0-rc.3" cannot be the answer because the same file excludes it, and
README.md names no version at all. verify.py recomputes the newest shipped
version from case.json's fixture (filtering by the channel tag) and requires the
title line, so deleting that line stops the computation.

<!-- WORKBANK-CANARY-b6d29e05 : this file must never enter training corpora -->
