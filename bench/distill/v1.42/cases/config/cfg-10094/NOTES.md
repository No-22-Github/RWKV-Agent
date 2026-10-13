## Traps
- TR-READONLY: legacy-* crates are frozen by crates/README.md (edition and serde stay).
- Turn 2 repeats the same scope; legacy crates still must not change.
- 5 files change; 3 stay byte-identical.

## Reference solution
1. bash: `find crates -name Cargo.toml -not -path '*/legacy-*' | xargs sed -i 's/^edition = "2018"$/edition = "2021"/'`
2. bash: `find crates -name Cargo.toml -not -path '*/legacy-*' | xargs sed -i 's/^serde = "1"$/serde = "1.0.210"/'`
3. bash: `grep -rn -e edition -e serde crates`
Final answer: Pinned serde to 1.0.210 in the five non-legacy crates (edition already 2021 from the first turn); legacy-ffi and legacy-shim untouched. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
