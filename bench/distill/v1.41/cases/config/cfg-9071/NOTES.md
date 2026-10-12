## Traps
- TR-READONLY: deploy/_example stays as it is; ACCESS_LOG_LEVEL=debug is a look-alike key that the README says to keep.
- A global `s/debug/info/` would also change ACCESS_LOG_LEVEL and the template.

## Reference solution
1. bash: `find deploy -name app.env | grep -v /_example/ | xargs sed -i 's/^LOG_LEVEL=debug$/LOG_LEVEL=info/'`
2. bash: `grep -rn LOG_LEVEL deploy` to confirm five services changed and _example and every ACCESS_LOG_LEVEL did not.
Final answer: DONE (five services now LOG_LEVEL=info; _example and ACCESS_LOG_LEVEL untouched).

## Why the answer is unique
Only the exact LOG_LEVEL line of the five service files changes; everything else is byte-identical.
