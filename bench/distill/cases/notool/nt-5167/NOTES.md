## Traps
- TR-NOTOOLNEED: headers/cache-key-cards.tsv, README.md and notes/edge-review.txt are props. The header that tells a cache which request headers to key on is a property of HTTP, so no file has to be read. The near-miss decoy `Cache-Control: private` narrows who may be served from a stored copy but names no request header, so the cache still hands the compressed copy to a client that asked for the plain one.

## Reference solution
1. Answer from the caching rules: the response header whose value lists the request headers a stored copy varies on is `Vary`.
2. Reply with the line `Vary: Accept-Encoding`.

## Why the answer is unique
The question asks for a header that splits stored copies by what the client asked for, and `Vary` is the only header that enumerates request headers for the cache to key on; `Accept-Encoding` is the request header that carries the compression choice. `Cache-Control: private` cannot be a reading of the question: it says who may be served a stored copy, not which request headers distinguish one stored copy from another, so the mixed-up serving the question describes stays possible.
