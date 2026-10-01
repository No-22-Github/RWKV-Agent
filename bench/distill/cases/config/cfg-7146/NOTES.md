## Traps
- TR-NEARNAME: two similar yaml files sit in config/; only irrigation.yaml is
  live, the wiring-audit-2025.yaml snapshot must stay byte-identical.
- TR-DECOY: run_pressure_bar appears in both sections and both files; editing
  the pump's 2.6 or the audit copy's 0.9 is the trap.

## Reference solution
1. Read README.md: irrigation.yaml is live, wiring-audit-2025.yaml is an archived snapshot the controller never reads.
2. Read both config files.
3. Change drip_lines' run_pressure_bar in irrigation.yaml from 1.0 to 1.3.
4. Leave the audit snapshot byte-identical.

## Why the answer is unique
The README fixes which file is live and says the audit snapshot stays as
archived, so the snapshot is out of bounds and the pump's 2.6 is the wrong key.
Only drip_lines' 1.0 in irrigation.yaml moves, the line shape is preserved,
and the final pair of files has exactly one possible content.
