## Traps
- TR-NOTOOLNEED: headers/response-header-cards.tsv and README.md are workspace props. A caching directive is a property of HTTP, so nothing on disk has to be read before replying. The near-miss decoy `Cache-Control: no-cache` is what people reach for when they mean "do not reuse a stale copy": it still allows the response to be stored, and only forces a check with the origin before each reuse, so a copy does end up on disk.

## Reference solution
1. Answer from the caching rules: the directive that forbids writing a response to storage at all is `no-store`, and it travels in the `Cache-Control` response header.
2. Reply with the line `Cache-Control: no-store`.

## Why the answer is unique
The question asks for a header under which no copy may be written, and `no-store` is the only `Cache-Control` directive that forbids storage by every cache. `no-cache` is not a second reading of the question: a cache is allowed to store a `no-cache` response and only has to revalidate it before each reuse, so the copy the question rules out is still written. The files on disk restate the same rule for the delivery team and change nothing about it.
