## Traps
- TR-NEARNAME: station jannerby-lane-33's lines contain the string of station jannerby-lane-3 as a prefix. Matching the station name loosely counts lane-33's 12 consignments together with lane-3's 26 and answers 38.

## Reference solution
1. List the workspace: README.md and logs/crate-intake.log.
2. Read README.md: two stations journal into one file and their names differ by one trailing character.
3. Read logs/crate-intake.log and count crate lines whose station field is exactly jannerby-lane-3 = 26.

## Why the answer is unique
The station field is a single token, so a line belongs either to exactly jannerby-lane-3 or to exactly jannerby-lane-33 and never to both. Lorry and QA lines carry no station field at all. Once the comparison is on the whole field, 26 is the only count left; 38 requires treating the shorter name as a prefix of the longer one, which the field format does not support.
