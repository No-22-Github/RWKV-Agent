## Traps
No traps. One search returns a single troubleshooting page and its table answers the question.

## Reference solution
1. Search for the Thistlebay gateway error codes; the only result is support.thistlebay.example/troubleshooting/gateway-errors.
2. Open that page: the TB-4021 row prescribes waiting 45 seconds before a retry.

## Why the answer is unique
The table has one row per code and the question names TB-4021, so only that row applies. 5 seconds belongs to TB-4001, 120 seconds to TB-5030, and TB-5112 asks the client not to retry at all; none of them is the wait prescribed for TB-4021. The handshake itself has to finish within 2 seconds, which is a separate statement about the gateway, not about the client's retry wait.

## Five alternative phrasings of the task
Every query below carries the fixture keyword thistlebay, so each one is answered by the fixture entry.
1. thistlebay TB-4021 retry wait
2. thistlebay gateway error codes
3. thistlebay upstream handshake timeout client action
4. thistlebay troubleshooting wait before retry
5. thistlebay edge error reference
