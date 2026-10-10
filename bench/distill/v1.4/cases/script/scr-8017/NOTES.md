## Traps
- CRLF leaves '\r' on the status, so status == 'OK' never matches.

## Reference solution
Read script, switch to splitlines() (or strip), read back.

## Why the answer is unique
Lines are split correctly regardless of CRLF.
The fixed script prints:
east 2
north 3
south 2
