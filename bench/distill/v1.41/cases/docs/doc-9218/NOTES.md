## Traps
- TR-READONLY: policies/drafts holds unapproved drafts (policies/README.md).
- TR-DECOY: policies/README.md is itself a .md page in the same folder but not a policy.

## Reference solution
1. bash: `find policies -maxdepth 1 -name '*.md' | grep -v README | xargs sed -i '1a Last reviewed: 2026-10'`
2. bash: `head -n 3 policies/*.md` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four approved policies have the review line below the title; the drafts and the README are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Under each approved policy title in policies, insert `Last reviewed: 2026-10` on the next line; drafts and the README are excluded. Verify, then reply DONE.
2. Stamp the approved policies with a second line `Last reviewed: 2026-10` (right after the heading), following policies/README.md, then confirm and reply DONE.
3. policies 里已批准的政策页，在标题下一行插入 Last reviewed: 2026-10，草稿目录不动，检查后回复 DONE。
4. After the review, add `Last reviewed: 2026-10` below the first line of security, travel, expenses and remote work policies only, check, reply DONE.
5. Insert a review-date line `Last reviewed: 2026-10` under the title of every policy page except drafts and the README, then check and reply DONE.
