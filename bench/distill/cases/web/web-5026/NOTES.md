## Traps
No traps. One search returns Coldbridge's own decline code page and the CB-1077 row
answers the question.

## Reference solution
1. Search for the Coldbridge decline codes; the only result is
   support.coldbridge.example/errors/declines.
2. Open that page: CB-1077 is raised when a card sees more than 19 attempts in a
   rolling hour, and the worked example says nineteen attempts are accepted while
   the twentieth ends on the code.

## Why the answer is unique
The page attaches one condition and one worked example to the code the shop keeps
hitting, so the number of attempts that pass in the window is fixed at 19. CB-1004
means the issuer wants a challenge and CB-1120 means the account has no volume
left, so neither describes the attempts; the 30 seconds on the CB-1077 row is how
long to leave the card before retrying, not how many attempts are allowed.

## Five alternative phrasings of the task
1. coldbridge decline codes
2. coldbridge CB-1077 meaning
3. how many attempts before coldbridge raises CB-1077
4. coldbridge rolling hour attempt limit
5. coldbridge payment decline reference
