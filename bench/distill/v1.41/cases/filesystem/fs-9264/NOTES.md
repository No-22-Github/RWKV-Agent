## Traps
- TR-READONLY: pipelines/vendor stays as it is. TR-DECOY: old-notes.yml.bak is a backup file, not a .yml pipeline.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `for f in $(find pipelines -name '*.yml' | grep -v /vendor/); do mv "$f" "${f%.yml}.yaml"; done`
2. bash: `find pipelines -type f`
Final answer: DONE (seven pipelines renamed to .yaml, vendor untouched).
Turn 2:
1. bash: `for f in pipelines/legacy/*.yaml; do mv "$f" "${f%.yaml}.yml"; done`
2. bash: `find pipelines -type f`
Final answer: DONE (legacy nightly and cleanup are .yml again).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Change .yml to .yaml across pipelines (vendor excluded), then restore .yml in the legacy folder.
2. Rename the pipelines to the .yaml extension, but the legacy ones must go back to .yml afterwards.
3. yml -> yaml everywhere except vendor; then legacy back to yml.
4. Move all pipeline files to .yaml, leave the vendor mirror; the two legacy pipelines return to .yml.
5. 把 pipelines 里的 .yml 统一改成 .yaml，之后 legacy 里的两个改回 .yml
