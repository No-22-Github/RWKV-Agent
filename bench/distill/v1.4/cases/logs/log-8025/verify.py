# DISTILL-CANARY-4c996f00 : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]['logs/dryers-east/2026-09-05.log'].splitlines()
assert log[0].startswith('# dryers-east event log')
stamps = [re.match(r"2026-09-05T(\d\d):(\d\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
assert not any(1200 <= x < 1260 for x in minutes)
assert any('paused' in l for l in log) and any('not backfilled' in l for l in log)
words = ['gap', 'not collected', 'no logs', 'not shipped', 'not uploaded', 'paused', 'maintenance', 'no records', 'not recorded', 'no entries', 'blank', 'missing from', 'offline', 'not backfilled', "can't be counted", 'cannot be counted', 'no count', 'no lines']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
