## Traps
- TR-DECOY: The 2024 blog quotes 0.023, which is the file's current value; archive 0.004 and egress 0.05 are other lines.

## Reference solution
1. Read the basis https://stratus-cloud.com/object-storage/pricing: the new value is 0.021.
2. Read costmodel/rates.yaml: line 2, `standard_gb_month: 0.023`, is the one to change.
3. replace_lines line 2 with `standard_gb_month: 0.021`; the rest of the line stays.
4. Read costmodel/rates.yaml back to confirm.
Final answer example: costmodel/rates.yaml now has standard_gb_month 0.021, from Stratus's official pricing page; archive and egress are unchanged.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.

## Five alternative phrasings of the task
1. Stratus Object Storage pricing
2. Stratus Object Storage standard tier price
3. Stratus Object Storage GB-month 2026
4. Stratus Object Storage official rates
5. Stratus Object Storage price change
