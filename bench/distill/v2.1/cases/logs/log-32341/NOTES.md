## Traps
No python; group by hour with cut|sort|uniq.

## Reference solution
grep ERROR | cut | uniq -c.

## Why the answer is unique
hour 14 with 60 errors.
Expected: 14; 60
