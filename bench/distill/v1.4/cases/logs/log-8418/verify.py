# DISTILL-CANARY-9c558105 : distillation case
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

import hashlib
from datetime import timedelta
assert hashlib.sha256(case["files"]['port/ferry-ops.log'].encode()).hexdigest() == 'd67cb4a1ef9ef25b118905a32ba76cbe8ca071802f43dbc7a3531749c70f9685'
w1 = datetime.strptime('2026-10-14 00:00', "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo('Europe/London')).astimezone(UTC)
w2 = w1 + timedelta(hours=5)
ts = [parse(x, 'z', 'Asia/Shanghai') for x in case["files"]['port/ferry-ops.log'].splitlines() if 'DEPARTURE_HOLD' in x and not x.startswith("#")]
n = sum(1 for d in ts if w1 <= d < w2)
print(json.dumps({"expected_number": n}) if 'en' == "en" else json.dumps({"expected_contains_any": sorted({"%d%s%s" % (n, sp, u) for u in ['times', 'events', 'occurrences', 'instances', 'entries', 'lines', 'DEPARTURE_HOLD'] for sp in [' ']})}))
