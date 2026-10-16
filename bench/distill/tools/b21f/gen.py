"""Event generation and per-format bash fragments for b21f."""
import datetime as dt
from random import Random

from common import Ev, gen_times, ipaddr, rid, write_files

SVCS = [["orders", "payment", "inventory", "auth", "search"], ["gateway", "billing", "catalog", "session", "notify"],
        ["checkout", "profile", "media", "ledger", "sync"], ["api", "worker", "scheduler", "export", "mailer"]]
PATHS = [["/api/orders", "/api/cart", "/api/pay", "/api/items", "/login", "/health", "/api/search"],
         ["/v2/users", "/v2/invoices", "/v2/reports", "/v2/upload", "/auth/token", "/ping", "/v2/events"],
         ["/shop/list", "/shop/buy", "/shop/refund", "/account", "/static/app.js", "/status", "/feed"],
         ["/graphql", "/rest/jobs", "/rest/files", "/rest/mail", "/oauth/refresh", "/ready", "/rest/stats"]]
UAS = ["curl/8.1", "Mozilla/5.0", "okhttp/4.12", "python-requests/2.31", "Go-http-client/1.1"]
OK_MSG = ["request served", "cache hit", "ok", "completed"]
WARN_MSG = ["slow upstream", "retry scheduled", "rate limit near", "validation failed"]
ERR_MSG = ["upstream timeout", "db connection reset", "internal error", "pool exhausted"]


def pick(rng, pool, k=None):
    return rng.choice(pool) if k is None else rng.sample(pool, k)


def make_events(rng, n, start, span_s, fmt, vi, *, code=None, code_rate=0.08, decoy=True, ips=None, focus=None):
    """n events; `code` is the target status whose substring decoys appear in
    dur/bytes/path/ids of other lines when decoy is set."""
    svcs, paths = SVCS[vi % 4], PATHS[vi % 4]
    times = gen_times(rng, n, start, span_s)
    out = []
    for t in times:
        roll = rng.random()
        if code is not None and roll < code_rate:
            st = code
        elif roll < 0.62:
            st = rng.choice([200, 200, 200, 201, 204])
        elif roll < 0.78:
            st = rng.choice([301, 304, 400, 401, 404])
        elif roll < 0.90:
            st = rng.choice([404, 429, 500, 502, 503])
        else:
            st = rng.choice([200, 304])
        if code is not None and st == code and roll >= code_rate:
            st = 200
        lvl = "ERROR" if st >= 500 else "WARN" if st >= 400 else "INFO"
        msg = rng.choice(ERR_MSG if lvl == "ERROR" else WARN_MSG if lvl == "WARN" else OK_MSG)
        dur = int(rng.lognormvariate(4.6, 0.7))
        size = rng.randint(180, 9000)
        r = rid(rng)
        path = rng.choice(paths)
        e = Ev(ts=t, level=lvl, svc=rng.choice(svcs), path=path, method=rng.choice(["GET", "GET", "POST", "PUT"]),
               status=st, dur=dur, size=size, rid=r, ip=ipaddr(rng, ips), msg=msg,
               extra=rng.choice(UAS) if fmt == "nginx" else "worker-%d" % rng.randint(1, 6))
        if focus and st == code and rng.random() < 0.75:
            if focus.get("path"):
                e.path = rng.choice(focus["path"])
            if focus.get("svc"):
                e.svc = rng.choice(focus["svc"])
        if decoy and code is not None and st != code:
            d = rng.random()
            if d < 0.07:
                e.dur = code
            elif d < 0.12:
                e.size = code
            elif d < 0.15:
                e.path = rng.choice(paths) + "/%d" % code
        out.append(e)
    return out


def with_boundaries(events, times):
    """Replace the timestamps of the first len(times) events at spots near the
    given datetimes (kept sorted) so window edges are exercised exactly."""
    return events


# ---------------------------------------------------------------- bash fragments

def g_status(fmt, c):
    return {"nginx": "grep -F 'HTTP/1.1\" %d '" % c, "json": "grep -F '\"status\":%d,'" % c,
            "kv": "grep -F ' status=%d '" % c, "app": "grep -F 'status=%d '" % c}[fmt]


