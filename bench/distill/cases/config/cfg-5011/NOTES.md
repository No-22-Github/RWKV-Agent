## Traps
- TR-PRECEDENCE: `queue_ceiling` is defined twice in the sheet, as 890 in the profile block and as 650 in the shipped defaults. The README states that the sources in `resolved_from` are consulted in order and the first one that defines a setting gives it its value, so the profile block wins; a solver that takes the shipped default, or that stops at the first block it happens to read, reports 650.

## Reference solution
1. Read `config/dispatch-settings.json`, the settings sheet the README describes.
2. Walk the three blocks in the order `resolved_from` lists. The runner exports do not define `queue_ceiling`; the profile block does, with 890, so the profile's value stands and the shipped default of 650 never applies. The answer is 890.

## Why the answer is unique
The README fixes the resolution order and `resolved_from` fixes which sources take part, so the profile block is the first source that defines `queue_ceiling`; the shipped defaults are only consulted for a setting no higher source mentions, which is not the case here. The decoy 650 is the shipped default of the same setting, a legitimate value for a deployment that changes nothing, but the production profile does change it, so 650 is not the value this service runs with. The answer is 890.
