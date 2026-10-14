## Traps
- TR-DECOY: The policy keeps 200 days (the file's value) for pre-October certificates and also mentions the 30-day renewal window; the blog is from 2025.

## Reference solution
1. Read the basis https://lumencerts.org/policy/validity: the new value is 90.
2. Read config/renewal.yaml: line 2, `validity_days: 200`, is the one to change.
3. replace_lines line 2 with `validity_days: 90`; the rest of the line stays.
4. Read config/renewal.yaml back to confirm.
Final answer example: validity_days in config/renewal.yaml is now 90, per the Lumen Certs policy for certificates issued from 2026-09-01; renew_before_days stays 30.
Criteria: exact target file content.

## Changelog
- v2：S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.

## Five alternative phrasings of the task
1. Lumen Certs validity policy
2. Lumen Certs certificate lifetime 90 days
3. Lumen Certs maximum validity 2026
4. Lumen Certs new issuance policy
5. Lumen Certs renewal
