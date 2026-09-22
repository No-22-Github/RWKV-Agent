## Traps
- TR-SIGN: credits_2026-05.csv stores each credit as a positive figure. The
  README states that a credit reduces the amount billed for the account it is
  issued against, so the month's total is charges (48767.30) less credits
  (3426.25) = 45341.05. A model that reads the positive credits as money
  flowing toward the company and adds them to the charges gets 48767.30 +
  3426.25 = 52193.55 (registered decoy) instead of 45341.05.

## Reference solution
1. read_file README.md - a credit is stored as a positive figure and reduces
   the amount billed (1)
2. read_file subscriptions_2026-05.csv - eight charges summing to 48767.30 (2)
3. read_file credits_2026-05.csv - three credits summing to 3426.25 (3)
4. calculator - 48767.30 - 3426.25 = 45341.05 (4)

The answer is 45341.05.

## Why the answer is unique
The two files are the only sources of amounts, every credit names an account
that also appears in the charge file, and no account is charged or credited
twice. The README fixes the direction of a credit, so there is exactly one
arithmetic reading: 48767.30 less 3426.25. The decoy 52193.55 is only reached
by ignoring the stated direction and adding the credits to the charges.
