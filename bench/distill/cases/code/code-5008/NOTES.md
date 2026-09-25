## Traps
- TR-DECOY: `interfaces/ledger.py` gives its own class an `emit` method too, and `consumers/relay.py` calls it as `ledger.emit(event)`. Counting every `.emit(` call site in the workspace gives 4 instead of 3.

## Reference solution
1. Read interfaces/sink.py: Sink declares emit, and the annotated variables in the consumers are the way to tell a sink from a ledger (call 1).
2. Read consumers/pump.py: `self.sink` and the `sink: Sink` parameter carry two emit calls (call 2).
3. Read consumers/relay.py: `ledger.emit(event)` goes to the Ledger class, while `sink.emit(events)` is the interface call, so one call site (call 3).
4. Read interfaces/ledger.py to confirm its emit belongs to a different class (call 4). The interface's emit has three call sites: two in pump.py, one in relay.py.

## Why the answer is unique
The decoy 4 counts the ledger call in consumers/relay.py together with the interface calls. The Ledger class is not a Sink and its emit signature takes a posted entry, while the parameters that are annotated `Sink` in the two consumers are what the interface calls run through. Three calls bind to Sink.emit and one does not, so the count is 3.
