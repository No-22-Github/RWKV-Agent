## Traps
- TR-AMBIG: the first message asks for the packing on eleven crates without saying which crate the order leaves in. The charge sheet carries both crate sizes (standard 3.75, deep 5.20) and nothing in the workspace says which crate was agreed, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn names the deep crates and the answer is eleven at 5.20: 57.20. The careless answer is 41.25, the same eleven crates on the standard charge.

## Reference solution
1. Turn 1: ask which crate the order leaves in, since the packing charge follows the crate; no calls.
2. Turn 2 (deep crates named): read packing/crate-charges-2026-09.csv and take the deep crate charge of 5.20. Eleven crates give 57.20, a total of 2 calls.

## Why the answer is unique
Once the crate is named one row of the charge sheet is left: the deep crate at 5.20, and eleven of them come to 57.20. The decoy 41.25 is the same eleven crates on the standard charge, and the README says the charge follows the crate that goes out, so 41.25 cannot answer an order leaving in deep crates. Nothing in the workspace says which crate the Merryfield order uses, so the choice belongs to the requester and no reading of the files settles it before the second turn.
