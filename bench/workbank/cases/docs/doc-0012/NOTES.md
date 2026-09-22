## Traps
- TR-RULEFILE: the body of the handbook gives the general permit validity in clause 6.1.1 ("valid for a period of 12 months"); the value that applies to the Northgate depot shuttle fleet sits in a second place, appendix D.1.1, which sets 36 months for a class P7 vehicle based at that depot and used only on the landside service roads, in place of clause 6.1.1. The request names exactly that fleet (depot-based, service roads only, never the apron), so the appendix value governs. A reader who works from clause 6.1.1, or who reads only the visible part of a 48KB handbook, records 12 months — the decoy. The applicable interval is 36 months.
- TR-LONG: handbook/airside-operations-handbook.md is about 48KB across 17 clauses and five appendices, and the applicable variation appears once, in the fourth appendix; the appendix also carries variations for the maintenance base, the cargo apron and the general aviation apron, so the reader has to reach and read the D.1 entry rather than stop at the first appendix heading.
- Grading note: both decoys are null per the bank convention for write-file cases (there is no single wrong value). expect.files requires the interval line "36 months" in notes/northgate-shuttle-permits.md; a file that states the general 12-month validity fails.

## Reference solution
1. list_files; the task set is README.md, handbook/airside-operations-handbook.md, handbook/section-index.json and the empty notes/ directory (1)
2. read_file README.md to learn that the index is revised with the handbook (2)
3. read_file handbook/airside-operations-handbook.md and find clause 6.1.1, the standard 12-month validity (3)
4. read_file handbook/section-index.json to locate the appendix that holds the site variations (4)
5. Read appendix D and its D.1.1 entry: a class P7 vehicle based at the Northgate depot and used only on the landside service roads holds a permit valid for 36 months in place of clause 6.1.1 (5)
6. write_file notes/northgate-shuttle-permits.md: header "# Northgate shuttle fleet - permit renewal", then "36 months" (6)

## Why the answer is unique
The handbook has one clause giving the standard permit validity (6.1.1, 12 months) and one entry varying it for the vehicles in question (D.1.1, 36 months for a depot-based class P7 vehicle used only on the landside service roads). Appendix D states its own effect — a variation applies only to the site and class it names and is granted only on the depot manager's written confirmation that the vehicle does not enter the apron — and the request describes exactly that class, so only 36 months can apply; a P7 vehicle that begins to work on the apron is expressly re-permitted and returns to clause 6.1.1's validity, which removes the other reading. Appendix B.2 fixes what class P7 covers, and the request's description ("used only on the landside service roads and never enters the apron") matches it rather than any other class. Numbers are not reused as a shortcut: the figure 36 appears once in the whole fixture. verify.py locates the two headed sections through handbook/section-index.json, derives the general value from clause 6.1.1 and the variation from D.1.1, and refuses a fixture in which the appendix does not vary the general value, so corrupting the index is detected.

<!-- WORKBANK-CANARY-82a5e3b7 : this file must never enter training corpora -->
