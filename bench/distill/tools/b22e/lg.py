"""Synthetic log/table generators for b22e (fixed seeds, short lines)."""
import datetime as dt

LV = ["INFO"] * 14 + ["DEBUG"] * 4 + ["WARN"] * 2


def timeline(r, n, t0, span_s):
    """n monotone datetimes from t0 spread over span_s seconds."""
    base = sorted(r.randint(0, span_s) for _ in range(n))
    return [t0 + dt.timedelta(seconds=s) for s in base]


def build(r, n, t0, span_s, gen, plants=None):
    """gen(r, i, ts)->line; plants {idx: fn(ts)->line} override generated lines."""
    plants = plants or {}
    out = []
    for i, ts in enumerate(timeline(r, n, t0, span_s)):
        out.append(plants[i](ts) if i in plants else gen(r, i, ts))
    return out


def text(lines):
    return "".join(l + "\n" for l in lines)


def iso(ts):
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def isoz(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def nginx_ts(ts):
    return ts.strftime("%d/%b/%Y:%H:%M:%S +0800")


def sysl(ts):
    return ts.strftime("%b %d %H:%M:%S").replace(" 0", "  ", 1) if ts.day < 10 else ts.strftime("%b %d %H:%M:%S")


def pick(r, xs):
    return xs[r.randrange(len(xs))]


def ip(r):
    return "%d.%d.%d.%d" % (pick(r, [10, 172, 192, 203]), r.randint(0, 255), r.randint(0, 255), r.randint(2, 250))


PATHS = ["/api/orders", "/api/orders/{n}", "/api/users/{n}", "/api/cart", "/api/search", "/static/app.js", "/static/site.css",
         "/health", "/login", "/api/items/{n}", "/api/pay", "/img/{n}.png"]


def path(r):
    return pick(r, PATHS).replace("{n}", str(r.randint(100, 9999)))


def access_line(r, ts, status=None, p=None, method=None, size=None):
    st = status or pick(r, [200] * 30 + [304] * 6 + [301] * 2 + [404] * 3 + [499] + [500] + [502])
    return '%s - - [%s] "%s %s HTTP/1.1" %d %d' % (ip(r), nginx_ts(ts), method or pick(r, ["GET"] * 8 + ["POST"] * 3 + ["PUT"]),
                                                  p or path(r), st, size if size is not None else r.randint(120, 48000))


def access_gen(r, i, ts):
    return access_line(r, ts)


APP_MSGS = ["request {n} handled in {ms}ms", "cache hit key=u:{n}", "cache miss key=u:{n}", "session {n} refreshed", "worker {w} idle",
            "flush {n} rows to disk", "heartbeat ok peer=node{w}", "job {n} queued", "job {n} finished in {ms}ms", "config reload ok",
            "gc pause {ms}ms", "pool size {w}/16", "lease renewed ttl=30s", "metrics pushed ({n} series)"]


def fill(r, m):
    return (m.replace("{n}", str(r.randint(100, 99999))).replace("{ms}", str(r.randint(2, 480)))
             .replace("{w}", str(r.randint(1, 12))))


def app_gen(comps, msgs=None, lv=None):
    msgs = msgs or APP_MSGS
    lv = lv or LV

    def g(r, i, ts):
        return "%s %-5s %s: %s" % (iso(ts), pick(r, lv), pick(r, comps), fill(r, pick(r, msgs)))
    return g


def app_line(ts, level, comp, msg):
    return "%s %-5s %s: %s" % (iso(ts), level, comp, msg)


def jsonl_line(ts, lvl, svc, msg, extra=""):
    return '{"ts":"%s","lvl":"%s","svc":"%s","msg":"%s"%s}' % (isoz(ts), lvl, svc, msg, extra)


def jsonl_gen(svcs, msgs=None):
    msgs = msgs or ["request ok", "cache refreshed", "queue drained", "tick", "lease renewed", "batch committed"]

    def g(r, i, ts):
        return jsonl_line(ts, pick(r, ["info"] * 15 + ["debug"] * 4 + ["warn"]), pick(r, svcs), pick(r, msgs),
                          ',"ms":%d' % r.randint(1, 300))
    return g


def zh_gen(comps, msgs, lv=None):
    lv = lv or ["信息"] * 14 + ["调试"] * 4 + ["警告"] * 2

    def g(r, i, ts):
        return "%s [%s] %s: %s" % (iso(ts), pick(r, lv), pick(r, comps), fill(r, pick(r, msgs)))
    return g
