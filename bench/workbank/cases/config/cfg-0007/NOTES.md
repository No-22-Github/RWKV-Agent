## Traps
- TR-NEARNAME: the request names settings.yml, but no such file is on disk —
  the live runtime settings file is settings.yaml at the workspace root.
  docs/ingest-migration.md still cites the old settings.yml path and quotes
  the value it carried, 90 seconds. A model that answers from the migration
  prose without opening the live settings file reports the decoy 90; the
  file on disk sets shutdown_grace_seconds to 240.

## Reference solution
1. list_files — the root holds settings.yaml, plus README.md, docs/ and
   schemas/
2. read_file docs/ingest-migration.md — the note cites settings.yml with the
   old 90-second value, which is not a file on disk
3. read_file settings.yaml — shutdown_grace_seconds: 240
4. answer 240

## Why the answer is unique
settings.yaml is the only settings file in the tree and the only source that
defines shutdown_grace_seconds; the migration note is prose describing a path
that is not present, and the event contract and README carry no timing value.
Nothing else constrains the answer, so the effective shutdown grace period is
240 seconds.

<!-- WORKBANK-CANARY-7c2d9e51 : this file must never enter training corpora -->
