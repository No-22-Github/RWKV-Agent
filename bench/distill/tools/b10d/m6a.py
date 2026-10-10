"""M6 (v1.4 §3.6) b10d: mixed date formats (tab-8400..8439).

A date column mixes four writings; data_query has no range filter or date
normalisation, so the path is group_by date -> pick groups in range -> calculator.
Answers are recomputed independently in every verify.py.
"""
import csv as _csv
import io as _io
import random
from common import revised
write_case = revised({"tab-%d" % n: "S5：去掉 required data_query（表里日期混用三四种写法，data_query 只做等值筛选、没法归一日期，老师整读后按日期归并手算才是对的路径）；read_file 上限 1→2（README 说明日期写法，先读 README 再读表是正常路径）；计数题词表补「N 个 / N 条」；终答上限 500→600。" for n in range(8400, 8440)})

MAXREAD = {"max_calls": {"read_file": 2}}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONFULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Source text shared by the generator and every verify.py.
PARSE_SRC = '''
import re

MON = %r

def parse(s):
    """-> (month, day) of a date cell; dmy cells are day-month-year."""
    m = re.match(r"2026/(\\d\\d)/(\\d\\d)$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"(\\d\\d)-(\\d\\d)-2026$", s)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.match(r"([A-Z][a-z][a-z]) (\\d+), 2026$", s)
    if m:
        return MON.index(m.group(1)) + 1, int(m.group(2))
    m = re.match(r"2026-(\\d\\d)-(\\d\\d)T08:00:00Z$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    raise AssertionError(s)

def comma(s):
    return "{:,}".format(int(s))

def forms(n, zh, unit, kind):
    """-> (mode, list) of accepted writings of the number n."""
    s = str(n)
    if kind == "count":
        if zh:
            return "any", sorted({"%%d%%s%%s" %% (n, sp, u) for u in (unit, "个", "条") for sp in (" ", "")})
        return "token", [s]
    base = sorted({s, comma(s)})
    if zh:
        return "any", sorted({b + sp + unit for b in base for sp in (" ", "")})
    return "any", base
''' % (MON,)
exec(PARSE_SRC)


def cell(fmt, m, d):
    return {"slash": "2026/%02d/%02d" % (m, d), "dmy": "%02d-%02d-2026" % (d, m),
            "mon": "%s %d, 2026" % (MON[m - 1], d), "iso": "2026-%02d-%02dT08:00:00Z" % (m, d)}[fmt]


def csvtext(header, rows):
    buf = _io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


class Collide(Exception):
    pass


DOMAINS = {}
_FAMN = {}


def D(slug, **kw):
    DOMAINS[slug] = kw


