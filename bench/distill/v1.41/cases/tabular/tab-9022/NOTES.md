## Traps
- TR-MULTISRC: four site ledgers; the north site alone gives 5940 units.
- TR-DECOY: ALU-100 and ALU-10X share the ALU-10 prefix, and receipt-void rows contain the word receipt; a prefix or substring match gives 57024 units.
- TR-DEFN: the ledgers count cartons, ledgers/README.md says 12 units per carton; the question asks for units (cartons alone is 1539).

## Reference solution
1. bash: `cat ledgers/q3/*.csv | awk -F, '$1=="ALU-10" && $3=="receipt" {s+=$2} END{print s*12}'`
Final answer: 18468 units of ALU-10 were received in Q3 (1539 cartons x 12; ALU-100, ALU-10X and receipt-void rows excluded).

## Why the answer is unique
SKU and type are exact fields and the README fixes the unit conversion.
