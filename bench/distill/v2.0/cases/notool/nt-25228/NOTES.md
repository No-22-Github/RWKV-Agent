## Traps
- TR-NOTOOLNEED: the call profile carries the call count and the holding time, so the traffic follows without opening anything. Stopping at the call minutes gives 312.

## Reference solution
No steps; ref_calls is 0. 96 calls of 3.25 minutes is 312 call minutes, which over the hour is 5.2 Erlangs.

## Why the answer is unique
The calls hold the group for 96 times 3.25, or 312 minutes, and an Erlang is a busy hour, so the traffic is 312 over sixty: 5.2 Erlangs. The decoy 312 is those holding minutes before the hour is taken into account, which is a count of minutes rather than traffic; the mast notes carry no figure that changes it.
