## Traps
- TR-EARLYHIT: the first result, docs.peldreth.example/channels/error-codes, already states the backoff for PD-2004, so one search is enough; docs.peldreth.example/relay/error-codes is a second page for the relay service whose 60-second backoff belongs to PR-3117 and is the decoy.

## Reference solution
1. Search once for the Peldreth channel error codes: the first result is the channel page, whose snippet gives the 20-second backoff for PD-2004, and the relay page is listed with it.
2. Open docs.peldreth.example/channels/error-codes and confirm the PD-2004 row: back off for 20 seconds, then subscribe again; answer 20.

## Why the answer is unique
The two pages are separate error namespaces, and the code in the question, PD-2004, appears only in the channel table, which prescribes 20 seconds. The relay table's 60 seconds belongs to PR-3117, a different service and a different code, so it cannot be the backoff for PD-2004. PD-1010 and PD-3404 prescribe no backoff at all.

## Five alternative phrasings of the task
Every query below carries the fixture keyword peldreth, so each one is answered by a fixture entry.
1. peldreth channel error codes
2. peldreth PD-2004 backoff seconds
3. peldreth channel buffer overflow client action
4. peldreth subscribe again after error
5. peldreth channel service error reference
