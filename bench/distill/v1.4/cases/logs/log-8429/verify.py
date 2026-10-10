# DISTILL-CANARY-f9716623 : distillation case
import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse(l, style, tz):
    if style == "z":
        return datetime.strptime(l[:20], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    if style == "sp":
        return datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    if style == "sys":
        m = re.match(r"(\w{3}) +(\d+) (\d\d:\d\d:\d\d)", l)
        return datetime.strptime("2026 %s %s %s" % (MON.index(m.group(1)) + 1, m.group(2), m.group(3)), "%Y %m %d %H:%M:%S").replace(tzinfo=UTC)
    if style == "loc":
        return datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(tz)).astimezone(UTC)
    return datetime.fromisoformat(l[:25]).astimezone(UTC)


case = json.load(open("case.json"))
for _p, _t in case["files"].items():  # the clock basis is declared on the first line of each log
    if _p.endswith(".log"):
        assert _t.startswith("# ")

dev = [x for x in case["files"]['port/berth-desk.log'].splitlines() if 'DEPARTURE_HOLD' in x and not x.startswith("#")]
assert len(dev) == 1
T = parse(dev[0], "loc", 'Australia/Sydney')
hit = [x for x in case["files"]['port/ferry-ops.log'].splitlines() if 'DEPARTURE_HOLD' in x and not x.startswith("#") and parse(x, 'sys', "UTC") == T]
assert len(hit) == 1
print(json.dumps({"expected_contains_any": [re.search(r"id=(EV-\d+)", hit[0]).group(1)]}))
