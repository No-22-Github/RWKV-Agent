## Traps
- TR-NEARNAME: docs/oncall-handbook.md cites configs/quota.yaml, but the file on disk is
  configs/quota.yml (the README states the .yml convention). A model that stops at the stale
  name never reaches the file, and the most conspicuous figure nearby is the enterprise
  tier's 500000.

## Reference solution
1. read_file docs/oncall-handbook.md: the quota file is cited as configs/quota.yaml.
2. list_files configs/: the actual file is configs/quota.yml.
3. read_file configs/quota.yml. Turn 1: pro monthly_quota = 50000. Turn 2: trial monthly_quota = 2000. Turn 3: the file's closing comment says over-quota tenants are throttled, not rejected. Turn 4: pro burst_per_sec 20 halved = 10.

## Why the answer is unique
The .yaml name resolves to nothing on disk, and the README's .yml convention plus the single quota file leave exactly one candidate. Inside it the tier keys separate the three quotas (2000 / 50000 / 500000), so the pro answer is 50000 and the trial answer 2000; the throttle line is the only statement about over-quota behaviour and halves the per-second burst, giving 10.

## Five alternative phrasings of the task
1. changfeng software tenant quota file pro tier
2. monthly api quota for the pro tier
3. trial tier monthly quota number
4. what happens when the monthly quota is exceeded
5. throttled requests per second after quota