def build(n, slug, kind, month, win0, a, b, cat=None, obscure=False, fmts=("slash", "dmy", "mon", "iso"), nrows=80):
    """kind: count | sum | catcount | catsum. Window is win0..win0+8; range a..b."""
    d = DOMAINS[slug]
    zh = d["zh"]
    cid = "tab-%d" % n
    hdr = d["alt"] if obscure else d["hdr"]
    seed = 84000 + n
    rng = random.Random(seed)
    rows = []
    for i in range(nrows):
        day = rng.randint(win0, win0 + 8)
        f = rng.choice(fmts)
        rows.append(["%s%05d" % (d["kp"], d["k0"] + i), cell(f, month, day), rng.choice(d["cats"]), rng.randint(*d["amt"])])
    rng.shuffle(rows)
    # keep the trap alive: some dmy rows in range with day != month
    assert any(r[1].endswith("-2026") and a <= parse(r[1])[1] <= b and parse(r[1])[1] != month for r in rows) or "dmy" not in fmts
    sumk = kind in ("sum", "catsum")
    catk = kind in ("catcount", "catsum")
    pick = [r for r in rows if a <= parse(r[1])[1] <= b and parse(r[1])[0] == month and (not catk or r[2] == cat)]
    ans = sum(r[3] for r in pick) if sumk else len(pick)
    # decoy: dmy cells read as month-day
    dec = [r for r in rows if _mdy(r[1], month, a, b) and (not catk or r[2] == cat)]
    decv = sum(r[3] for r in dec) if sumk else len(dec)
    assert decv != ans and len({r[1] for r in rows}) <= 40 and len(rows) >= 60
    assert (ans >= 100) if sumk else (ans >= 10), (cid, kind, ans)
    if str(ans) in {str(r[3]) for r in rows}:
        raise Collide
    unit = d["au"] if sumk else d["cu"]
    mode, lst = forms(ans, zh, unit, "sum" if sumk else "count")
    expect = {"output_contains": lst, "output_contains_token": True} if mode == "token" else {"output_contains_any": lst}
    expect["max_output_chars"] = 600
    rtxt = ("%d 月 %d 日到 %d 日（含）" % (month, a, b)) if zh else ("%s %d to %s %d, inclusive" % (MONFULL[month - 1], a, MONFULL[month - 1], b))
    prompt = d["p"][kind].format(rng=rtxt, cat=cat, path=d["path"])
    files = {d["path"]: csvtext(hdr, rows), "README.md": d["readme"].format(m=month, mon=MON[month - 1], mm="%02d" % month) +
             (("\n列名说明：" if zh else "\nColumn guide: ") + ("；" if zh else "; ").join("%s=%s" % (x, y) for x, y in zip(hdr, d["gloss"])) + "\n" if obscure else "")}
    cfg = dict(path=d["path"], hdr=hdr, month=month, a=a, b=b, kind=kind, cat=cat, zh=zh, unit=unit)
    verify = '''
import csv
import io
import json

case = json.load(open("case.json"))
CFG = %r
%s
rows = list(csv.DictReader(io.StringIO(case["files"][CFG["path"]])))
assert "README.md" in case["files"] and len(rows) >= 60
hd, hc, ha = CFG["hdr"][1], CFG["hdr"][2], CFG["hdr"][3]
assert len({r[hd] for r in rows}) <= 40
kind = CFG["kind"]
pick = [r for r in rows if CFG["a"] <= parse(r[hd])[1] <= CFG["b"] and parse(r[hd])[0] == CFG["month"] and (kind in ("count", "sum") or r[hc] == CFG["cat"])]
v = sum(int(r[ha]) for r in pick) if kind in ("sum", "catsum") else len(pick)
mode, lst = forms(v, CFG["zh"], CFG["unit"], "sum" if kind in ("sum", "catsum") else "count")
if mode == "token":
    print(json.dumps({"expected_number": float(lst[0])}))
else:
    print(json.dumps({"expected_contains_any": lst}, ensure_ascii=False))
''' % (cfg, PARSE_SRC)
    key = (slug, kind in ("count", "sum"))
    _FAMN[key] = _FAMN.get(key, 0) + 1
    fam = "fam-tab-b10d-md%s%s-mixdates-%02d" % (slug, "a" if key[1] else "b", _FAMN[key])
    answ = str(ans)
    notes = _notes(d, zh, kind, hdr, month, a, b, cat, answ, decv, unit, obscure, pick)
    write_case(
        cid,
        desc="%s in a %s export whose date column mixes up to four writings (day-month-year included), over a date range" % ({"count": "Count rows", "sum": "Sum amounts", "catcount": "Count rows of one category", "catsum": "Sum amounts of one category"}[kind], d["title"]),
        task_type="filter_count" if not sumk else "aggregate", family=fam, level="L2" if obscure else "L1", ref_calls=4,
        traps=["TR-DATEFMT"] + (["TR-HEADER"] if obscure else []), decoys=dict({"TR-DATEFMT": str(decv)}, **({"TR-HEADER": d["hdr"][1]} if obscure else {})), axes=["OBS"],
        case_expect=MAXREAD, files=files,
        turns=[{"prompt": prompt, "expect": expect}], verify=verify, notes=notes)


def _mdy(s, month, a, b):
    """True if the row lands in the range when dmy cells are misread as month-day."""
    import re
    m = re.match(r"(\d\d)-(\d\d)-2026$", s)
    if m:
        mo, dy = int(m.group(1)), int(m.group(2))
    else:
        mo, dy = parse(s)
    return mo == month and a <= dy <= b


