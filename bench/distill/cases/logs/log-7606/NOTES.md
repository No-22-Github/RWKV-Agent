## Traps
- TR-DECOY: the last line of logs/berthing-jun.log is a W1 load-sensor FAULT on 2026-06-25 (16:02) that cleared itself in nine minutes. Picking it as the failure tells the ops review the wrong winch and the wrong day; README says a self-clearing W1 sensor fault is the known loose-connector glitch and never suspends service.

## Reference solution
1. Read README.md: self-clearing W1 sensor faults are the known glitch; real suspensions are marked SUSPEND and the NOTE line names the finding.
2. Read logs/berthing-jun.log.
3. The SUSPEND line sits on 2026-06-23 after the W2 pressure-drop FAULT at 11:40; the NOTE finding is a hydraulic hose leak on W2.

## Why the answer is unique
The decoy 16:02 is the W1 sensor glitch. README rules it out as a service event (cleared within minutes, never suspends service), and unlike the W2 line it carries no SUSPEND marker, so the suspension story cannot start there. Only 2026-06-23 has a SUSPEND line, the FAULT on that day is the W2 pressure drop at 11:40, and the finding line names a hydraulic hose leak on W2. Each required fact is anchored to the SUSPEND marker, so no second reading exists.
