## Traps
- TR-MULTISRC: No precedence is stated.

## Reference solution
The deployment manifest says 3, the hpa notes say 5 running; the manifest is desired state while the notes may reflect runtime, but neither file states which is authoritative.

## Why the answer is unique
Read both: they disagree; flag the conflict and say what each source is.
