# DISTILL-CANARY-342aa1ae : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/payment-gw/2026-09-14.log"].splitlines()
assert log[0].startswith("# payment-gw warn log, host gw-02")
stamps = [re.match(r"2026-09-14T(\d\d):(\d\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
# No line at all falls inside 02:00-03:00: the collector paused at 01:47 and resumed at 03:41.
assert not any(120 <= x < 180 for x in minutes)
assert any("shipping paused" in l for l in log) and any("not backfilled" in l for l in log)
words = ["中断", "暂停", "维护", "没有采集", "没有推送", "没有日志", "缺失", "空白", "没有记录"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
