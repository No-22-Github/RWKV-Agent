## Traps
- TR-EARLYHIT: the first result is the clay supplier's own note for the red stoneware
  loaded in the kiln and its snippet states the soak (35 minutes), so one search is
  enough and the case caps web_search at 1. The workspace holds no soak at all: the row is
  empty, and the blue stoneware note on the other page gives 20 minutes for a body the
  kiln is not carrying.

## Reference solution
1. list_files: the workspace holds kiln/firing-profile.csv and README.md.
2. read_file kiln/firing-profile.csv: soak_minutes has no value and clay_body is
   vennmoor-red; the README routes the soak to the clay supplier's note for that body.
3. web_search "vennmoor red stoneware firing note": the note for the red body is the first
   result and its snippet gives 35 minutes.
4. write_file kiln/firing-profile.csv with soak_minutes,35; the clay body, the ramp and
   the header are untouched. Then reply DONE.

## Why the answer is unique
The profile states the clay body and the README routes the soak to the supplier's note for
that body rather than to the kiln manual, so the red note is the only source. It gives 35
minutes and the blue note's 20 minutes applies to a body the kiln is not carrying, so
nothing is left to choose between. The blank row is filled in as soak_minutes,35.

## Five alternative phrasings of the task
1. vennmoor clay red stoneware firing note
2. vennmoor red stoneware soak minutes
3. vennmoor clay firing note soak
4. vennmoor blue stoneware firing note
5. vennmoor pottery firing profile soak
