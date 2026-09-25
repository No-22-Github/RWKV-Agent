## Traps
- TR-EARLYHIT: the first search result is the lamp maker's own operating note and
  its snippet states the lamp power (68 percent) outright, so one search is
  enough and a second search is a redundant call; the case caps web_search at 1.
  The workspace holds no lamp power figure at all: the row is blank.

## Reference solution
1. list_files: the workspace holds press/cure-settings.csv and README.md.
2. read_file press/cure-settings.csv: lamp_power_percent has no value, lamp_type
   is mercury, and the README says lamp settings come from the lamp maker's note.
3. web_search "vantry ridgeline mercury lamp power": the operating note is the
   first result and its snippet gives 68 percent.
4. write_file press/cure-settings.csv with lamp_power_percent,68; the header, the
   belt speed and the lamp type are untouched. Then reply DONE.

## Why the answer is unique
The lamp type is fixed by the settings table itself and the README routes lamp
settings to the maker's note rather than the press manual, so the note is the
only source. Both of the maker's pages give 68 percent for a mercury head and
neither page carries a second power figure (the rating-plate warning names no
number), so there is nothing to choose between. The blank row is filled in as
lamp_power_percent,68.

## Five alternative phrasings of the task
1. vantry uv mercury head lamp power setting
2. ridgeline press curing unit lamp power percent
3. what lamp power does a ridgeline mercury head run at
4. vantry uv curing settings questions lamp power
5. ridgeline press cure settings table lamp power
