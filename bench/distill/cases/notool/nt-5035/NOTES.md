## Traps
- TR-NOTOOLNEED: the run sheet and the brewery table are in the workspace, and the keg's own 15.5 gallons are booked on the run sheet itself. Treating the keg as the barrel doubles the return to 2,572.

## Reference solution
No steps; ref_calls is 0. 1,286 kegs x 15.5 gallons / 31 gallons per barrel. The answer is 643.

## Why the answer is unique
A US brewery barrel is 31 gallons and a keg is 15.5 gallons, so 1,286 kegs hold 1,286 x 15.5 / 31 = 643 barrels. 2,572 is twice that, i.e. the fill counted as if each keg were a whole barrel; the run sheet books the keg's 15.5 gallons and the table keys 31 gallons to the barrel, so the two units are distinct and the return is half the keg count.
