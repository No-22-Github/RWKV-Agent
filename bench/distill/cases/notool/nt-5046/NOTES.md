## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The programme codes run in a near-identical series, so a reply built from the wrong row gives KBS-4520.

## Reference solution
1. Read finance/cost-centre-register.txt; the cold chain retrofit row gives KBS-4410 (one lookup, matching ref_calls 1).

## Why the answer is unique
The register issues one code per programme and the README says a code stays with its programme for life, so the cold chain retrofit has a single cost centre recorded. KBS-4520 belongs to the fleet refit. The answer is KBS-4410.
