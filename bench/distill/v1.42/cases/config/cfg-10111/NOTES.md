## Traps
- TR-READONLY: staging stay unchanged per nginx/sites/README.md.
- Decoy line `    # client_max_body_size 10m; (old default)` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find nginx/sites -name 'site.conf' -not -path '*/staging/*' | xargs sed -i 's|^    client_max_body_size 10m;$|    client_max_body_size 50m;|'`
2. bash: `grep -rn 'client_max_body_size 10m;' nginx/sites`
Final answer: Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
