## Traps
- TR-DECOY: config/app.yaml 里的 artifact_store=/tmp/relay-artifacts 会被 overlay 覆盖，粗读会把基座值当成生效值。 A careless pass reports `/tmp/relay-artifacts`.

## Reference solution
1. List config/ and read the README for the layering rule.
2. Read config/app.yaml for the base values.
3. Read config/prod.overlay.yaml, apply it over the base, and report each effective value with its source.

## Why the answer is unique
The README fixes the rule that the overlay wins per key, so log_level and artifact_store take the overlay's warn and the s3:// bucket, while metrics appears only in the base and keeps ws://metrics.bramblewick.internal/stream. The /tmp path survives only in the base layer and is therefore not in effect.
