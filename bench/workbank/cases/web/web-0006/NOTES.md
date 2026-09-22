## Traps
- TR-SUPERSEDE: two fixture pages give a different release for the same event. The migration post "Moving off analyzer_chain" (in-content date 2025-12-08) says analyzer_chain was deprecated in 3.9.0; the project's own release notes (newest entry 4.2.0, released 2026-06-23) record the deprecation under 4.2.0 and list 3.9.0 (2025-11-30) as an unrelated release. A model that takes the older, more directly worded page answers 3.9.0. The dates are readable from the page bodies (the post's byline date and the release-day dates in the notes), not from the URLs.

## Reference solution
1. web_search "glasswren analyzer_chain deprecated release" (1)
2. web_fetch indexnotes.press/glasswren-migration-notes — post dated 2025-12-08, claims the deprecation landed in 3.9.0 (2)
3. web_fetch glasswren.dev/release-notes — the 4.2.0 entry (2026-06-23) deprecates analyzer_chain, and the 3.9.0 entry (2025-11-30) shows no deprecation at all (3)
4. answer 4.2.0 (4)

## Why the answer is unique
The release notes are the project's own record of what each release shipped, and their entry for 4.2.0 states that analyzer_chain is deprecated in 4.2.0. The 3.9.0 answer is wrong on the record itself: the release-notes entry for 3.9.0 lists only query performance and a crash fix, so the release the blog names did not deprecate the option. The blog is a third-party post dated 2025-12-08, before 4.2.0 existed, and it describes the maintainers' roadmap rather than the shipped release. The StackVault thread names no version. Only one release can be the one in which the deprecation shipped.

## Five alternative phrasings of the task
1. glasswren analyzer_chain deprecated release
2. glasswren analyzer_chain when deprecated
3. glasswren release notes analyzer_chain deprecation
4. glasswren indexing option retirement versions
5. glasswren analyzer_chain pipeline_steps migration version

## Grading note
v2 puts each source's claim in its own snippet: the migration write-up says
3.9.0 and the release notes say 4.2.0, so the contradiction is visible at the
result layer and published_at (2025-12-08 against 2026-06-23) is what settles
it. In v1 both snippets were silent about the release, so the only way to see
the conflict at all was to open both pages - the L2 shape of web-0008 - and
TR-SUPERSEDE was never exercised at its own rung. Opening the release notes
still confirms the answer; what changed is that the case now separates
"noticed two sources disagree and preferred the newer, authoritative one"
from "read far enough".

<!-- WORKBANK-CANARY-2e8b41c9 : this file must never enter training corpora -->
