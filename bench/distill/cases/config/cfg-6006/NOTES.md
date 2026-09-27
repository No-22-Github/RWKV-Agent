## Traps
- TR-ABSENT: the meter_reader block in config/poller.json carries no `firmware_channel`. The relay_controller block in the same file carries `firmware_channel` "stable", and a solver that takes the channel from the neighbouring block reports "stable" instead of UNKNOWN.

## Reference solution
1. Read README.md: each service reads only its own block, and a service never falls back to another block's settings.
2. Read config/poller.json: the meter_reader block holds poll, backoff and timeout keys and no channel; the only `firmware_channel` sits in the relay_controller block.
3. Read docs/firmware-notes.md: meter firmware is updated by the meter supplier on their own schedule, so no channel is configured in the poller. The answer is UNKNOWN.

## Why the answer is unique
The README states that a service never falls back to another block's settings, so the relay controller's channel cannot reach the meter reader, and the supplier note confirms no channel is set for the meters. The decoy "stable" is `relay_controller`'s `firmware_channel`, a different service's setting, so reading it across blocks is the mistake the case is built around. The answer is UNKNOWN.
