"""M6 (v1.4 §3.6) b10d part B: time-zone conversion over logs, log-8400..8429.

The 30 cases are rows of ROWS (below); one generic builder turns a row into a
log file (>=150 lines, generated from a fixed seed) plus the question. Kinds:
  first  time of the first KEY event, converted to another zone
  count  KEY events inside a local-time window
  join   a local-time device log quotes an incident; find the UTC-log line
"""
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from common import revised
write_case = revised({"log-%d" % n: "S5：read_file 上限 1→2（对表题要读设备日志和服务端日志两份文件）；英文计数题改为 token 只认数字本身（老师常以「6.」开头）；终答上限 400→600（老师要写清换算口径和区间边界，三遍里多次超 400 被判挂）。" for n in range(8400, 8430)})

MAXREAD = {"max_calls": {"read_file": 2}}
UTC = timezone.utc
# key -> (tz database name, zh name, en name)
ZONES = {
    "bj": ("Asia/Shanghai", "北京", "Beijing"),
    "sg": ("Asia/Singapore", "新加坡", "Singapore"),
    "tk": ("Asia/Tokyo", "东京", "Tokyo"),
    "ld": ("Europe/London", "伦敦", "London"),
    "db": ("Asia/Dubai", "迪拜", "Dubai"),
    "in": ("Asia/Kolkata", "印度", "India"),
    "sy": ("Australia/Sydney", "悉尼", "Sydney"),
    "ny": ("America/New_York", "纽约", "New York"),
    "la": ("America/Los_Angeles", "洛杉矶", "Los Angeles"),
    "be": ("Europe/Berlin", "柏林", "Berlin"),
    "se": ("Asia/Seoul", "首尔", "Seoul"),
}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def utc_dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def loc(dt, zk):
    return dt.astimezone(ZoneInfo(ZONES[zk][0]))


