## Traps
No traps. One search returns the Pellumbra releases page, whose own rule plus the
release table settle the answer.

## Reference solution
1. Search for the Pellumbra CLI releases; the only result is pellumbra.example/releases.
2. Open that page: a plain install takes the newest release on the stable channel.
   The stable rows carry builds 2410 and 2218, so a plain install gets 2410.

## Why the answer is unique
The page states the rule and lists every release with its channel, so the set a
plain install can pick up is the stable rows, and the page's own dates put 2410
(19 May 2026) after 2218 (8 November 2025). 2444 is a release candidate and the
page says candidates are never offered to plain installs; 2218 is kept only for
installs that never moved to 6.1.

## Five alternative phrasings of the task
1. pellumbra cli releases
2. pellumbra newest stable build
3. pellumbra cli plain install build number
4. pellumbra release channels and builds
5. pellumbra cli rollback build
