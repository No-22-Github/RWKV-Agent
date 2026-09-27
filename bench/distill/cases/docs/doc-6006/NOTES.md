## Traps
- TR-ABSENT: no summary in the release log mentions SNMPv3. The nearest row is 1.9.4, which added SNMPv1 read-only monitoring, and a solver that reads the two as the same capability reports 1.9.4 instead of UNKNOWN.

## Reference solution
1. Read README.md: the log is one row per release and a capability no summary mentions has never shipped.
2. Read releases/release-log.csv: the summaries name torque curves, SNMPv1 read-only monitoring, ramp-down, load balancing and a protocol tidy-up; SNMPv3 is not among them.
3. Read docs/engineer-checklist.md: SNMP figures are read off the plant room panel where a site has them enabled, with no version claim. The answer is UNKNOWN.

## Why the answer is unique
The README states that a capability no summary mentions has never shipped, so a version that introduced SNMPv3 does not exist in the log. The decoy 1.9.4 is the SNMPv1 read-only release, a different protocol generation; reading one SNMP row as the other is the mistake the case is built around. The answer is UNKNOWN.
