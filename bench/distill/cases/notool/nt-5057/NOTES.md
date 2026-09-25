## Traps
- TR-NOTOOLNEED: deploy/port-swap.tsv and README.md sit in the workspace, but the rewrite is a fixed shell idiom and nothing on disk is needed to produce it. The near-miss decoy drops the backup suffix: `sed -i 's/7411/8117/g' shore-gateway.conf` edits in place but leaves no copy of the original, which the question asks for.

## Reference solution
1. Answer from the shell: an in-place rewrite is `sed -i` plus a substitution, and the backup suffix is attached to the `-i` flag.
2. Reply with `sed -i.bak 's/7411/8117/g' shore-gateway.conf`.

## Why the answer is unique
The question names the file, both ports and the required backup, so the command is fully determined: `-i.bak` is the spelling every GNU sed documents for "edit in place and save the previous content as <file>.bak", and the substitution must carry both ports with the global flag because the question says every occurrence. `sed -i 's/7411/8117/g' shore-gateway.conf` cannot be a reading of the question because it never produces the .bak copy, and no other tool's flag set changes the requested behaviour. The recorded deployments file holds the same rewrite for reference only.
