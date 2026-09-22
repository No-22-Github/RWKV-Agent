## Traps
- TR-EARLYHIT: the first search result's snippet already states the answer outright ("TRD-1094 reports a coldshard: a cache region that never warmed after a worker restart"). One search is enough, so the case carries `expect.max_calls: {"web_search": 1}` (case-level, counted over the whole transcript): a second search call, including one the harness rejects as a duplicate, breaks the cap. The decoy a careless model lands on is hotloop: the same index page lists TRD-2211 (hotloop) above TRD-1094, and the second result is a thread about TRD-2211, so a model that distrusts the snippet and reads the top of the table instead of the named row reports the neighbouring code's condition.

## Reference solution
1. Search "tiderail error TRD-1094": the first result's snippet names the condition coldshard (1)
2. Answer coldshard (2)

## Why the answer is unique
The snippet and the index table both tie TRD-1094 to exactly one condition name, coldshard. The condition strings on that page are unique per code (TRD-2211 is hotloop, TRD-1088 is thinmoss), so hotloop is the name of a different code. The other results discuss TRD-2211 or probe tuning and never rename TRD-1094, so there is no second reading of the requested code.

## Five alternative phrasings of the task
1. tiderail TRD-1094 meaning
2. what does tiderail error TRD-1094 indicate
3. tiderail TRD-1094 condition name
4. tiderail error index TRD-1094 explained
5. tiderail TRD-1094 documentation

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `coldshard` failed the answer "Coldshard" - the capitalisation a model reaches
for when the term opens its reply. v2 uses `output_contains_any` with the
lowercase, capitalised and upper-case forms. The vendor term itself is
unchanged; only the spelling tolerance is.

<!-- WORKBANK-CANARY-5f0a93d1 : this file must never enter training corpora -->
