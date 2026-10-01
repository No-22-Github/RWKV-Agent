## Traps
- TR-ABSENT: temperature_unit is defined in neither layer, so it has no
  effective value at all. The defaults' temp_log_interval_min (20) is the
  nearest temperature-flavoured key whose figure a conflating solver quotes.

## Reference solution
1. Read README.md: the two config layers, the fallback, and that a key in
   neither layer has no effective value.
2. Read config/coldchain.json: no temperature_unit.
3. Read config/coldchain-defaults.json: no temperature_unit either; the nearest
   temperature-flavoured key is temp_log_interval_min, a different setting.
   Final answer in two or three sentences per allocation v1.3 §4.1 row 1: name
   both files checked, say temperature_unit has no record in either layer, point
   to the nearest key without quoting its figure, and name the next step.
   Scored with output_contains_any over the key's three surface forms;
   output_excludes rules out UNKNOWN, the no-tools claim and the 20 figure.

## Why the answer is unique
The README states the instance config overrides the defaults, that unset keys
fall through, and that a key in neither layer has no value; those two files are
the whole config surface, so a key neither layer mentions has no effective
value at all. The decoy 20 is the defaults' temp_log_interval_min, a different
setting whose figure says nothing about a display unit; conflating the two is
the mistake the case is built around, so no reply that quotes a figure can be
right, and every accepted surface form names that one missing key.
