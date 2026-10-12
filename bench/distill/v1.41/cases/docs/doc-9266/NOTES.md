## Traps
- TR-READONLY: wiki/archive is frozen and README.md is not a page, so neither gets the line; the exact text of the line is in wiki/README.md.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find wiki -name '*.md' | grep -v '/archive/\|README' | xargs sed -i '1i <!-- owner: docs-team -->'`
2. bash: `head -n 1 -q wiki/*.md wiki/*/*.md`
Final answer: DONE (seven live pages start with the owner comment).
Turn 2:
1. bash: `sed -i '1{/^<!-- owner: docs-team -->$/d}' wiki/legal/terms.md wiki/legal/privacy.md`
2. bash: `head -n 1 -q wiki/*.md wiki/*/*.md`
Final answer: DONE (legal terms and privacy are back to their original text, the other five keep the line).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Stamp each wiki page (not the archive, not the README) with the owner comment on line one, then strip it from the legal pages.
2. Put the docs-team owner comment at the top of the live wiki pages, and afterwards take it off terms.md and privacy.md.
3. Prepend the owner line to all wiki pages except archive; legal pages must not have it.
4. First line owner comment on every live page; remove from wiki/legal/*.
5. 给 wiki 里的在用页面第一行加上 owner 注释，再把 legal 下两页的去掉
