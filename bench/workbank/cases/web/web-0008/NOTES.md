## Traps
- TR-SUPERSEDE: the community option history (in-content date 2026-01-14, covering the 8.x line) says session_ttl_minutes was deprecated in 8.5.0, while the vendor's release notes record the deprecation under 9.3.0 (released 2026-07-09). A model that takes the community page's release answers 8.5.0. Dates are readable from the page bodies (the "last touched" line and the release-day dates), not from the URLs.
- TR-SNIPPETVAGUE: neither page that carries a deprecation release states one in its snippet. The community page's snippet says only that options "changed across the 8.x line", and the release notes' snippet says only that it covers the 8.x and 9.x series. The only snippet containing a version belongs to the 9.5.0 news item, so a model that answers from the result list grabs 9.5.0.

## Reference solution
1. web_search "marrowgate session_ttl_minutes deprecated version" (1)
2. web_fetch authwiki.net/marrowgate-option-history — community page last touched 2026-01-14, claims the deprecation landed in 8.5.0 (2)
3. web_fetch marrowgate.io/news/passkeys-in-9-5 — the 9.5.0 news item (released 2026-08-28) names no deprecation release for session_ttl_minutes (3)
4. web_fetch docs.marrowgate.io/release-notes — the 9.3.0 entry (2026-07-09) deprecates session_ttl_minutes; the 9.5.0 entry (2026-08-28) does not (4)
5. answer 9.3.0 (5)

## Why the answer is unique
The release notes are the vendor's record of what each release did, and their 9.3.0 entry states that session_ttl_minutes is deprecated in 9.3.0. The 8.5.0 answer is wrong on two counts: the community page is dated 2026-01-14 and covers only the 8.x line, and the vendor's own notes list 9.0.0 (2026-02-03) and 9.3.0 with no 8.5.0 deprecation entry at all, so no page but the community one asserts 8.5.0. The 9.5.0 answer is wrong because the news item is about passkey sign-in: its version is the release date of the announcement, and it explicitly defers the per-key record to the release notes. Only one entry in the fixture states a deprecation release for session_ttl_minutes.

## Five alternative phrasings of the task
1. marrowgate session_ttl_minutes deprecated version
2. marrowgate session_ttl_minutes retirement release
3. marrowgate release notes session_ttl_minutes
4. marrowgate when was session_ttl_minutes deprecated
5. marrowgate session idle_timeout replacement version

<!-- WORKBANK-CANARY-91c40fb6 : this file must never enter training corpora -->
