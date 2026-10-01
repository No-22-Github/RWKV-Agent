## Traps
- TR-NEARNAME: the canonical source also defines resolve_tenant_id (line 1178) and its name carries resolve_tenant as a prefix, so a prefix search or a first-hit answer lands on the wrong line. A definition is the exact `def resolve_tenant(` line: 1664.

## Reference solution
1. Read README.md: it names kelpgrid/policy.py as the canonical source.
2. Search the name resolve_tenant and read the line windows around the hits.
3. The hit inside resolve_tenant_id is a different function; a definition is a `def` line matching the exact name.
4. `def resolve_tenant(` is at line 1664.

## Why the answer is unique
The README pins the canonical source and the runbook counts definitions; resolve_tenant_id is a separate function whose name merely extends the target's, and only one `def resolve_tenant(` line exists. The answer is 1664.
