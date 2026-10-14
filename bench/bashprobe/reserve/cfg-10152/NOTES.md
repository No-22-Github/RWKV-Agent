## Traps
- TR-DECOY: the root values.yaml says 1.8.0. Every bash call starts at the workspace root, so a turn-2 `cat values.yaml` after turn 1's `cd deploy/staging` reads the root copy.

## Reference solution
Turn 1: bash `cd deploy/staging && ls` -> lists notes.txt among others.
Turn 2: read deploy/staging/values.yaml by its full path (read tool or bash) -> 1.9.0-rc2.
Final answer turn 2: Staging pins image_tag 1.9.0-rc2 (deploy/staging/values.yaml; the root chart default is 1.8.0).

## Why the answer is unique
The question is about the file inside deploy/staging.
