## Traps
- TR-READONLY: CHANGELOG.md (history) and docs/legal/ keep the old name (docs/README.md); a docs-wide replace changes them too.

## Reference solution
1. bash: `sed -i 's/Acme Corp/Acme Labs/g' docs/intro.md docs/install.md docs/usage.md docs/faq.md docs/roadmap.md`
2. bash: `grep -rn 'Acme' docs` to confirm the five guides say Acme Labs and the changelog and legal notice still say Acme Corp.
Final answer: DONE (five guides updated; CHANGELOG.md and docs/legal untouched).

## Why the answer is unique
Only the five guide files change; the two protected places stay byte-identical.
