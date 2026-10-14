## Traps
- TR-SUPERSEDE: the official page lists 8.1.0-beta.1 (beta) above the stable line; customers can only use the latest stable, 8.0.6.

## Reference solution
1. Search Ember Cache versions: the official release page.
2. Fetch https://embercache.io/download: stable 8.0.6 (2026-09-04), preview 8.1.0-beta.1.
3. Read the local manifest for the installed version 7.2.9.
Final answer: Your manifest has Ember Cache on 7.2.9. The newest stable Ember Cache release customers can use is 8.0.6 (released 2026-09-04); 8.1.0-beta.1 is only on the beta channel and is not for production.
Criteria: contains 8.0.6 and 7.2.9; does not call 8.1.0-beta.1 the stable version; a fetch happened.

## Changelog
- v2：S5：题面补一句「本地文件里没写，去厂家/上游查」——原题面只指向本地清单，老师查完本地就收尾，从不上网（0–1/3）。

## Why the answer is unique
The question restricts to what customers/production can use, i.e. the stable channel; the only newer entry is a beta build, so 8.0.6 is the single correct version.

## Five alternative phrasings of the task
1. Ember Cache download
2. ember cache production version
3. Ember Cache 8.1
4. ember cache recommended release
5. Ember Cache latest
