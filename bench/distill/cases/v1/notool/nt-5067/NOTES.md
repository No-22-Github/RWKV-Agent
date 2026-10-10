## Traps
- TR-NOTOOLNEED: the key table, README and job note are props; the merge line is a feature of the file format itself. The near-miss decoy `<<: *defaults` has the merge key but the wrong anchor name, so it references a mapping the build file never defines and the file fails to load.

## Reference solution
1. Answer from the format: the merge key is `<<`, and it takes an alias to the anchored mapping, which is written `*` followed by the anchor name.
2. Reply with `<<: *sensor-defaults`.

## Why the answer is unique
The question asks for a merge, and the format has exactly one key that merges an aliased mapping into the mapping being written, `<<`; reusing the shared block without it copies nothing because an alias alone is not a mapping key. The anchor name is part of the question, so `<<: *defaults` points at a mapping that does not exist. Writing the key in quotes is the same line protected against a parser that reserves the bare `<<` token.
