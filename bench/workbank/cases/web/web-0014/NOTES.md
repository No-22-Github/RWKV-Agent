## Traps
- TR-EARLYHIT: the first search result (threadneedle.io/releases) has a snippet that states the current stable release outright, 7.4.1, so one search is enough to answer. The case-level `expect.max_calls` of `{"web_search": 1}` fails a trace that issues a second search: the extra query is scored as redundant, whether or not it is rejected as a duplicate. A model that keeps searching and lands on the 7.3-era write-up reports 7.3.0.

## Reference solution
1. web_search "threadneedle newest stable release" (1) — the first result's snippet reads "The current stable threadneedle release is 7.4.1, published 2026-08-19."
2. answer 7.4.1 (2)

## Why the answer is unique
The releases page lists tagged releases newest first and its own summary line names 7.4.1 as the current stable release, dated 2026-08-19. The other entries cannot compete: the operations write-up is dated 2025-12-02 and pinned the 7.3 line a year earlier, and the repository README carries no version at all. Only one release can be the newest, and only one fixture entry asserts which one it is.

## Five alternative phrasings of the task
1. threadneedle newest stable release
2. threadneedle current release version
3. what version of threadneedle is current
4. threadneedle releases page current tag
5. threadneedle latest tagged release

## Grading note
v1 graded with `output_equals: "7.4.1"`. Answer normalization lowercases and
strips emphasis and trailing punctuation but nothing else, so the reply
"7.4.1 (2026-08-19)" - the release with the date the page prints beside it -
was scored wrong. v2 uses `output_equals_any` and accepts both forms.

It stops there rather than moving to a substring check, which would tolerate
any wording. This case has no workspace files, so verify_all skips the
sabotage test on it, and matching verify.py's extracted string against the
`output_equals` family is the only automated tie between the expectation and
the fixture it came from. A substring expectation is invisible to that check
(verify_all collects `output_equals` / `output_equals_any` / `expected_number`
only), and the case would be left with no cross-check at all. Wider tolerance
is worth having, and it is filed with the S-C tools item: once verify_all
collects `output_contains`, this can become a contains-check.

<!-- WORKBANK-CANARY-2f8a6d05 : this file must never enter training corpora -->
