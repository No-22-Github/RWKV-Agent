# DISTILL-CANARY-3ce7cbfb : distillation case
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

l = next(x for x in case["files"]['game/match-server.log'].splitlines() if 'MATCH_ABORT' in x and not x.startswith("#"))
L = parse(l, 'sp', 'Asia/Shanghai').astimezone(ZoneInfo('Australia/Sydney'))
d, t = L.strftime("%Y-%m-%d"), L.strftime("%H:%M:%S")
if 'full' == "full":
    out = {"%s %s" % (d, t), "%sT%s" % (d, t), "%s %s" % (d.replace("-", "/"), t),
           "%d月%d日 %s" % (L.month, L.day, t), "%d 月 %d 日 %s" % (L.month, L.day, t)}
else:
    out = {t}
print(json.dumps({"expected_contains_any": sorted(out)}))
