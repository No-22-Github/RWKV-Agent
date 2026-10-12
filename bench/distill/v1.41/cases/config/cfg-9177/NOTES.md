## Traps
- TR-DECOY: config/retention.yaml.example says 14; the live file says 30.

## Reference solution
1. read_file config/retention.yaml
Final answer: Application logs are kept for 30 days (config/retention.yaml; the .example file has 14).

## Why the answer is unique
The user names config/retention.yaml; only it holds the live value.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. In config/retention.yaml, how many days are application logs kept?
2. What log retention (in days) does config/retention.yaml set?
3. According to config/retention.yaml, for how long do we keep logs?
4. Check config/retention.yaml: logs_days is set to what?
5. How many days of logs does the retention config keep?
