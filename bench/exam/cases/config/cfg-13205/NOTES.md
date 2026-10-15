## Traps
- TR-PRECEDENCE: each environment file overrides the base file's port (8080). Reading only the base file gives 8080 for both questions.
Turn 1 (prod) expects 8443; the correction (staging) expects 9443 on the first line. (r1: output_excludes 8443 wrongly failed a correct reply that listed all three files, so it was replaced by output_first_line_contains_any.)

## Reference solution
1. Read config/payments.prod.yaml -> 8443 (and see the base).
2. Read config/payments.staging.yaml -> 9443.

## Why the answer is unique
The environment files both set `port:` explicitly, so base 8080 is never effective. 9443 is staging's, 8443 prod's.

EXAM-CANARY-4f20170b
