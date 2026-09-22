## Traps
- TR-SNIPPETVAGUE: no snippet in the result list carries the release the question asks for. The deprecations page ranks second with an index-level snippet ("options that have been adjusted or retired"), and only its body gives the concrete row media_priority / deprecated in 6.1.0. The snippet that does carry a version belongs to the 6.4.0 release news item, so a model that answers from the result list without opening a page answers 6.4.0.

## Reference solution
1. web_search "tidalforge media_priority deprecated version" (1)
2. web_fetch tidalforge.dev/news/scheduler-rework-6-4 — the 6.4.0 news item (released 2026-08-05) describes media handling moving into the profile but names no deprecation release for media_priority (2)
3. web_fetch docs.tidalforge.dev/reference/deprecations — the scheduler table row for media_priority gives "Deprecated in" 6.1.0 (3)
4. answer 6.1.0 (4)

## Why the answer is unique
The deprecations page is the vendor's own index and its scheduler table gives exactly one release for media_priority, 6.1.0. The 6.4.0 answer is wrong because that news item never states when the option was deprecated: it announces a scheduler rework and defers the per-option record to the deprecation index, so 6.4.0 is the release in which the news was published, not the release that deprecated the option. The Forge Farm thread also names no version and points at the same index. Only one row in the fixture states a deprecation release for media_priority.

## Five alternative phrasings of the task
1. tidalforge media_priority deprecated version
2. tidalforge media_priority retirement release
3. tidalforge docs deprecations media_priority
4. tidalforge when was media_priority retired
5. tidalforge media_priority media_policy replacement version

<!-- WORKBANK-CANARY-a37d5e02 : this file must never enter training corpora -->
