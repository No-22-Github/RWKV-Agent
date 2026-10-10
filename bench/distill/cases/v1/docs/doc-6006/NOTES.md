## Traps
- TR-ABSENT: no summary in the release log mentions SNMPv3. The nearest row is 1.9.4, which added SNMPv1 read-only monitoring, and a solver that reads the two as the same capability reports 1.9.4 instead of UNKNOWN.

## Reference solution
1. Read README.md, releases/release-log.csv and docs/engineer-checklist.md.
2. The release summaries name torque curves, SNMPv1 read-only monitoring, ramp-down, load balancing and a protocol tidy-up, and none of them mentions SNMPv3; README.md states that a capability no summary mentions has never shipped in a drive release, and the engineer checklist only reads SNMP figures off the plant room panel where a site has them enabled, with no version claim. No release introduced SNMPv3 polling.
3. Final answer in two or three sentences: name the files checked, say no release summary mentions SNMPv3 and so no version introduced it, and point to the log's only SNMP entry (an SNMPv1 read-only release) as a different protocol generation without quoting its version. Scored with output_contains_any over "SNMPv3", "snmpv3", "SNMPv3 polling" or "SNMP version 3"; output_excludes rules out UNKNOWN and the 1.9.4 SNMPv1 version, so the reply names the missing capability instead of quoting any version.

## Why the answer is unique
README.md states that a capability no summary mentions has never shipped, so a version that introduced SNMPv3 does not exist in the log. The decoy 1.9.4 is the SNMPv1 read-only release, a different protocol generation; reading one SNMP row as the other is the mistake the case is built around. The only truthful reply reports the absence: the release log, README.md and the engineer checklist were checked, no summary mentions SNMPv3, and the log's only SNMP entry is a different generation whose version is not the answer to the question.
