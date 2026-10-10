## Traps
- TR-NOTOOLNEED: the directive file and README are props for a standard front-end idiom. The near-miss decoy `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` sets the address header instead of the scheme header: it tells the upstream where the visitor came from, not whether the connection was encrypted, so absolute links built from it still come out as http.

## Reference solution
1. Answer from the front end's variable set: the request scheme is exposed as `$scheme`, and the header that carries it upward is `X-Forwarded-Proto`.
2. Reply with `proxy_set_header X-Forwarded-Proto $scheme;`.

## Why the answer is unique
The question asks for the scheme of the visitor's connection, and the front end has exactly one built-in variable for it, `$scheme`, together with one conventional header for passing it upstream, `X-Forwarded-Proto`. The address header answers a different question, and the constant `https` cannot answer this one because the same directive must also serve plain requests. Writing the header without the surrounding directive, or reading it back from a header that the front end already received, are the same answer spelled for a different placement.
