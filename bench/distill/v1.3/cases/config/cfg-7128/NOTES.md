## Traps
- TR-PRECEDENCE: dispatch_timeout_s is defined in the base (90) and in the
  north site file (60); the site file wins. Reading only the base reports 90,
  and reading the wrong site file reports 75.

## Reference solution
1. Read README.md: which site file belongs to the north dispatch center and the
   site-over-base order.
2. Read config/site-north.json: dispatch_timeout_s is 60.
3. Read config/base.json: the base carries 90, which the north file overrides.

## Why the answer is unique
The README maps the north center to site-north.json and states the site file
wins on same-name keys, so between 90 and 60 exactly one is effective for the
north. The south figure 75 belongs to a file the north never reads. No reading
makes 90 or 75 the north's effective value, leaving 60.
