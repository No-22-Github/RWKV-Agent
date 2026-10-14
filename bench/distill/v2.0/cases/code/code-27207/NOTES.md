## Traps
- TR-CLAIM: a STALE NOTE comment at line 703 claims drain_queue moved to queuectl2.py in the spring cleanup; queuectl2.py defines nothing of the sort and the README resolves definitions against the canonical source, so the claim is false. The definition sits in the canonical file at line 1677.

## Reference solution
1. Read README.md: it names pineburst/queuectl.py as the canonical source and says definitions resolve against it, not against comments.
2. Search the name drain_queue and read the line windows around the hits.
3. Check the STALE NOTE's claim against queuectl2.py; no definition lives there.
4. `def drain_queue(` in the canonical source is at line 1677.

## Why the answer is unique
The README pins the canonical source and explicitly overrides comment claims; queuectl2.py contains no such definition, so the stale note cannot be a reading. Exactly one `def drain_queue(` line exists: 1677.
