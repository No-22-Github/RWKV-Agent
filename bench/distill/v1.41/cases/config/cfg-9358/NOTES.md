## Traps
- TR-DECOY: `log_level_file: debug` lines are a different key, so those services are not at debug. TR-READONLY: override files of non-debug services stay (config/README.md), and so does every other key.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep -n '^log_level: debug$' config/services/*.yaml`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/^log_level: debug$/log_level: info/' config/services/api.yaml; rm config/overrides/api.debug.yaml; sed -i 's/^log_level: debug$/log_level: info/' config/services/report.yaml; rm config/overrides/report.debug.yaml; sed -i 's/^log_level: debug$/log_level: info/' config/services/sync.yaml; rm config/overrides/sync.debug.yaml`
2. bash: `ls config/overrides; grep -n '^log_level' config/services/*.yaml`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Which services are at log_level debug? Return them to info and remove their debug override files.
2. List the services whose own config says debug, then switch them to info and delete the matching overrides/<name>.debug.yaml.
3. Find services logging at debug; for each, change the level to info and remove its temporary debug override.
4. Debug-level services: name them, then lower them to info and clean up their debug overrides.
5. 哪些服务的日志级别是 debug？改回 info，并删掉它们的 overrides 文件
