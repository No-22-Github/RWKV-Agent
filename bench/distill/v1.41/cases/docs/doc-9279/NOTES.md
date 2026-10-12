## Traps
- TR-READONLY: docs/drafts and README.md never get the footer. Every append goes on its own last line and every removal restores the original bytes (files end with one newline).
- Turn 3 undoes both earlier turns: all files are byte-identical to the fixture.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere; turn 3 undoes the whole change.

## Reference solution
Turn 1:
1. bash: `find docs -name '*.md' | grep -v '/drafts/\|README' | xargs sed -i '$a -- reviewed 2026'`
2. bash: `tail -n 1 -q docs/*.md docs/*/*.md`
Final answer: DONE (six pages end with the reviewed line).
Turn 2:
1. bash: `sed -i '/^-- reviewed 2026$/d' docs/legal/terms.md docs/legal/privacy.md`
2. bash: `tail -n 1 -q docs/*.md docs/*/*.md`
Final answer: DONE (legal pages have no footer, intro/setup/api/faq keep it).
Turn 3:
1. bash: `find docs -name '*.md' | xargs sed -i '/^-- reviewed 2026$/d'`
2. bash: `tail -n 1 -q docs/*.md docs/*/*.md`
Final answer: DONE (no page has the footer).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Append the reviewed footer to the live pages, take it off the legal ones, then remove it everywhere.
2. Add the review stamp at the bottom of docs pages (not drafts or README), undo for legal, finally strip all stamps.
3. Footer line on pages except drafts; legal pages without; then no footers at all.
4. Stamp the docs as reviewed, un-stamp legal, finally revert the entire change.
5. 给 docs 页面末尾加 reviewed 页脚，legal 两页去掉，最后全部撤销