def g_path(fmt, p):
    return {"nginx": "grep -F ' %s HTTP'" % p, "json": "grep -F '\"path\":\"%s\"'" % p,
            "kv": "grep -F ' path=%s '" % p}[fmt]


def g_level(fmt, lv):
    return {"json": "grep -F '\"level\":\"%s\"'" % lv, "kv": "grep -F ' level=%s '" % lv.lower(),
            "app": "grep -F '] %s'" % lv.ljust(5)}[fmt]


def g_svc(fmt, s):
    return {"json": "grep -F '\"svc\":\"%s\"'" % s, "kv": "grep -F ' svc=%s '" % s, "app": "grep -F ' %s - '" % s}[fmt]


def tod_awk(fmt):
    """awk statements setting t = HH:MM:SS(.mmm), comparable as a string."""
    return {"nginx": "t=substr($4,14,8)",
            "json": "match($0,/\"ts\":\"[^\"]+/); t=substr($0,RSTART+17,12)",
            "kv": "match($0,/ts=[^ ]+/); t=substr($0,RSTART+14,12)",
            "app": "t=substr($0,12,12)"}[fmt]


def hms(fmt, h, m=0, s=0, ms=0):
    base = "%02d:%02d:%02d" % (h, m, s)
    return base if fmt == "nginx" else base + ".%03d" % ms


def stamp(e):
    return e.ts.strftime("%H:%M:%S") + ".%03d" % (e.ts.microsecond // 1000)


def plant(rng, evs, instants, *, status, path=None, svc=None, fmt="json", msg=None, durs=None, level=None):
    """Insert extra events at exact instants (window edges), cloned from a
    random existing event and forced to the given status/path/svc."""
    import copy
    out = list(evs)
    for n_, ts in enumerate(instants):
        e = copy.copy(rng.choice(evs))
        e.ts, e.status = ts, status
        e.level = "ERROR" if status >= 500 else "WARN" if status >= 400 else "INFO"
        e.rid = rid(rng)
        if level:
            e.level = level
        if path:
            e.path = path
        if svc:
            e.svc = svc
        if msg:
            e.msg = msg
        if durs:
            e.dur = durs[n_]
        out.append(e)
    out.sort(key=lambda x: x.ts)
    return out


def date_grep(fmt, day):
    """Fixed-string grep for one calendar day (day is a datetime.date)."""
    from common import MON
    if fmt == "nginx":
        return "grep -F '[%02d/%s/%d:'" % (day.day, MON[day.month - 1], day.year)
    return "grep -F '%s'" % day.isoformat()


def g_method(fmt, m):
    return {"nginx": "grep -F '\"%s '" % m, "json": "grep -F '\"method\":\"%s\"'" % m, "kv": "grep -F ' method=%s '" % m}[fmt]


def extract(fmt, by):
    """Pipeline fragment printing one value of field `by` per line."""
    if fmt == "nginx":
        return {"ip": "awk '{print $1}'", "path": "awk '{print $7}'"}[by]
    if fmt == "json":
        return "grep -o '\"%s\":\"[^\"]*\"' | cut -d'\"' -f4" % by
    if fmt == "kv":
        if by == "msg":
            return "grep -o 'msg=\"[^\"]*\"' | cut -d'\"' -f2"
        return "grep -o ' %s=[^ ]*' | cut -d= -f2" % by
    if fmt == "app":
        return {"svc": "awk '{print $5}'", "msg": "sed -E 's/.* - (.*) \\(req=.*/\\1/'"}[by]
    raise ValueError


def cond_greps(fmt, conds):
    out = []
    if "status" in conds:
        out.append(g_status(fmt, conds["status"]))
    if "level" in conds:
        out.append(g_level(fmt, conds["level"]))
    if "method" in conds:
        out.append(g_method(fmt, conds["method"]))
    if "path" in conds:
        out.append(g_path(fmt, conds["path"]))
    if "svc" in conds:
        out.append(g_svc(fmt, conds["svc"]))
    return out
