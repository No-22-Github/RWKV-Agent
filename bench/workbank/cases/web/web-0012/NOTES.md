## Traps
- TR-FETCHFAIL: the first search result advertises https://wiki.harborlight.io/errors/HL-3312, but that entry carries a `url` and no `url_match`, so a fetch of it returns the not-found body. A model that stops after the dead first link answers UNKNOWN.
- TR-DECOY: the second result is a community thread about HL-3132 (tidebreak), a transposed-digit neighbour of the requested HL-3312. It ranks above the vendor reference, its title repeats a live-looking code, and its snippet and body both spell out tidebreak, so a model that skims the prominent result reports the wrong code's condition. The usable answer is on the third result, docs.harborlight.io/reference/errors, where HL-3312 is moatleak.

## Reference solution
1. Search "harborlight error HL-3312" (1)
2. Fetch wiki.harborlight.io/errors/HL-3312 - the advertised wiki page is gone; the fetch yields the not-found body (2)
3. Fetch community.harborlight.io/t/hl-3132-keeps-recurring - it explains HL-3132 as tidebreak, a different code (3)
4. Fetch docs.harborlight.io/reference/errors - the table row for HL-3312 gives the condition name moatleak (4)
5. Answer moatleak (5)

## Why the answer is unique
The vendor reference is the only entry that names HL-3312, and it gives exactly one condition, moatleak ("the primary's write lease and the quorum's view disagree"). Its own table also lists HL-3132 as tidebreak, which confirms that the community thread's tidebreak belongs to the transposed code and not to the requested one. The dead wiki entry has no content; no other entry assigns a condition to HL-3312. The only two plausible errors are therefore answering UNKNOWN after the dead link, or echoing the adjacent code's tidebreak.

## Five alternative phrasings of the task
1. harborlight error HL-3312 meaning
2. what does harborlight HL-3312 mean
3. harborlight HL-3312 condition name
4. harborlight error reference HL-3312
5. harborlight cluster error HL-3312 documentation

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `moatleak` failed the answer "Moatleak" - the capitalisation a model reaches
for when the term opens its reply. v2 uses `output_contains_any` with the
lowercase, capitalised and upper-case forms. The vendor term itself is
unchanged; only the spelling tolerance is.

<!-- WORKBANK-CANARY-cc41b7f2 : this file must never enter training corpora -->