def _notes(d, zh, kind, hdr, month, a, b, cat, answ, decv, unit, obscure, pick):
    sumk = kind in ("sum", "catsum")
    catk = kind in ("catcount", "catsum")
    flt = ' filter {"%s":"%s"},' % (hdr[2], cat) if catk else ""
    op = 'operation sum, field %s' % hdr[3] if sumk else "operation count"
    if zh:
        return """
## Traps
- TR-DATEFMT: %s 列混了 2026/%02d/xx、dd-%02d-2026（日-月-年，README 说明）、%s d, 2026、ISO 时间四种写法。把日-月-年读成月-日-年，范围内这类行会被算到别的月份，得到 %s。
%s
## Reference solution
1. data_query：path %s，%s group_by %s，%s，得到各日期写法的分组结果（不超过 40 组）。
2. 按 README 的口径把每组归一到 %d 月几日，挑出 %d 日到 %d 日（含）的 %d 组%s。
3. 用计算器%s，得 %s。
终答 1–2 句：给出 %s %s，并说明日期列写法不统一、日-月-年已按 README 归一后再%s。判据：值判据（写法变体放 any）；read_file 最多 2 次（README + 表）。

## Why the answer is unique
README 规定了短日期的读法，ISO 时间固定为 UTC 08:00、落在同一天，每个日期单元格都能唯一归到 %d 月某日；范围含两端，%s结果唯一。
""" % (hdr[1], month, month, MON[month - 1], decv,
       ("- TR-HEADER: 列名不直观（%s），写错列名会报 field missing，需改正后重查。\n" % "、".join(hdr)) if obscure else "",
       d["path"], flt, hdr[1], op, month, a, b, len(pick) and len({r[1] for r in pick}), ("，并在这些组里" if False else ""),
       "把各组的数值相加核对" if True else "", answ, answ, unit, "计数" if not sumk else "求和", month, "类别用等值过滤，" if catk else "")
    return """
## Traps
- TR-DATEFMT: the %s column mixes 2026/%02d/xx, dd-%02d-2026 (day-month-year per the README), %s d, 2026 and ISO timestamps. Reading dd-mm as mm-dd moves those rows out of the range and gives %s.
%s
## Reference solution
1. data_query: path %s,%s group_by %s, %s; at most 40 groups come back.
2. Normalise every group to a day of month %d using the README; keep days %d to %d inclusive (%d distinct cell values in range).
3. Add them up with the calculator: %s.
Final answer, 1-2 sentences: the result is %s %s (as the question asks), noting the date column mixes formats and the dd-mm-yyyy cells were read as day-month-year per the README. Criteria: value (spellings in any), data_query used, at most one read_file.

## Why the answer is unique
The README fixes how the short dates read and ISO timestamps are UTC 08:00 on the same day, so each cell maps to exactly one day of month %d; both range ends are inclusive%s.
""" % (hdr[1], month, month, MON[month - 1], decv,
       ("- TR-HEADER: the column names are not obvious (%s); a wrong name returns a field-missing error and must be corrected and retried.\n" % ", ".join(hdr)) if obscure else "",
       d["path"], flt, hdr[1], op, month, a, b, len({r[1] for r in pick}), answ, answ, unit, month,
       "; the category filter is an exact match" if catk else "")


# ------------------------------------------------------------------ domains (zh)
ZHREAD = "{src}\n日期列来自三个系统，写法不统一：{a}写 2026/{mm}/02；{b}的短日期是「日-月-年」，07-{mm}-2026 表示 2026 年 {m} 月 7 日；{c}写 {mon} 11, 2026 或 ISO 时间（UTC 08:00，即北京时间当天下午）。\n"
ENREAD = "{src}\nThe date column comes from three systems and is not uniform: {a} writes 2026/{mm}/02; {b} writes short dates as day-month-year, so 07-{mm}-2026 is 7 {mon} 2026; {c} writes {mon} 11, 2026 or an ISO timestamp (UTC 08:00, same calendar day).\n"