def off_min(dt, zk):
    return int(loc(dt, zk).utcoffset().total_seconds() // 60)


def off_str(dt, zk):
    m = off_min(dt, zk)
    return "%s%02d:%02d" % ("+" if m >= 0 else "-", abs(m) // 60, abs(m) % 60)


def stamp(dt, style, zk="bj"):
    if style == "z":
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if style == "sp":
        return dt.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    if style == "sys":
        return "%s %2d %s" % (MON[dt.month - 1], dt.day, dt.strftime("%H:%M:%S"))
    if style == "loc":  # bare local clock, no offset
        return loc(dt, zk).strftime("%Y-%m-%d %H:%M:%S")
    l = loc(dt, zk)  # "off": ISO with the log zone's own offset
    return l.strftime("%Y-%m-%dT%H:%M:%S") + off_str(dt, zk)


def basis(style, zk, lang):
    """One header sentence saying which clock the stamps use."""
    if style == "loc":
        n = ZONES[zk]
        return ("时间戳为%s当地时间（无偏移）" % n[1]) if lang == "zh" else ("timestamps are %s local time, no offset" % n[2])
    if style == "off":
        n = ZONES[zk]
        return ("时间戳为%s当地时间，带 UTC 偏移" % n[1]) if lang == "zh" else ("timestamps are %s local time with a UTC offset" % n[2])
    return "时间戳为 UTC" if lang == "zh" else "timestamps are UTC"


def fmt_variants(l):
    """Accepted spellings of a local datetime (full date + time to the second)."""
    d, t = l.strftime("%Y-%m-%d"), l.strftime("%H:%M:%S")
    return sorted({"%s %s" % (d, t), "%sT%s" % (d, t), "%s %s" % (d.replace("-", "/"), t),
                   "%d月%d日 %s" % (l.month, l.day, t), "%d 月 %d 日 %s" % (l.month, l.day, t)})


# scenario: (lang, server log path, device log path, service, key, decoy, filler templates, zh/en context)
SC = {
    "wind": ("zh", "scada/wind-farm.log", "scada/turbine-hmi.log", "wtg-scada", "GRID_FAULT", "GRID_WARN",
             ["INFO WTG-{a:02d} output {b}kW", "INFO WTG-{a:02d} yaw adjust {c}deg", "WARN WTG-{a:02d} vibration {c}mm/s"], "风场的 SCADA 日志"),
    "cold": ("zh", "cold/coldroom.log", "cold/door-panel.log", "coldroom-ctl", "DOOR_OPEN_ALARM", "DOOR_AJAR",
             ["INFO room-{a:02d} temp {c}.{a}C", "INFO room-{a:02d} compressor duty {b}pct", "WARN room-{a:02d} defrost overdue {b}min"], "冷库监控日志"),
    "gate": ("zh", "gates/station-a.log", "gates/gate-panel.log", "gate-ctl", "GATE_JAM", "GATE_SLOW",
             ["INFO gate-{a:02d} passed count={b}", "INFO gate-{a:02d} card reader ok", "WARN gate-{a:02d} sensor dirty level={c}"], "地铁闸机日志"),
    "belt": ("zh", "sorter/line3.log", "sorter/plc-local.log", "sorter-plc", "BELT_STOP", "BELT_SLOW",
             ["INFO lane-{a:02d} parcels={b}", "INFO lane-{a:02d} scan ok barcode=SF{b}{c}", "WARN lane-{a:02d} misread retry={c}"], "快递分拣线日志"),
    "farm": ("zh", "farm/irrigation.log", "farm/field-box.log", "irrigation-hub", "VALVE_STUCK", "VALVE_SLOW",
             ["INFO zone-{a:02d} soil moisture {b}pct", "INFO zone-{a:02d} pump flow {c}L/min", "WARN zone-{a:02d} pressure low {b}kPa"], "灌溉系统日志"),
    "dome": ("en", "observatory/dome.log", "observatory/dome-local.log", "dome-ctl", "SHUTTER_FAULT", "SHUTTER_WARN",
             ["INFO tracking target=HD{b} err={c}arcsec", "INFO dome azimuth {b}deg", "WARN seeing {c}.{a} arcsec"], "the telescope dome log"),
    "game": ("en", "game/match-server.log", "game/region-agent.log", "match-srv", "MATCH_ABORT", "MATCH_RETRY",
             ["INFO lobby-{a:02d} players={b}", "INFO match m{b}{c} started", "WARN lobby-{a:02d} ping p95={b}ms"], "the match server log"),
    "ferry": ("en", "port/ferry-ops.log", "port/berth-desk.log", "ferry-ops", "DEPARTURE_HOLD", "DEPARTURE_DELAY",
              ["INFO berth-{a:02d} loaded vehicles={b}", "INFO berth-{a:02d} gangway retracted", "WARN berth-{a:02d} wind gust {c}kn"], "the ferry operations log"),
    "lab": ("en", "lab/centrifuge.log", "lab/bench-panel.log", "cfg-ctl", "IMBALANCE_TRIP", "IMBALANCE_WARN",
            ["INFO rotor-{a:02d} rpm={b}00", "INFO rotor-{a:02d} temp {c}C", "WARN rotor-{a:02d} vibration {c} g"], "the centrifuge controller log"),
    "cdn": ("en", "cdn/edge.log", "cdn/pop-agent.log", "edge-gw", "ORIGIN_FAILOVER", "ORIGIN_SLOW",
            ["INFO pop-{a:02d} hit ratio {b}pct", "INFO pop-{a:02d} bandwidth {b}Mbps", "WARN pop-{a:02d} cert expires in {c}d"], "the edge gateway log"),
}


def filler(rng, tpl, svc):
    return "%s " % svc + rng.choice(tpl).format(a=rng.randint(1, 12), b=rng.randint(10, 99), c=rng.randint(1, 9))


def line(rng, s, dt, style, lz, kind="fill", **kw):
    lang, _, _, svc, key, decoy, tpl, _ = SC[s]
    if kind == "key":
        body = "%s ERROR %s %s" % (svc, key, kw.get("extra", "unit=%02d" % rng.randint(1, 12)))
    elif kind == "decoy":
        body = "%s WARN %s %s" % (svc, decoy, kw.get("extra", "unit=%02d" % rng.randint(1, 12)))
    else:
        body = filler(rng, tpl, svc)
    return "%s %s" % (stamp(dt, style, lz), body)


def timeline(rng, n, anchor_i, anchor, lo=20, hi=60):
    """n UTC datetimes, strictly increasing, with index anchor_i exactly at anchor."""
    ts = [None] * n
    ts[anchor_i] = anchor
    for i in range(anchor_i - 1, -1, -1):
        ts[i] = ts[i + 1] - timedelta(seconds=rng.randint(lo, hi))
    for i in range(anchor_i + 1, n):
        ts[i] = ts[i - 1] + timedelta(seconds=rng.randint(lo, hi))
    return ts


def header(s, style, lz, lang, zname=None):
    ctx = SC[s][7]
    b = basis(style, lz, lang)
    return ("# %s；%s\n" % (ctx, b)) if lang == "zh" else ("# %s; %s\n" % (ctx, b))


def build_first(rng, r):
    """Log with the first KEY at utc instant r['utc']; decoys and later KEYs around it."""
    s, style, lz = r[2], r[3], r[4]
    T = utc_dt(r[6])
    n = rng.randint(170, 210)
    ti = rng.randint(100, 125)
    ts = timeline(rng, n, ti, T)
    keys_after = {ti + rng.randint(15, 25), ti + rng.randint(40, 60)}
    decoys = {ti - rng.randint(30, 45), ti - rng.randint(5, 12)}
    out = []
    for i, dt in enumerate(ts):
        k = "key" if (i == ti or i in keys_after) else ("decoy" if i in decoys else "fill")
        out.append(line(rng, s, dt, style, lz, k))
    return ts[0], out


def local_dt(s, zk):
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(ZONES[zk][0])).astimezone(UTC)


def build_count(rng, r):
    """Many KEYs over ~9 h; r['n'] of them fall in the local window, the window read as UTC gives another count."""
    s, style, lz, zk = r[2], r[3], r[4], r[5]
    w1 = local_dt(r[6][0], zk)
    w2 = w1 + timedelta(hours=r[6][1])
    first = w1 - timedelta(hours=2, minutes=rng.randint(0, 20))
    n = 420
    ts = timeline(rng, n, 0, first, 40, 70)
    inside = [i for i, d in enumerate(ts) if w1 + timedelta(minutes=6) <= d <= w2 - timedelta(minutes=6)]
    outside = [i for i, d in enumerate(ts) if d < w1 - timedelta(minutes=6) or d > w2 + timedelta(minutes=6)]
    # indices whose UTC clock (same date) would fall in the naive window: wrong-answer bait
    shift = w1.astimezone(ZoneInfo(ZONES[zk][0])).replace(tzinfo=UTC) - w1
    bait = [i for i in outside if w1 + shift <= ts[i] <= w2 + shift]
    pick_in = set(rng.sample(inside, r[7]))
    pick_out = set(rng.sample(bait, min(len(bait), 4))) | set(rng.sample(outside, 4))
    dec = set(rng.sample([i for i in range(n) if i not in pick_in | pick_out], 6))
    out = [line(rng, s, d, style, lz, "key" if i in pick_in | pick_out else ("decoy" if i in dec else "fill")) for i, d in enumerate(ts)]
    naive = sum(1 for i in pick_in | pick_out if w1 + shift <= ts[i] <= w2 + shift)
    assert naive != r[7], r[0]
    return ts[0], out, w1, w2


def build_join(rng, r):
    """Server log in UTC with many KEY ids + a device log in local clock with one KEY; returns both texts and the id."""
    s, sstyle, zk = r[2], r[3], r[5]
    T = utc_dt(r[6])
    bait = T + timedelta(minutes=off_min(T, zk))  # the device clock read as UTC
    secs = set(rng.sample(range(-9 * 3600, 9 * 3600), 330))
    times = sorted({T + timedelta(seconds=x) for x in secs} | {T, bait})
    keyset = set(rng.sample([i for i, d in enumerate(times) if d not in (T, bait) and abs((d - T).total_seconds()) > 120 and abs((d - bait).total_seconds()) > 120], 9))
    ids = rng.sample(range(1000, 9999), 12)
    srv, target_id, bait_id = [], None, None
    for i, d in enumerate(times):
        if d == T or d == bait or i in keyset:
            ev = "EV-%d" % ids.pop()
            if d == T:
                target_id = ev
            elif d == bait:
                bait_id = ev
            srv.append(line(rng, s, d, sstyle, "bj", "key", extra="id=%s" % ev))
        else:
            srv.append(line(rng, s, d, sstyle, "bj"))
    dts = timeline(rng, 170, 90, T, 15, 40)
    dkeys = {5, 160}
    dev = []
    for i, d in enumerate(dts):
        k = "key" if i == 90 else "decoy" if i in (40, 130) else "fill"
        dev.append(line(rng, s, d, "loc", zk, k))
    return srv, dev, target_id, bait_id, times[0]


# (cid, kind, scenario, log stamp style, log zone, asked zone, utc instant / window, extras)
ROWS = [
    ("log-8400", "first", "wind", "z", "bj", "bj", "2026-09-14 17:41:07", "full"),
    ("log-8401", "first", "wind", "sys", "bj", "tk", "2026-03-05 06:12:44", "time"),
    ("log-8402", "first", "cold", "z", "bj", "sg", "2026-08-02 20:05:33", "full"),
    ("log-8403", "first", "cold", "off", "tk", "bj", "2026-11-10 03:20:48", "time"),
    ("log-8404", "first", "gate", "sp", "bj", "bj", "2026-10-08 16:08:21", "full"),
    ("log-8405", "first", "gate", "sp", "bj", "ld", "2026-06-18 11:47:09", "time"),
    ("log-8406", "first", "belt", "sys", "bj", "sg", "2026-12-30 18:22:05", "full"),
    ("log-8407", "first", "belt", "z", "bj", "in", "2026-05-14 21:15:50", "full"),
    ("log-8408", "first", "farm", "off", "sg", "ny", "2026-04-09 02:50:12", "full"),
    ("log-8409", "first", "farm", "sp", "bj", "tk", "2026-02-11 13:09:30", "time"),
    ("log-8410", "first", "dome", "z", "bj", "bj", "2026-01-22 18:36:41", "full"),
    ("log-8411", "first", "game", "sp", "bj", "sy", "2026-09-30 15:20:18", "full"),
    ("log-8412", "first", "ferry", "z", "bj", "se", "2026-03-27 20:44:03", "full"),
    ("log-8413", "first", "lab", "off", "ny", "bj", "2026-10-19 12:10:55", "time"),
    # count: window (asked-zone local start, hours), n inside
    ("log-8414", "count", "cdn", "z", "bj", "bj", ("2026-09-14 22:00", 4), 5),
    ("log-8415", "count", "cdn", "sp", "bj", "tk", ("2026-05-03 08:00", 3), 4),
    ("log-8416", "count", "game", "z", "bj", "sg", ("2026-08-21 23:00", 4), 6),
    ("log-8417", "count", "game", "off", "ld", "bj", ("2026-07-09 20:30", 3), 5),
    ("log-8418", "count", "ferry", "z", "bj", "ld", ("2026-10-14 00:00", 5), 7),
    ("log-8419", "count", "dome", "sp", "bj", "ny", ("2026-02-17 19:00", 4), 5),
    ("log-8420", "count", "lab", "z", "bj", "in", ("2026-06-02 06:00", 4), 6),
    ("log-8421", "count", "dome", "z", "bj", "db", ("2026-03-12 22:30", 4), 8),
    # join: server log style, device-log zone, utc instant of the incident
    ("log-8422", "join", "wind", "z", "bj", "tk", "2026-09-14 16:33:20", None),
    ("log-8423", "join", "cold", "sp", "bj", "sg", "2026-11-03 18:12:40", None),
    ("log-8424", "join", "gate", "z", "bj", "ld", "2026-08-12 09:27:15", None),
    ("log-8425", "join", "belt", "sp", "bj", "bj", "2026-12-05 17:55:30", None),
    ("log-8426", "join", "farm", "z", "bj", "in", "2026-05-28 20:40:10", None),
    ("log-8427", "join", "lab", "z", "bj", "ny", "2026-04-22 02:18:44", None),
    ("log-8428", "join", "cdn", "sp", "bj", "la", "2026-10-05 05:09:51", None),
    ("log-8429", "join", "ferry", "sys", "bj", "sy", "2026-10-17 12:30:05", None),
]


def zn(zk, lang):
    return ZONES[zk][1] + "时间" if lang == "zh" else ZONES[zk][2] + " time"


def hm(dt):
    return dt.strftime("%Y-%m-%d %H:%M")


def prompt_first(r, i, lang):
    cid, _, s, style, lz, zk, utc, fmt = r
    _, srv, _, _, key, _, _, ctx = SC[s]
    z = zn(zk, lang)
    note = ""
    if style == "sys":
        note = "日志里的时间是 UTC，年份 2026。" if lang == "zh" else " The log times are UTC, year 2026."
    if lang == "zh":
        tail = "格式 YYYY-MM-DD HH:MM:SS。" if fmt == "full" else "只要几点几分几秒，格式 HH:MM:SS。"
        t = [
            "看一下 %s（%s），%s 第一次出现是%s几点？%s%s" % (srv, ctx, key, z, tail, note),
            "同事在%s，想知道%s 里第一次 %s 发生在%s什么时候。日志在 %s。%s%s" % (ZONES[zk][1], ctx, key, z, srv, tail, note),
            "帮我查下 %s，第一条 %s 按%s算是什么时刻？%s%s" % (srv, key, z, tail, note),
        ]
    else:
        tail = "Give it as YYYY-MM-DD HH:MM:SS." if fmt == "full" else "Just the clock time, HH:MM:SS."
        t = [
            "In %s (%s), when does the first %s appear in %s? %s%s" % (srv, ctx, key, z, tail, note),
            "Someone in %s needs to know when the first %s shows up in %s, in their own time. The file is %s. %s%s" % (ZONES[zk][2], key, ctx, srv, tail, note),
            "Check %s for the first %s and tell me what time that was in %s. %s%s" % (srv, key, z, tail, note),
        ]
    return t[i % 3]


def prompt_count(r, i, lang):
    cid, _, s, style, lz, zk, (w, hrs), n = r
    _, srv, _, _, key, _, _, ctx = SC[s]
    w1 = datetime.strptime(w, "%Y-%m-%d %H:%M")
    w2 = w1 + timedelta(hours=hrs)
    z = zn(zk, lang)
    note = ""
    if style == "sys":
        note = "日志时间是 UTC。" if lang == "zh" else " Log times are UTC."
    if lang == "zh":
        t = ["%s从 %s 到 %s（含起不含止），%s 里 %s 一共出现了几次？%s" % (z, hm(w1), hm(w2), srv, key, note)]
    else:
        t = [
            "How many %s events does %s record between %s and %s %s (start inclusive, end exclusive)?%s" % (key, srv, hm(w1), hm(w2), z, note),
            "Between %s and %s %s, how many times did %s show up in %s?%s" % (hm(w1), hm(w2), z, key, srv, note),
        ]
    return t[i % len(t)]


def prompt_join(r, i, lang, dev):
    cid, _, s, style, lz, zk, utc, _ = r
    _, srv, dv, _, key, _, _, ctx = SC[s]
    if lang == "zh":
        t = ["%s现场的设备日志 %s 里记了一次 %s，服务端 %s 里对应的是同一时刻那条，它的事件 id 是什么？" % (ZONES[zk][1], dv, key, srv),
             "%s 是%s当地的设备日志，里面 %s 那条在服务端日志 %s 里是哪个 id？" % (dv, ZONES[zk][1], key, srv)]
    else:
        t = ["The %s site's device log %s recorded a %s locally. Which event id in the server log %s is that same moment?" % (ZONES[zk][2], dv, key, srv),
             "%s comes from the %s site's own device, and it logs one %s. What is the matching event id in %s?" % (dv, ZONES[zk][2], key, srv)]
    return t[i % len(t)]


# shared by every verify.py: parse the stamp of a log line back into an aware UTC datetime
PV = '''
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
        m = re.match(r"(\\w{3}) +(\\d+) (\\d\\d:\\d\\d:\\d\\d)", l)
        return datetime.strptime("2026 %s %s %s" % (MON.index(m.group(1)) + 1, m.group(2), m.group(3)), "%Y %m %d %H:%M:%S").replace(tzinfo=UTC)
    if style == "loc":
        return datetime.strptime(l[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(tz)).astimezone(UTC)
    return datetime.fromisoformat(l[:25]).astimezone(UTC)


case = json.load(open("case.json"))
for _p, _t in case["files"].items():  # the clock basis is declared on the first line of each log
    if _p.endswith(".log"):
        assert _t.startswith("# ")
'''


def head(s, style, lz, lang):
    h = header(s, style, lz, lang)
    if style == "sys":
        h = h.rstrip("\n") + ("，年份 2026\n" if lang == "zh" else ", year 2026\n")
    return h


def readme(s, lang, extra=""):
    ctx = SC[s][7]
    return ("# %s\n\n日志每行以时间戳开头。%s\n" % (ctx, extra)) if lang == "zh" else ("# %s\n\nEvery log line starts with a timestamp. %s\n" % (ctx[0].upper() + ctx[1:], extra))


def expected_first(r, rng):
    cid, _, s, style, lz, zk, utc, fmt = r
    T = utc_dt(utc)
    L = loc(T, zk)
    naive = stamp(T, style, lz)
    if fmt == "full":
        any_ = fmt_variants(L)
    else:
        any_ = [L.strftime("%H:%M:%S")]
    assert not any(naive.endswith(a) or a in naive for a in any_), cid
    if fmt == "time":
        assert L.date() == loc(T, lz).date() or style != "off", cid
    return L, any_, naive


def expected_label(L, zk, lang):
    return "%s %s" % (L.strftime("%Y-%m-%d %H:%M:%S"), ZONES[zk][1] if lang == "zh" else ZONES[zk][2])


def vfirst(path, style, lz, tz, key, fmt):
    return PV + '''
l = next(x for x in case["files"][%r].splitlines() if %r in x and not x.startswith("#"))
L = parse(l, %r, %r).astimezone(ZoneInfo(%r))
d, t = L.strftime("%%Y-%%m-%%d"), L.strftime("%%H:%%M:%%S")
if %r == "full":
    out = {"%%s %%s" %% (d, t), "%%sT%%s" %% (d, t), "%%s %%s" %% (d.replace("-", "/"), t),
           "%%d月%%d日 %%s" %% (L.month, L.day, t), "%%d 月 %%d 日 %%s" %% (L.month, L.day, t)}
else:
    out = {t}
print(json.dumps({"expected_contains_any": sorted(out)}))
''' % (path, key, style, ZONES[lz][0], tz, fmt)


def notes_first(r, L, naive, lang, srv, key, hasdate):
    cid, _, s, style, lz, zk, utc, fmt = r
    off = off_str(utc_dt(utc), zk)
    return '''
## Traps
- TR-TZ: log stamps are %s (%s); the question asks %s time (UTC%s on that date). Reporting the log clock as is ("%s") is the decoy.%s
- TR-DECOY: %s also appears in WARN form earlier, and %s appears again later; only the first %s line counts.

## Reference solution
1. search_text for "%s" in %s: the first hit is the ERROR line stamped %s.
2. Convert to %s time (UTC%s): %s.
Final answer, one sentence: the first %s is %s. Criteria: any accepted spelling of the converted time (%s); search_text used; at most one read_file.

## Why the answer is unique
Exactly one first %s line exists, its stamp has a defined offset, and the target zone's offset on that date is fixed.
''' % (basis(style, lz, "en"), style, ZONES[zk][2], off, naive, " The conversion crosses midnight." if hasdate else "",
       SC[r[2]][5], key, key, key, srv, naive, ZONES[zk][2], off, expected_label(L, zk, "en"), key, expected_label(L, zk, "en"),
       "full date and time" if r[7] == "full" else "clock time", key)


def count_units(key, lang):
    if lang == "zh":
        return ["次", "条", "起"], ["", " "]
    return ["times", "events", "occurrences", "instances", "entries", "lines", key], [" "]


def count_any(n, key, lang):
    us, seps = count_units(key, lang)
    return sorted({"%d%s%s" % (n, sp, u) for u in us for sp in seps})


def vcount(path, style, lz, tz, key, win, hours, lang, n, sha):
    us, seps = count_units(key, lang)
    return PV + '''
import hashlib
from datetime import timedelta
assert hashlib.sha256(case["files"][%r].encode()).hexdigest() == %r
w1 = datetime.strptime(%r, "%%Y-%%m-%%d %%H:%%M").replace(tzinfo=ZoneInfo(%r)).astimezone(UTC)
w2 = w1 + timedelta(hours=%d)
ts = [parse(x, %r, %r) for x in case["files"][%r].splitlines() if %r in x and not x.startswith("#")]
n = sum(1 for d in ts if w1 <= d < w2)
print(json.dumps({"expected_number": n}) if %r == "en" else json.dumps({"expected_contains_any": sorted({"%%d%%s%%s" %% (n, sp, u) for u in %r for sp in %r})}))
''' % (path, sha, win, tz, hours, style, ZONES[lz][0], path, key, lang, us, seps)


def notes_count(r, n, lang, w1, w2):
    cid, _, s, style, lz, zk, (w, hrs), _ = r
    key, srv = SC[s][4], SC[s][1]
    return '''
## Traps
- TR-TZ: the window is given in %s time, the log in %s. Counting %s lines whose log clock falls between the same clock numbers gives a different (wrong) count.
- TR-DECOY: %s lines are a different, similar event type and are not counted.

## Reference solution
1. Convert the window to the log clock: %s to %s UTC.
2. search_text for "%s" in %s, then count the hits stamped inside that UTC range: %d.
Final answer, one sentence: %d %s events in the window. Criteria: the count %d (%s); search_text used; at most one read_file.

## Why the answer is unique
Window start is inclusive and end exclusive; every counted line sits at least 6 minutes inside a boundary, so the count is %d.
''' % (ZONES[zk][2], basis(style, lz, "en"), key, SC[s][5], w1.strftime("%Y-%m-%d %H:%M"), w2.strftime("%Y-%m-%d %H:%M"),
       key, srv, n, n, key, n, "number with a unit word", n)


def vjoin(spath, dpath, style, key, dtz, dstyle="loc"):
    return PV + '''
dev = [x for x in case["files"][%r].splitlines() if %r in x and not x.startswith("#")]
assert len(dev) == 1
T = parse(dev[0], "loc", %r)
hit = [x for x in case["files"][%r].splitlines() if %r in x and not x.startswith("#") and parse(x, %r, "UTC") == T]
assert len(hit) == 1
print(json.dumps({"expected_contains_any": [re.search(r"id=(EV-\\d+)", hit[0]).group(1)]}))
''' % (dpath, key, dtz, spath, key, style)


FAMS = {}
for idx, r in enumerate(ROWS):
    cid, kind, s, style, lz, zk = r[:6]
    lang, srv, dv, svc, key, decoy, tpl, ctx = SC[s]
    rng = random.Random(84000 + idx)
    FAMS[s] = FAMS.get(s, 0) + 1
    fam = "fam-log-b10d-tz%s-%02d" % (s, FAMS[s])
    exp = {"required_tools": ["search_text"], "max_output_chars": 600}
    if kind == "first":
        t0, lines = build_first(rng, r)
        L, any_, naive = expected_first(r, rng)
        cross = L.date() != utc_dt(r[6]).date()
        files = {srv: head(s, style, lz, lang) + "\n".join(lines) + "\n",
                 "README.md": readme(s, lang, "日志一律按文件头说明的时钟记录。" if lang == "zh" else "Logs use the clock stated in the file header.")}
        exp["output_contains_any"] = any_
        prompt = prompt_first(r, idx, lang)
        verify = vfirst(srv, style, lz, zk and ZONES[zk][0], key, r[7])
        notes = notes_first(r, L, naive, lang, srv, key, cross)
        decoys = {"TR-TZ": naive, "TR-DECOY": decoy}
        ref, ttype, traps = 2, "locate_error", ["TR-TZ", "TR-DECOY"]
    elif kind == "count":
        t0, lines, w1, w2 = build_count(rng, r)
        n = r[7]
        files = {srv: head(s, style, lz, lang) + "\n".join(lines) + "\n",
                 "README.md": readme(s, lang, "日志一律按文件头说明的时钟记录。" if lang == "zh" else "Logs use the clock stated in the file header.")}
        if lang == "en":  # teacher writes "6." / "5 times." / "**6**" -- match the number itself
            exp["output_contains"] = [str(n)]
            exp["output_contains_token"] = True
        else:
            exp["output_contains_any"] = count_any(n, key, lang)
        prompt = prompt_count(r, idx, lang)
        verify = vcount(srv, style, lz, ZONES[zk][0], key, r[6][0], r[6][1], lang, n,
                        __import__("hashlib").sha256(files[srv].encode()).hexdigest())
        notes = notes_count(r, n, lang, w1, w2)
        decoys = {"TR-TZ": "naive-clock count", "TR-DECOY": decoy}
        ref, ttype, traps = 3, "count_events", ["TR-TZ", "TR-DECOY"]
        cross = w1.astimezone(ZoneInfo(ZONES[zk][0])).date() != w2.astimezone(ZoneInfo(ZONES[zk][0])).date() or w1.date() != w2.date()
    else:
        continue  # join: next block
    write_case(
        cid, desc="%s (time-zone conversion, %s)" % ({"first": "Report the first KEY event of a log in another time zone", "count": "Count KEY events inside a window given in another time zone"}[kind].replace("KEY", key), "crosses midnight" if cross else "same day"),
        task_type=ttype, family=fam, level="L2", ref_calls=ref, traps=traps, decoys=decoys, axes=["OBS"],
        case_expect=MAXREAD, files=files,
        turns=[{"prompt": prompt, "expect": exp}], verify=verify, notes=notes,
    )


for idx, r in enumerate(ROWS):
    cid, kind, s, style, lz, zk = r[:6]
    if kind != "join":
        continue
    lang, srv, dv, svc, key, decoy, tpl, ctx = SC[s]
    rng = random.Random(84000 + idx)
    FAMS[s] = FAMS.get(s, 0) + 1
    srv_lines, dev_lines, tid, bid, t0 = build_join(rng, r)
    T = utc_dt(r[6])
    dev_clock = stamp(T, "loc", zk)
    cross = loc(T, zk).date() != T.date()
    z = ZONES[zk]
    files = {
        srv: head(s, style, "bj", lang) + "\n".join(srv_lines) + "\n",
        dv: head(s, "loc", zk, lang) + "\n".join(dev_lines) + "\n",
        "README.md": readme(s, lang, ("%s 是服务端日志，%s 是现场设备日志，两边各用自己的时钟。" if lang == "zh" else "%s is the server log and %s the on-site device log; each keeps its own clock.") % (srv, dv)),
    }
    notes = '''
## Traps
- TR-TZ: the device log is in %s local time (no offset); the server log is UTC. Searching the server log for the device clock ("%s") lands on %s, a different incident.
- TR-DECOY: the server log has about ten %s events with different ids; only one sits at the converted instant.

## Reference solution
1. search_text "%s" in %s: one hit stamped %s (%s local).
2. Convert to UTC (%s%s): %s.
3. search_text "%s" in %s and find the line stamped at that instant: id %s.
Final answer, one sentence: the matching event is %s. Criteria: the id; search_text used; at most one read_file.

## Why the answer is unique
The converted instant matches exactly one server line to the second; the bait id %s sits at the device clock read as UTC.
''' % (z[2], dev_clock, bid, key, key, dv, dev_clock, z[2], "UTC", off_str(T, zk), stamp(T, "z"), key, srv, tid, tid, bid)
    write_case(
        cid, desc="Match a local-clock device log entry to the UTC server log event at the same instant (%s)" % ("crosses midnight" if cross else "same day"),
        task_type="time_window", family="fam-log-b10d-tz%s-%02d" % (s, FAMS[s]), level="L2", ref_calls=4,
        traps=["TR-TZ", "TR-MULTISRC"], decoys={"TR-TZ": bid, "TR-MULTISRC": "other EV ids"}, axes=["OBS", "CHN"],
        case_expect=MAXREAD, files=files,
        turns=[{"prompt": prompt_join(r, idx, lang, dv),
                "expect": {"output_contains_any": [tid], "required_tools": ["search_text"], "max_output_chars": 600}}],
        verify=vjoin(srv, dv, style, key, ZONES[zk][0]), notes=notes,
    )
