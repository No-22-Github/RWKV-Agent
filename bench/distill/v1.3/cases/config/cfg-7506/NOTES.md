## Traps
- TR-DECOY: config/service.yaml 里 audit_sink 只出现在注释行 # audit_sink: s3://wrenfield-audit，粗读会认为已配置。 A careless pass reports `s3://wrenfield-audit`.

## Reference solution
1. Read runbooks/launch.md for the required set.
2. Read config/service.yaml and check each required key, treating the commented audit_sink line as absent.
3. Report the missing key and the values that are already set.

## Why the answer is unique
The checklist states a commented key does not count, so audit_sink is missing even though its s3:// value sits in a comment; trace_endpoint, sentry_dsn and the bulk_export flag are present, with the collector URL as the trace value. No other required item exists, so the gap is exactly audit_sink.