def _r(tmpl, **kw):
    return tmpl.replace("{src}", kw["src"]).replace("{a}", kw["a"]).replace("{b}", kw["b"]).replace("{c}", kw["c"])


D("hua", zh=True, title="florist orders", path="订单/花店订单.csv", kp="HD-", k0=21000,
  hdr=["订单号", "下单日期", "品类", "金额"], alt=["订单号", "单据日期(登记)", "类目", "实收"],
  gloss=["订单编号", "下单日期，来源系统不同写法不同", "商品类目", "实收金额，元"],
  cats=["鲜花", "永生花", "绿植", "花器"], amt=(48, 520), cu="单", au="元",
  readme=_r(ZHREAD, src="# 柳巷花坊 订单流水\n\n一行一单。", a="门店收银", b="小程序", c="第三方外卖平台"),
  p={"count": "柳巷花坊 {rng}一共收了多少单？订单在 {path}。",
     "sum": "{rng}柳巷花坊的订单实收一共多少元？数据在 {path}。",
     "catcount": "柳巷花坊 {rng}「{cat}」这个品类收了几单？{path} 里有流水。",
     "catsum": "帮我算一下柳巷花坊 {rng}「{cat}」的订单实收合计多少元，表格是 {path}。"})
D("minsu", zh=True, title="guesthouse bookings", path="入住/登记表.csv", kp="BK", k0=7000,
  hdr=["预订号", "入住日期", "房型", "房费"], alt=["预订号", "ci_date", "房型", "房费_元"],
  gloss=["预订编号", "入住日期，写法因渠道而异", "房型", "房费，元"],
  cats=["大床房", "双床房", "亲子房", "榻榻米房"], amt=(180, 880), cu="间", au="元",
  readme=_r(ZHREAD, src="# 竹溪里民宿 入住登记\n\n一行一间次。", a="前台登记", b="民宿管家系统", c="线上旅行平台"),
  p={"count": "竹溪里民宿 {rng}一共有多少间次入住？登记表是 {path}。",
     "sum": "竹溪里民宿 {rng}的房费收入合计多少元？看 {path}。",
     "catcount": "{rng}竹溪里的「{cat}」被住了几间次？登记在 {path}。",
     "catsum": "竹溪里民宿 {rng}「{cat}」的房费一共多少元？数据在 {path}。"})
D("yizhan", zh=True, title="parcel station outbound log", path="驿站/出库登记.csv", kp="YZ", k0=50000,
  hdr=["运单号", "出库日期", "包裹类型", "重量克"], alt=["运单号", "出库日期(登记)", "类型", "重量(g)"],
  gloss=["运单号", "出库日期，三套系统写法不同", "包裹类型", "重量，克"],
  cats=["文件", "服饰", "数码", "食品"], amt=(120, 1900), cu="件", au="克",
  readme=_r(ZHREAD, src="# 桂花街驿站 出库登记\n\n一行一件。", a="驿站手持机", b="快递公司系统", c="电商平台回传"),
  p={"count": "桂花街驿站 {rng}一共出库了多少件？登记表在 {path}。",
     "sum": "桂花街驿站 {rng}出库包裹的总重量是多少克？数据在 {path}。",
     "catcount": "{rng}桂花街驿站出库的「{cat}」有多少件？见 {path}。",
     "catsum": "桂花街驿站 {rng}出库的「{cat}」一共多重（克）？登记在 {path}。"})
D("print", zh=True, title="print shop jobs", path="接单/打印任务.csv", kp="PJ-", k0=3300,
  hdr=["任务号", "接单日期", "纸张", "页数"], alt=["任务号", "收件日", "纸张", "页数"],
  gloss=["任务编号", "接单日期，三个入口写法不同", "纸张规格", "打印页数"],
  cats=["A4", "A3", "名片卡", "相纸"], amt=(20, 400), cu="单", au="页",
  readme=_r(ZHREAD, src="# 墨点图文 打印任务\n\n一行一个任务。", a="店内电脑", b="扫码自助机", c="网络下单"),
  p={"count": "墨点图文 {rng}一共接了多少个打印任务？任务表是 {path}。",
     "sum": "墨点图文 {rng}一共要打多少页？数据看 {path}。",
     "catcount": "{rng}墨点图文接的「{cat}」任务有几个？表在 {path}。",
     "catsum": "墨点图文 {rng}「{cat}」类的任务一共多少页？看 {path}。"})


