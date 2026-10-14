## Traps
- TR-NEARNAME: the delivery note calls it unit three; the bank's naming rule
  makes it compressor_3 (not a copy of compressor_2 or a free-form name).
- TR-DECOY: both existing units cut out at -12; copying a sibling's cutout
  instead of the plate-freezer -18 is the trap, as is inventing a nonzero
  service counter.

## Reference solution
1. Read README.md: the new unit enters as compressor_3 with the sibling keys, cutout_c: -18 and service_due_h: 0, appended at the end in the two-space style.
2. Read config/compressors.yaml.
3. Append the compressor_3 section, leaving every existing line byte-identical.

## Why the answer is unique
The README fixes the section name, key set, cutout, starting service counter,
placement and indentation, so the appended block and the resulting file each
have exactly one possible content; copying -12 would mis-tune the plate
freezers and a nonzero counter would invent service hours the unit does not
have.
