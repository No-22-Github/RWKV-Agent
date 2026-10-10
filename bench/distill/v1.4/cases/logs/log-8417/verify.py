# DISTILL-CANARY-f3088772 : distillation case
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
assert hashlib.sha256(case["files"]['game/match-server.log'].encode()).hexdigest() == '5ccd86375bace20537be678058916d0e3679babcd0a786917dfc6b41a58c4c48'
w1 = datetime.strptime('2026-07-09 20:30', "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo('Asia/Shanghai')).astimezone(UTC)
w2 = w1 + timedelta(hours=3)
ts = [parse(x, 'off', 'Europe/London') for x in case["files"]['game/match-server.log'].splitlines() if 'MATCH_ABORT' in x and not x.startswith("#")]
n = sum(1 for d in ts if w1 <= d < w2)
print(json.dumps({"expected_number": n}) if 'en' == "en" else json.dumps({"expected_contains_any": sorted({"%d%s%s" % (n, sp, u) for u in ['times', 'events', 'occurrences', 'instances', 'entries', 'lines', 'MATCH_ABORT'] for sp in [' ']})}))
