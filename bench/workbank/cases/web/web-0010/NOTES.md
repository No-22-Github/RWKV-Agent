## Traps
- TR-FETCHFAIL: the first search result (a community wiki entry titled "copperlane CL-5812", ranks first with a promising snippet) is advertised with a URL that has no resolvable page, so fetching it returns the not-found body. The fixture entry deliberately carries a `url` but no `url_match`. A model that gives up after the dead first link answers UNKNOWN. The working vendor reference ranks second and names the condition.

## Reference solution
1. Search "copperlane error CL-5812" (1)
2. Fetch wiki.copperlane.io/errors/CL-5812 - the advertised wiki page is gone; the fetch yields the not-found body (2)
3. Fetch docs.copperlane.io/reference/errors - the table row for CL-5812 gives the condition name ledgerdrift (3)
4. Answer ledgerdrift (4)

## Why the answer is unique
The vendor error reference is the only fixture entry that assigns a condition name to CL-5812: ledgerdrift, "the posted ledger entries no longer reconcile against the settlement file". The community wiki entry has no reachable page and no content, and the status-page incident names no code. The other codes in the reference table carry different condition names (latefeed, gatehold, thincover), so the reply cannot be one of those without a misread of the row.

## Five alternative phrasings of the task
1. copperlane error CL-5812 meaning
2. what does copperlane CL-5812 mean
3. copperlane settlement error CL-5812 condition
4. copperlane error reference CL-5812
5. copperlane CL-5812 documentation name

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `ledgerdrift` failed the answer "Ledgerdrift" - the capitalisation a model reaches
for when the term opens its reply. v2 uses `output_contains_any` with the
lowercase, capitalised and upper-case forms. The vendor term itself is
unchanged; only the spelling tolerance is.

<!-- WORKBANK-CANARY-b62d8e04 : this file must never enter training corpora -->
