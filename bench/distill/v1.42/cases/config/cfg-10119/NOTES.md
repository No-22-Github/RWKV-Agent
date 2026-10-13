## Traps
- TR-READONLY: modules-vendor/aws-legacy stay unchanged per infra/terraform/README.md.
- Decoy line `  # dr_region default = "us-east-1"` shares text with the target line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find infra/terraform -name 'variables.tf' -not -path '*/modules-vendor/*' | xargs sed -i 's|^  default = "us-east-1"$|  default = "eu-west-1"|'`
2. bash: `grep -rn 'default' infra/terraform`
Final answer: Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
