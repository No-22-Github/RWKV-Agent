## Traps
- TR-EARLYHIT: the first result's snippet already carries a version, "the release we run, 3.2.1", beside a stable-looking operations write-up. A model that answers from that snippet alone reports 3.2.1 and never sees that the page is a 2025 retrospect of what a single company pinned. The case-level `expect.max_calls` of `{"web_search": 1}` also fails a trace that issues a second query, whether or not the harness rejects it as a duplicate, so the extra search cannot be used to recover.
- TR-WEBSTALE: the two pages that mention a version before the release page are both older than it. The Byteharbour write-up is dated 2025-11-05 and pins the 3.2 line; the Latticework walkthrough, dated 2026-01-22, was tested against 4.0.0. A model that fetches the walkthrough and stops there reports 4.0.0. Only the vendor release notes, ranked third, carry the newest tag.

## Reference solution
1. web_search "thornfield broker current release" (1) — one search, then work only with the returned results
2. web_fetch byteharbour.io/blog/thornfield-in-production — an operations write-up dated 2025-11-05 running 3.2.1; older than the release page (2)
3. web_fetch docs.latticework.dev/tutorials/thornfield-quickstart — a walkthrough last checked 2026-01-22, written against 4.0.0; still not the release page (3)
4. web_fetch thornfield.dev/releases — release notes newest first, top entry 5.1.0 dated 2026-08-27 (4)
5. answer 5.1.0 (5)

## Why the answer is unique
The release page is the broker's own tagged-release list and the only fixture entry that enumerates releases rather than describing one deployment. Its newest entry, 5.1.0 of 2026-08-27, postdates every other dated source in the fixture: the Byteharbour post of 2025-11-05 (3.2.1) and the Latticework walkthrough of 2026-01-22 (4.0.0). Each decoy is refuted by its own date and by its framing: a production retro describes what one operator pinned, and a tutorial describes what it was tested against, while only the release list states what has been published. The dates are readable both from the page bodies and from the results themselves, so there is exactly one newest release.

## Five alternative phrasings of the task
1. thornfield current release version
2. thornfield broker newest release
3. which thornfield release is current
4. thornfield releases page newest tag
5. thornfield broker release notes newest version

## Grading note
Same change as web-0014: v1's `output_equals: "5.1.0"` failed the reply
"5.1.0 (2026-08-27)", so v2 accepts both forms through `output_equals_any`.
It matters more here than on web-0014, because this case rewards a solver that
works out which page is current before answering - the solver most likely to
say where the number came from. It stays inside the `output_equals` family for
the reason web-0014's note gives: with no workspace files there is no sabotage
test, so that family is this case's only automated tie back to the fixture.

<!-- WORKBANK-CANARY-5e93c0b7 : this file must never enter training corpora -->
