# DISTILL-CANARY-94b3eb8f : distillation case
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
assert hashlib.sha256(case["files"]['observatory/dome.log'].encode()).hexdigest() == 'bcd5883c897a1d2297f5b0eee5cfc68fb308002973a4f07d8feb833e1d3e86fb'
w1 = datetime.strptime('2026-02-17 19:00', "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo('America/New_York')).astimezone(UTC)
w2 = w1 + timedelta(hours=4)
ts = [parse(x, 'sp', 'Asia/Shanghai') for x in case["files"]['observatory/dome.log'].splitlines() if 'SHUTTER_FAULT' in x and not x.startswith("#")]
n = sum(1 for d in ts if w1 <= d < w2)
print(json.dumps({"expected_number": n}) if 'en' == "en" else json.dumps({"expected_contains_any": sorted({"%d%s%s" % (n, sp, u) for u in ['times', 'events', 'occurrences', 'instances', 'entries', 'lines', 'SHUTTER_FAULT'] for sp in [' ']})}))