# ------------------------------------------------------------------ domains (en)
D("bike", zh=False, title="bike rental", path="rentals/checkouts.csv", kp="RN-", k0=40100,
  hdr=["rental_id", "checkout_date", "bike_type", "fee_cents"], alt=["rental_id", "out_dt", "model", "fee_c"],
  gloss=["rental id", "checkout date, written differently by each system", "bike type", "fee in cents"],
  cats=["road", "e-bike", "tandem", "cargo"], amt=(900, 6400), cu="rentals", au="",
  readme=_r(ENREAD, src="# Harbourline Bike Hire - checkouts\n\nOne row per rental.", a="the kiosk tablets", b="the depot system", c="the web shop"),
  p={"count": "How many rentals did Harbourline Bike Hire check out from {rng}? The log is {path}.",
     "sum": "What is the total rental fee, in cents, for Harbourline Bike Hire checkouts from {rng}? Data is in {path}.",
     "catcount": "How many {cat} bikes did Harbourline check out from {rng}? See {path}.",
     "catsum": "Add up the fees (in cents) for Harbourline's {cat} rentals from {rng}. The checkouts are in {path}."})
D("coffee", zh=False, title="coffee roaster wholesale shipments", path="wholesale/shipments.csv", kp="SH", k0=2600,
  hdr=["shipment", "ship_date", "grade", "kg"], alt=["shipment", "ship_dt", "grd", "wt_kg"],
  gloss=["shipment id", "ship date, mixed formats", "bean grade", "weight in kg"],
  cats=["washed", "natural", "honey", "decaf"], amt=(12, 95), cu="shipments", au="kg",
  readme=_r(ENREAD, src="# Copperfield Roasters - wholesale shipments\n\nOne row per shipment.", a="the warehouse scanner", b="the freight broker's feed", c="the online wholesale portal"),
  p={"count": "How many wholesale shipments did Copperfield Roasters send out from {rng}? The list is {path}.",
     "sum": "How many kilograms did Copperfield Roasters ship in total from {rng}? Look at {path}.",
     "catcount": "From {rng}, how many {cat}-grade shipments left Copperfield? Records are in {path}.",
     "catsum": "What is the total weight in kg of Copperfield's {cat} shipments from {rng}? Data: {path}."})
D("solar", zh=False, title="solar installs", path="jobs/installs.csv", kp="INS-", k0=900,
  hdr=["job", "install_date", "roof", "panels"], alt=["job", "dt_done", "surface", "n_pnl"],
  gloss=["job id", "installation date, mixed formats", "roof type", "panel count"],
  cats=["tile", "metal", "flat", "shingle"], amt=(6, 34), cu="installs", au="",
  readme=_r(ENREAD, src="# Brightside Solar - completed installs\n\nOne row per finished install.", a="the field app", b="the dispatch office", c="the customer portal"),
  p={"count": "How many installs did Brightside Solar complete from {rng}? Jobs are listed in {path}.",
     "sum": "Brightside Solar: how many panels were installed from {rng}? Check {path}.",
     "catcount": "How many {cat}-roof installs did Brightside finish from {rng}? The data is {path}.",
     "catsum": "How many panels went onto {cat} roofs from {rng}? Brightside's installs are in {path}."})
