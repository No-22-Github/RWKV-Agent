## Traps
- TR-EARLYHIT: the first search result is the lift maker's own commissioning note for the
  gearless drive fitted to the car and its snippet states the trip speed (1.6 metres per
  second) outright, so one search is enough and the case caps web_search at 1. The
  workspace holds no trip speed at all: the row is empty, and the hydraulic note on the
  other page gives 0.8 for drives of a type the car does not have.

## Reference solution
1. list_files: the workspace holds lift/car-settings.csv and README.md.
2. read_file lift/car-settings.csv: governor_trip_speed_m_per_s has no value and
   drive_type is gearless; the README routes trip speeds to the maker's commissioning
   note for the drive type fitted.
3. web_search "wraysbury gearless commissioning note": the note for the gearless drive is
   the first result and its snippet gives 1.6 metres per second.
4. write_file lift/car-settings.csv with governor_trip_speed_m_per_s,1.6; the header, the
   door dwell and the drive type are untouched. Then reply DONE.

## Why the answer is unique
The drive type is stated by the settings table itself and the README routes trip speeds to
the maker's note rather than the maintenance handbook, so the note for that drive type is
the only source. The gearless note gives 1.6 metres per second and the hydraulic note's
0.8 applies to a drive the car does not have, so nothing is left to choose between. The
blank row is filled in as governor_trip_speed_m_per_s,1.6.

## Five alternative phrasings of the task
1. wraysbury lifts gearless commissioning note trip speed
2. wraysbury lift governor trip speed
3. wraysbury gearless drive commissioning note
4. wraysbury lift commissioning note trip speed
5. wraysbury lifts car settings trip speed
