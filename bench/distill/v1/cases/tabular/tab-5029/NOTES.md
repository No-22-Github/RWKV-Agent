## Traps
- TR-RULEFILE: the levy rate and the charity exemption live in auction_terms.md, not in the request. Levying
  every landing at 2.4 per cent gives 1789.82, and the sale_type column in the landing file is the only place the
  exempt landings are marked.

## Reference solution
1. List the workspace: the August landing records, the auction terms and a short readme.
2. Read auction_terms.md: the levy is 2.4 per cent of a landing's sale value, and charity sales carry no levy.
3. Read landings_2026-08.csv, keep the landings whose sale_type is open and add their value.
4. 2.4 per cent of that total is 1666.94 pounds.

## Why the answer is unique
The levy is a share of sale value, so it can only be worked out from the terms that set the rate, and the terms
name the charity sales as exempt. Every landing carries a sale_type, so each row either carries the levy or is
exempt, and the exempt landings make up the difference between the two readings. Charging the rate across all
landings would levy sales the terms exclude, so the levy owed is 1666.94 pounds.
