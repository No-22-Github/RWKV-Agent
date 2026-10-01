## Traps
- TR-DECOY: config/relay.properties 的注释行和 .old 备份里都留着 mq.nanpu.legacy:9092，粗读会当成现用 broker。 A careless pass reports `tcp://mq.nanpu.legacy:9092`.

## Reference solution
1. Read config/relay.properties, skipping the commented line.
2. Read config/relay.properties.old only to confirm it is the retired copy.
3. Report the broker, the TLS requirement and the inflight limit.

## Why the answer is unique
The legacy host appears only behind a comment and in the .old backup, whose relay id (relay-cn-2) also differs from the live relay-cn-3, so both legacy sources are retired. The live file states tcp://mq.nanpu.internal:9092 with tls.required=true and max.inflight=256, so the answer is unique.