D("brew", zh=False, title="brewery keg deliveries", path="deliveries/kegs.csv", kp="KG", k0=7100,
  hdr=["delivery", "delivered_on", "beer", "litres"], alt=["delivery", "dlv", "sku", "l"],
  gloss=["delivery id", "delivery date, mixed formats", "beer style", "volume in litres"],
  cats=["pale", "stout", "lager", "saison"], amt=(30, 200), cu="deliveries", au="litres",
  readme=_r(ENREAD, src="# Stonebridge Brewing - keg deliveries\n\nOne row per delivery.", a="the driver handhelds", b="the distributor's EDI export", c="the pub ordering site"),
  p={"count": "How many keg deliveries did Stonebridge Brewing make from {rng}? The log is {path}.",
     "sum": "What is the total volume in litres that Stonebridge delivered from {rng}? Data in {path}.",
     "catcount": "From {rng}, how many {cat} deliveries did Stonebridge make? See {path}.",
     "catsum": "How many litres of {cat} did Stonebridge deliver from {rng}? The file is {path}."})
D("theatre", zh=False, title="community theatre ticket sales", path="box-office/sales.csv", kp="TX", k0=15000,
  hdr=["sale_id", "sale_date", "seat_zone", "price_eur"], alt=["sale_id", "txn_dt", "zone", "eur"],
  gloss=["sale id", "sale date, mixed formats", "seat zone", "price in euros"],
  cats=["stalls", "circle", "balcony", "box"], amt=(14, 62), cu="sales", au="",
  readme=_r(ENREAD, src="# Lantern Players - box office sales\n\nOne row per ticket sold.", a="the box-office till", b="the ticketing agent's export", c="the website checkout"),
  p={"count": "How many tickets did the Lantern Players sell from {rng}? Sales are in {path}.",
     "sum": "How much ticket revenue in euros did the Lantern Players take from {rng}? See {path}.",
     "catcount": "How many {cat} tickets did the Lantern Players sell from {rng}? Data: {path}.",
     "catsum": "What is the euro total for {cat} tickets the Lantern Players sold from {rng}? Look in {path}."})
D("boat", zh=False, title="boat charter bookings", path="charters/bookings.csv", kp="CH-", k0=610,
  hdr=["booking", "sail_date", "vessel", "fare_usd"], alt=["booking", "dep", "hull", "usd"],
  gloss=["booking id", "departure date, mixed formats", "vessel class", "fare in dollars"],
  cats=["ketch", "catamaran", "sloop", "trawler"], amt=(180, 1450), cu="bookings", au="",
  readme=_r(ENREAD, src="# Tern Island Charters - bookings\n\nOne row per booked day trip.", a="the dock office", b="the agency feed", c="the booking site"),
  p={"count": "How many charter trips did Tern Island sail from {rng}? Bookings are in {path}.",
     "sum": "What is the total fare in dollars for Tern Island trips from {rng}? See {path}.",
     "catcount": "How many {cat} trips did Tern Island sail from {rng}? Data is in {path}.",
     "catsum": "Tern Island: total fares in dollars for {cat} trips from {rng}? The bookings file is {path}."})


# ------------------------------------------------------------------ cases
if __name__ == "__main__":
    order = ["hua", "bike", "minsu", "coffee", "yizhan", "solar", "print", "brew", "theatre", "boat"]
    kinds = ["count", "catsum", "sum", "catcount"]
    FM = [("slash", "dmy", "mon", "iso"), ("slash", "dmy", "mon", "iso"), ("dmy", "mon", "iso"), ("slash", "dmy", "iso"), ("slash", "dmy", "mon")]
    idx = 0
    for k in range(4):
        for j, slug in enumerate(order):
            kind = kinds[(k + j) % 4]
            n = 8400 + idx
            month = [3, 4, 5, 6, 7, 8, 9, 10, 11][(idx * 2 + 1) % 9]
            win0 = 1 + idx % 4
            a = win0 + idx % 2
            b = a + (4 if kind.startswith('cat') else 2) + idx % 3
            cat = DOMAINS[slug]["cats"][idx % 4]
            nr = (200 if kind.startswith('cat') else 70) + (idx * 7) % 41
            while True:
                try:
                    build(n, slug, kind, month, win0, a, b, cat=cat if kind.startswith("cat") else None,
                          obscure=(idx % 3 == 0), fmts=FM[idx % 5], nrows=nr)
                    break
                except Collide:
                    nr += 1
            idx += 1
    print("cases", idx)
