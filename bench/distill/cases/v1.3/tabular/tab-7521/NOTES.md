## Traps
- TR-SIGN: return credits are stored as positive amounts. Reading them as extra intake and adding them to the charge total gives 5003.75; the README states the net intake takes the credits back out.

## Reference solution
1. read_file README.md: credits are positive amounts to take back out of the charge total.
2. data_query: {"path":"data/rental_charges.csv","filter":{"charge_month":"2026-03"},"operation":"sum","field":"amount"} -> 4399.93.
3. data_query: {"path":"data/return_credits.csv","filter":{"credit_month":"2026-03"},"operation":"sum","field":"amount"} -> 603.82.
4. Subtract: 4399.93 - 603.82 = 3796.11; reply with the number 3796.11 only.

## Why the answer is unique
The decoy 5003.75 treats positive-stored credits as income, but the README defines credits as returned-book amounts to take back out, so adding them contradicts the file's own semantics. February and April rows fail the month filters. The answer is 3796.11.
