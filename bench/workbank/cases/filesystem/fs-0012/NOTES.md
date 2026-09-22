## Traps
- TR-DECOY: release/manifest/crew_pairing_audit.txt and release/archive/crew_pairing_audit.txt share their file name in two folders, but their last line differs (rc3 vs rc4), so their stored bytes are not identical. A model that matches duplication by name reports the audit log (the recorded decoy); the byte-identical pair is the two .csv extracts.
- TR-NEARNAME: the question says the artifacts sit under release/manifests/, one character longer than the real directory release/manifest/. Nothing exists at release/manifests/, and README.md names the real folder, so a model that copies the question's folder into its answer reports release/manifests/crew-pairing-eu.csv (the recorded decoy). The real path is release/manifest/crew-pairing-eu.csv.

## Reference solution
1. list_files the workspace and see that release/ holds manifest/ and archive/, with no manifests/ entry (call 1)
2. read README.md for the release layout and the duplication rule (call 2)
3. read release/manifest/crew-pairing-eu.csv (call 3)
4. read release/manifest/crew_pairing_eu_copy.csv; the bytes match the first extract (call 4)
5. answer release/manifest/crew-pairing-eu.csv, one of the two identical copies (call 5)

## Why the answer is unique
Grouping every file by exact stored bytes leaves exactly one multi-member group, the two .csv extracts under release/manifest/; the two crew_pairing_audit.txt files differ on their last line. The folder the question names does not exist on disk and the README states the real directory release/manifest/, so the answer is unambiguously release/manifest/crew-pairing-eu.csv, or its identical twin release/manifest/crew_pairing_eu_copy.csv. verify.py regroups the fixture by content and returns the lexicographically first path of the single multi-member group.

<!-- WORKBANK-CANARY-c93f6d18 : this file must never enter training corpora -->
