## Traps
- TR-FETCHFAIL: the first search result (community wiki, ranks first with a promising title and snippet) is a stale index entry; fetching its URL returns a "Page not found" body because the wiki page was removed. A model that gives up after the dead first link answers UNKNOWN. The working documentation page ranks second and carries the answer.

## Reference solution
1. web_search "quillmark serve default port" (1)
2. web_fetch wiki.quillmark.io/configuration — returns a page-not-found body (2)
3. web_fetch docs.quillmark.dev/reference/serve/ — the options table lists --port with default 8630 (3)
4. answer 8630 (4)

## Why the answer is unique
The serve command reference is the vendor documentation page; its options table marks --port with default 8630. The wiki entry carries no value (its page is gone), and the GitHub issue discusses the port-collision fallback without naming the default, pointing at the same reference page. No other fixture entry states a port value.

## Five alternative phrasings of the task
1. quillmark serve default port
2. quillmark preview server default port number
3. what port does quillmark serve use by default
4. quillmark docs serve port default value
5. quillmark preview server port setting default
