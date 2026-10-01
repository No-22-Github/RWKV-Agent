## Traps
- TR-DECOY: the journal already carries a checkout-api 504 ERROR from the morning (rq-be2a104c), and after the switch a ledger-sync 502 and a checkout-api WARN quoting 504 sit near the target. The morning 504 is pre-switch, the 502 names another service and the 504 WARN is not an ERROR, so the first post-switch checkout-api 504 ERROR is rq-8d7aa0d2.

## Reference solution
1. Read README.md: line grammar, service field, and that a line belongs to the service named in it.
2. Open the head of the journal and search for the traffic-switch banner; it is unique.
3. Walk the ERROR lines after the banner with short line windows; skip the ledger-sync 502 and the 504 WARN.
4. The first checkout-api 504 ERROR after the switch carries req=rq-8d7aa0d2.

## Why the answer is unique
The switch banner is a single line, so "after the switch" is unambiguous; a 504 WARN is a WARN and not an ERROR, the ledger-sync 502 names a different service, and the morning 504 sits prior to the banner. Exactly one request ID answers the question: rq-8d7aa0d2.
