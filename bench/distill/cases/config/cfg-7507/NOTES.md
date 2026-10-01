## Traps
- TR-DECOY: conf/base.ini 的 daily_api_calls=1500 会被租户文件的 3000 覆盖，bulk_rows 则沿用 base 的 800。 A careless pass reports `1500`.

## Reference solution
1. Read the merge note at the bottom of conf/base.ini.
2. Read conf/tenant-huadong.ini and apply it over base key by key.
3. Read out daily_api_calls, bulk_rows and retention days after the merge.

## Why the answer is unique
The merge note says the tenant file overrides base per key and everything else carries over, so daily_api_calls becomes 3000 and days becomes 30, while bulk_rows has no tenant override and stays 800. tenant-north.ini belongs to a different tenant, so its 1200 never enters the Huadong merge.
