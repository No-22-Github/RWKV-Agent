## Traps
- TR-DECOY: two further issuer declines sit just outside the window edges (19:39 and one more), and WARN retry lines share the 'card declined' wording inside the window. Including the edges answers 23; only the entries inside 19:40:00-19:55:00 count: 21.

## Reference solution
1. Read README.md: line grammar and the issuer-decline wording.
2. Search 'card declined' and read the line windows around the hits.
3. Keep pay-gateway ERROR lines whose message opens with 'card declined by issuer'.
4. Compare timestamps with the window edges; the count inside is 21.

## Why the answer is unique
The window edges are quoted in the prompt and no event lands exactly on them; the retry WARNs are WARN level and their message opens differently. The in-window count is 21.
