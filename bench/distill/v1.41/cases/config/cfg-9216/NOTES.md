## Traps
- TR-READONLY: conf/audit.properties belongs to the compliance team (conf/README.txt).
- TR-DECOY: log4j.logger.audit=INFO is a named logger line that also ends in INFO.

## Reference solution
1. bash: `find conf -name '*.properties' | grep -v audit.properties | xargs sed -i 's/^log4j.rootLogger=INFO,/log4j.rootLogger=WARN,/'`
2. bash: `grep -rn log4j conf` to confirm the target files changed and the protected ones did not.
Final answer: DONE (app, worker, gateway and batch use rootLogger WARN; audit.properties and the audit logger lines are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Set log4j.rootLogger to WARN instead of INFO in the conf/*.properties files, except the one README forbids, then verify and say DONE.
2. Quiet the root logger: INFO becomes WARN in every properties file in conf that may be edited. Check and reply DONE.
3. conf 下的 .properties 把根日志级别由 INFO 改成 WARN，合规团队的文件和 audit logger 保持不变，检查后回复 DONE。
4. Lower the verbosity of rootLogger from INFO to WARN across conf, leaving audit.properties and log4j.logger.audit untouched. Reply DONE after checking.
5. Change the root logger level to WARN in the editable properties files in conf; use conf/README.txt for the exceptions; reply DONE when verified.
