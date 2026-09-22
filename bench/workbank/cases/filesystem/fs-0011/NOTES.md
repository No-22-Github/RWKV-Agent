## Traps
- TR-ABSENT: the workspace holds no pumpnet-oncology.yaml. devices/pumpnet_inventory.csv lists oncology's configuration file as pumpnet-oncology.yaml and the files for the other two wards are present under devices/configs/, so a model that trusts the planning record replies devices/configs/pumpnet-oncology.yaml (the recorded decoy). The named file exists nowhere in the tree, and the README says a ward counts as configured only once its file is present, so the correct reply is UNKNOWN.

## Reference solution
1. list_files the workspace and read devices/pumpnet_inventory.csv (call 1)
2. read README.md for the devices/ layout and the configured-ward rule (call 2)
3. read the two configuration files present under devices/configs/ and confirm no oncology file exists (call 3)
4. reply UNKNOWN, because the requested path cannot be produced (call 4)

## Why the answer is unique
Only cardiology and geriatrics have configuration files under devices/configs/; nothing named pumpnet-oncology.yaml, or any oncology pump-network file, appears anywhere in the tree. The oncology row in the inventory is a planning record, not a file on disk, and the answer contract defines UNKNOWN as the reply when the answer cannot be determined, so UNKNOWN is the only correct reply. verify.py reads the inventory header, then checks whether the file it names for oncology is actually present; the header assertion makes corruption of the inventory's first line fail loudly.

<!-- WORKBANK-CANARY-7e2a95b4 : this file must never enter training corpora -->
