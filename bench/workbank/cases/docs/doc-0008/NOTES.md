## Traps
- TR-DECOY: INDEX.md opens with "[Operations runbook](runbook.md)", whose target
  is not beside the index page; docs/ops/runbook.md does exist one level down.
  A reader who checks only the index's own directory calls runbook.md broken and
  reports "runbook.md" (or "deploy-guide.md", the same situation for the second
  entry), while the genuinely unresolved entry is rollback-checklist.md.
- TR-MULTISRC: deciding the answer needs two sources - INDEX.md (which names the
  entries) and the repository contents (which names exist). Using only the index
  page yields the conspicuous runbook.md/deploy-guide.md pair; using only the
  file listing cannot tell which names are claimed. trap_decoys records
  runbook.md for TR-DECOY and deploy-guide.md for TR-MULTISRC; both are wrong
  for the same reason, and NOTES names both here because a trap has one decoy
  slot.

## Reference solution
1. List the workspace recursively to collect every file the repository holds (1).
2. Read INDEX.md and collect its four entries (2).
3. Read README.md for the portal's resolution rule (a name that matches no file
   anywhere is unresolved) (3).
4. Match each entry against the file list: runbook.md and deploy-guide.md
   resolve under docs/ops/, oncall-rota.md at the root (4).
5. Reply rollback-checklist.md (5).

## Why the answer is unique
The portal rule in README.md is explicit: an entry is unresolved when its file
name matches no file in the repository. runbook.md and deploy-guide.md match
docs/ops/runbook.md and docs/ops/deploy-guide.md, and oncall-rota.md matches the
root file, so those three resolve. rollback-checklist.md matches nothing, and no
file with a comparable name exists anywhere in the repository, so exactly one
entry is unresolved. verify.py recomputes the unresolved set from case.json's
fixture by basename, rejects a fixture with zero or more than one unresolved
entry, and requires the index title line.

<!-- WORKBANK-CANARY-e2f07b3c : this file must never enter training corpora -->
