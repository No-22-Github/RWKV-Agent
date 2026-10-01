## Traps
- TR-NEARNAME: the twin service pay-sim-eu loses 6 leases inside the window; folding the names answers 24.
- TR-DECOY: two pay-sim lease losses sit just outside the window edges; including them answers 20. The in-window pay-sim count is 18.

## Reference solution
1. Read README.md: line grammar and the two services.
2. Search 'session lease lost' and read the line windows around the hits.
3. Keep ERROR lines whose service field is exactly pay-sim.
4. Compare timestamps with the window; the count is 18.

## Why the answer is unique
The service field separates pay-sim from pay-sim-eu and the README declares them separate; no event lands on the window edges, so the interval is exact. The count is 18.
