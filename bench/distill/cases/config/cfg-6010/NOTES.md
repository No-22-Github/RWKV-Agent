## Traps
- TR-ABSENT: no block in the chain defines `stream_keepalive_s`. base carries `keepalive_probe_s` 30, which lands in tracking's resolved config through the chain, and a solver that reads the two keepalive keys as one setting reports 30 instead of UNKNOWN.

## Reference solution
1. Read README.md: a service keeps the inherited value for any key it does not set, so the whole resolved chain is the service's effective config.
2. Read config/services.json: walking tracking, booking and base, no block defines `stream_keepalive_s`; base's `keepalive_probe_s` is a probe on the request path, not the stream.
3. Read docs/ops-notes.md: position pushes to the control room go through the carrier's own channel. No stream keepalive value exists, so the answer is UNKNOWN.

## Why the answer is unique
The resolved chain is the whole effective config by the README's rule, and `stream_keepalive_s` is named in none of its three blocks, so there is no value the service could run with. The decoy 30 belongs to `keepalive_probe_s`, a different key that merely rides the same chain; reading one keepalive key as the other is the mistake the case is built around. The answer is UNKNOWN.
