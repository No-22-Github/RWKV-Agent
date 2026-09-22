## Traps
- TR-LONG: the target page, docs.bellwether.dev/operating/sizing-and-limits, runs about 4,700 words (roughly 27.7 KB, an estimated 5,100-7,200 tokens), well past the fetch compression threshold, and the value is named exactly once, inside the prose sentence "The shipped default for max_concurrent_evaluations is 640 per node" in the Concurrency limits subsection. The page carries a dense Limits reference table near the end whose first row is a different concurrency setting, max_concurrent_publishes at 512; a model that works from a shortened view of the page, or that skims the table instead of reading the section that names the setting, reports 512.

## Reference solution
1. web_search "bellwether max_concurrent_evaluations default" (1)
2. web_fetch docs.bellwether.dev/operating/sizing-and-limits — read the Evaluation throughput section; the Concurrency limits subsection states the shipped default is 640 per node, and no other passage names a value for this setting (2)
3. answer 640 (3)

## Why the answer is unique
The operations guide is the only fixture entry that documents this setting, and within it the string 640 occurs exactly once, in the sentence that names max_concurrent_evaluations. The 512 that a skimmer may pick up belongs to max_concurrent_publishes, a different setting with its own row in the Limits reference table, and the changelog and forum thread do not state any default at all. A reader who follows the setting name to its sentence cannot reach any value other than 640.

## Five alternative phrasings of the task
1. bellwether max_concurrent_evaluations default
2. bellwether shipped value for max_concurrent_evaluations
3. what is bellwether's default max_concurrent_evaluations
4. bellwether operations guide max_concurrent_evaluations default
5. bellwether evaluator concurrency limit default

<!-- WORKBANK-CANARY-a1d74e28 : this file must never enter training corpora -->
