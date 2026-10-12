## Traps
- TR-READONLY: site/vendor/*.htm keep their names (site/README.txt); archive.htm.bak merely contains .htm in its name.

## Reference solution
1. bash: `for f in $(find site -name '*.htm' | grep -v /vendor/); do mv "$f" "${f}l"; done`
2. bash: `find site -name '*.htm*'` to confirm six pages are .html and the vendor files and the .bak keep their names.
Final answer: DONE, six pages renamed to .html; vendor files untouched.

## Why the answer is unique
Rename is by extension only, outside site/vendor; contents do not change.
