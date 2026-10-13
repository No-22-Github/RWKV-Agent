## Traps
- TR-READONLY: canary stay unchanged per services/README.md.
- Decoy line `new_ui_beta=false` shares text with the target line.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find services -name 'feature-flags.properties' -not -path '*/canary/*' | xargs sed -i 's|^new_ui=false$|new_ui=true|'`
2. bash: `grep -rn 'new_ui' services`
Final answer: Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
