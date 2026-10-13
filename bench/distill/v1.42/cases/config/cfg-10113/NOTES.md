## Traps
- TR-READONLY: release-legacy stay unchanged per ci/pipelines/README.md.
- Decoy line `  # node: 18 pinned by legacy runner` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find ci/pipelines -name 'pipeline.yml' -not -path '*/release-legacy/*' | xargs sed -i 's|^  node: 18$|  node: 20|'`
2. bash: `find ci/pipelines -name 'pipeline.yml' -not -path '*/release-legacy/*' | xargs sed -i 's|^  cache_key: deps-v3$|  cache_key: deps-v4|'`
3. bash: `grep -rn 'node' ci/pipelines`
Final answer: Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
