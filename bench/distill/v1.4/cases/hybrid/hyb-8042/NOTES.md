## Traps
- TR-SUPERSEDE: the official page lists 11.5.0-rc.2 (release candidate) above the stable line; customers can only use the latest stable, 11.4.2. A blog post promotes the preview.

## Reference solution
1. Search Tidewater DB versions: the official release page and a blog post.
2. Fetch https://tidewater-db.org/channels: stable 11.4.2 (2026-09-02), preview 11.5.0-rc.2.
3. Read the local manifest for the installed version 11.3.0.
Final answer: Your manifest has Tidewater DB on 11.3.0. The newest stable Tidewater DB release customers can use is 11.4.2 (released 2026-09-02); 11.5.0-rc.2 is only on the release candidate channel and is not for production.
Criteria: contains 11.4.2 and 11.3.0; does not call 11.5.0-rc.2 the stable version; a fetch happened.

## Changelog
- v2：S5：题面补一句「本地文件里没写，去厂家/上游查」——原题面只指向本地清单，老师查完本地就收尾，从不上网（0–1/3）。

## Why the answer is unique
The question restricts to what customers/production can use, i.e. the stable channel; the only newer entry is a release candidate build, so 11.4.2 is the single correct version.

## Five alternative phrasings of the task
1. Tidewater DB release channels
2. tidewater db supported stable
3. Tidewater DB 11.5
4. tidewater db upgrade client
5. Tidewater DB releases
