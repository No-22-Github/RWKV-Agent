# DISTILL-CANARY-f6b38fa1 : distillation case
import json
from datetime import datetime, timedelta

case = json.load(open("case.json"))
lines = case["files"]["logs/smtp-delivery.log"].splitlines()


def utc(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


def beijing(y, m, d, hh, mm, ss):
    # Beijing wall-clock window converted to UTC by subtracting 8 hours.
    return utc("%04d-%02d-%02d %02d:%02d:%02d" % (y, m, d, hh, mm, ss)) - timedelta(hours=8)


w1a, w1b = beijing(2026, 9, 24, 14, 0, 0), beijing(2026, 9, 24, 15, 0, 0)
w2a, w2b = beijing(2026, 9, 24, 15, 0, 0), beijing(2026, 9, 24, 16, 0, 0)
da, db = beijing(2026, 9, 24, 0, 0, 0), beijing(2026, 9, 25, 0, 0, 0)

w1 = w1_notest = w2 = busy = 0
codes = {}
for line in lines:
    if not line.strip() or "status=deferred" not in line:
        continue
    f = line.split()
    ts = utc(f[0] + " " + f[1])
    reason = line.split('reason="')[1].rstrip('"')
    code = reason.split()[0]
    rcpt = f[3]
    if w1a <= ts < w1b:
        w1 += 1
        if not rcpt.startswith("rcpt=mailer-test"):
            w1_notest += 1
    if w2a <= ts < w2b:
        w2 += 1
        codes[code] = codes.get(code, 0) + 1
    if da <= ts < db and "mailbox busy" in reason:
        busy += 1

top = sorted(codes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
forms = ["%d 封" % w1, "%d 封" % w1_notest, "%d 封" % w2, top, "%d 封" % busy]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
