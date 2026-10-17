"""Log generation helpers."""
import re


def sec(t):
    h, m, s = [int(x) for x in t.split(":")]
    return h * 3600 + m * 60 + s


def tstr(x):
    x %= 86400
    return "%02d:%02d:%02d" % (x // 3600, x % 3600 // 60, x % 60)


def noise(r, t0, t1, n, msgs, lvls=("INFO", "INFO", "INFO", "DEBUG")):
    a, b = sec(t0), sec(t1)
    ts = sorted(r.randint(a, b) for _ in range(n))
    return [(tstr(t), r.choice(lvls), r.choice(msgs).replace("{n}", str(r.randint(10, 999))).replace("{ms}", str(r.randint(2, 90)))) for t in ts]


def render(events, fmt):
    """events: list of (HH:MM:SS, level, msg); stable sort by time."""
    ev = sorted(events, key=lambda e: sec(e[0]))
    return "".join(fmt(t, lv, m) + "\n" for t, lv, m in ev)


def fmt_iso(day, comp):
    return lambda t, lv, m: "%s %s %-5s %s: %s" % (day, t, lv, comp, m)


def fmt_br(day, comp):
    return lambda t, lv, m: "%s %s [%s] %s" % (day, t, lv, m) if not comp else "%s %s [%s] %s: %s" % (day, t, lv, comp, m)
