"""Small deterministic log generator for the C2 log cases."""
import datetime
import random

SVC = ["api", "auth", "db", "cache", "queue", "web"]
INFO = ["request handled in %dms", "session refreshed", "connection pool at %d%%", "job %d dequeued", "cache hit ratio %d%%", "health check ok", "config reloaded"]


def make_log(seed, n, events, start="2026-09-14 20:00:00", fmt="{ts} {lvl:<5} {svc}: {msg}"):
    """events: {line_index: (level, service, message)}. Returns (text, timestamps list)."""
    rng = random.Random(seed)
    t = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    lines, stamps = [], []
    for i in range(n):
        t += datetime.timedelta(seconds=rng.randint(15, 70))
        ts = t.strftime("%Y-%m-%d %H:%M:%S")
        stamps.append(ts)
        if i in events:
            lvl, svc, msg = events[i]
        else:
            tpl = rng.choice(INFO)
            msg = tpl % rng.randint(3, 98) if "%" in tpl else tpl
            lvl, svc = "INFO", rng.choice(SVC)
        lines.append(fmt.format(ts=ts, lvl=lvl, svc=svc, msg=msg))
    return "\n".join(lines) + "\n", stamps
