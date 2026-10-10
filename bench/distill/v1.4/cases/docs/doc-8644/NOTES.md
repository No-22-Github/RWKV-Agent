## Traps
- pending is not expired.

## Reference solution
1. Read permits/trucks.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file compliance/expired.md with the 9 lines below (first line is the head the prompt dictates).
   # Expired permits
   - FT-301 Grill Parade Park
   - FT-309 Noodle Wagon Park
   - FT-322 Noodle Wagon Park
   - FT-325 Falafel Express Market
   - FT-329 Falafel Express Pier
   - FT-335 Falafel Express Market
   - FT-341 Sweet Wheels Stadium
   Count: 7
3. Read compliance/expired.md back to confirm.
Final answer, one sentence: Wrote the summary to compliance/expired.md (9 lines). Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
