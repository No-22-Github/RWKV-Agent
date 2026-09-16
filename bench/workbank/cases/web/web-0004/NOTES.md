## Traps
- TR-WEBSTALE: the community recap page (ranks first, touched 2026-08-14 but only tracks the 1.x/2.x series) and the production blog (published_at 2025-10-14, ferrocache 2.6) both present 128 as the default. The vendor changelog ranks third; its 4.2.0 entry (2026-07-30) sets the default to 256. A model that stops at the recap or the blog answers 128.
- TR-SNIPPETVAGUE: no snippet states the current value; the recap's snippet dangles only "the original 64-shard layout". A model answering from the search results without opening any page grabs 64.

## Reference solution
1. web_search "ferrocache default shard_count" (1)
2. web_fetch cachefolk.net/ferrocache-shard-defaults — community recap: 1.x 64, 2.x 128, no current value (2)
3. web_fetch ferrumwheel.net/blog/ferrocache-shard-tuning — blog dated 2025-10-14, ferrocache 2.6 era, 128 (3)
4. web_fetch ferrocache.io/changelog — 4.2.0 (2026-07-30): "The default shard_count is now 256" (4)
5. answer 256 (5)

## Why the answer is unique
The changelog is the vendor's release history and its newest entry (4.2.0, 2026-07-30) states the current default in plain words ("is now 256"). The recap is a community page covering only the 1.x and 2.x series; the blog predates 4.2 and carries an in-content date and version. Dates are readable from published_at and from page content, so only one value can be the default of the current release.

## Five alternative phrasings of the task
1. ferrocache default shard_count
2. ferrocache shard count default value
3. how many shards does ferrocache create by default
4. ferrocache shard_count out-of-the-box setting
5. ferrocache docs default shard count

<!-- WORKBANK-CANARY-09d4f7b2 : this file must never enter training corpora -->
