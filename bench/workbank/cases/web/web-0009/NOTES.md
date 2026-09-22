## Traps
- None declared. This is the family's L0 baseline: one search, the vendor reference names the condition, one answer. Every fixture entry that touches the code agrees with the reference, so no careless reading yields a different condition name. The forum thread and the quarterly review are unrelated context, not decoys.

## Reference solution
1. Search "kelpgate error code KG-4021" (1)
2. Open docs.kelpgate.dev/reference/error-codes; the client-and-handshake table row for KG-4021 gives the condition name sealbreak (2)
3. Answer sealbreak (3)

## Why the answer is unique
Only the vendor reference states what KG-4021 reports, and it assigns exactly one condition name, sealbreak ("the upstream peer closed the connection partway through the TLS handshake"). The forum thread describes the same behaviour without naming it and explicitly defers to the reference page; the quarterly review says no code meaning changed and names none. No other fixture entry contains the string sealbreak or a competing name for KG-4021.

## Five alternative phrasings of the task
1. kelpgate error code KG-4021 meaning
2. what does kelpgate error KG-4021 indicate
3. kelpgate KG-4021 condition name
4. kelpgate gateway error KG-4021 explained
5. kelpgate error reference KG-4021

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `sealbreak` failed the answer "Sealbreak" - the capitalisation a model reaches
for when the term opens its reply. v2 uses `output_contains_any` with the
lowercase, capitalised and upper-case forms. The vendor term itself is
unchanged; only the spelling tolerance is.

<!-- WORKBANK-CANARY-3a7f1c9e : this file must never enter training corpora -->
