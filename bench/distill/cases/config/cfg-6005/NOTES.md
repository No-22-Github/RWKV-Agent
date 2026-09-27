## Traps
- TR-DECOY: config/poller.json gives `poll_seconds` for three services: meter_reader 30, relay_controller 15, alarm_hub 60. A solver that takes the first poll interval in the file, or the one belonging to the most prominent service, reports 30 instead of the relay controller's 15.

## Reference solution
1. Read README.md: each service reads only the block named for it, with no sharing between blocks.
2. Read config/poller.json: the relay_controller block carries `poll_seconds` 15; the 30 and 60 in the other blocks belong to other services. The answer is 15.

## Why the answer is unique
The README states that a service never falls back to another block's settings, so the only interval that counts for the relay controller is the one inside its own block. The decoy 30 is `meter_reader`'s interval, and 60 is `alarm_hub`'s; both describe other services, so reading them as the relay controller's cadence is the mistake the case is built around. The answer is 15.
