"""M6 (v1.4 §3.6) b10d: filter + join over two tables (tab-8440..8489).

data_query has exact-match filters, group_by and sum/avg/min/max/count only,
so every case needs two queries (dimension table -> key set, fact table ->
per-key totals) plus the calculator. Thresholds are answered by grouping and
picking groups. Answers are recomputed independently in each verify.py.
"""
import json as _json
import random
from common import revised
write_case = revised({"tab-%d" % n: "S5：去掉 read_file 上限（连接题要读 README、名册/档案、流水三份文件，三遍老师全部因此判挂）；英文计数题改为 token 只认数字本身（老师写「2.」「3 Ale beers」，词表收不全）；「哪一台/哪个品种」题机台编号或货号也算对；tab-8447 判据单位由「元」改为题面问的「件」。" for n in range(8440, 8490)})

MAXREAD = {"max_calls": {"read_file": 2}}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
CNUM = "零一二三四五六七八九"
ENUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

# Shared by the generator and by every verify.py (kept as source text).
FORMS_SRC = '''
def fmt(v, sc):
    if sc == 1:
        return str(v)
    return ("%.1f" % (v / sc)).rstrip("0").rstrip(".")

def comma(s):
    if "." in s:
        a, b = s.split(".")
        return "{:,}".format(int(a)) + "." + b
    return "{:,}".format(int(s))

def forms(s, zh, unit, isint):
    """-> ("token", [s]) or ("any", [...]) accepted writings of the value s."""
    base = [s] if comma(s) == s else [s, comma(s)]
    if zh:
        out = []
        for b in base:
            out += [b + " " + unit, b + unit]
        if "." in s and len(s) >= 5:
            out += base
        return "any", sorted(set(out))
    if isint and len(s) <= 3:
        return "token", [s]
    return "any", sorted(set(base))

def count_forms(n, zh, cu):
    if zh:
        out = []
        for c in cu.split("|"):
            out += ["%d %s" % (n, c), "%d%s" % (n, c), "%s%s" % ("零一二三四五六七八九"[n], c), "%s %s" % ("零一二三四五六七八九"[n], c)]
        return "any", sorted(set(out))
    return "token", ["%d" % n]
'''
exec(FORMS_SRC)


def csvtext(header, rows):
    return ",".join(header) + "\n" + "".join(",".join(str(c) for c in r) + "\n" for r in rows)


DOMAINS = {}


def D(slug, **kw):
    DOMAINS[slug] = kw


_FAMN = {}


def _fam(slug, tmpl):
    key = (slug, tmpl)
    _FAMN[key] = _FAMN.get(key, 0) + 1
    return "fam-tab-b10d-%s-%s-%02d" % (slug, {"sum": "sumjoin", "value": "pricejoin", "count": "thrcount", "thsum": "thrsum", "top": "topname"}[tmpl], _FAMN[key])


def build(n, slug, tmpl, ai, pi, obscure, prompt):
    """tmpl: sum | count | thsum | value | top"""
    d = DOMAINS[slug]
    zh = d["zh"]
    cid = "tab-%d" % n
    attr = d["attrs"][ai]
    period = d["periods"][pi] if pi is not None else None
    hA = d["altA"] if obscure else d["hA"]
    hB = d["altB"] if obscure else d["hB"]
    sc = d["sc"]
    price = tmpl == "value"
    seed = 84400 + n
    while True:
        rng = random.Random(seed)
        seed += 1000
        sizes = [rng.randint(3, 5) for _ in d["attrs"]]
        sizes[ai] = rng.randint(4, 6)
        nk = sum(sizes)
        nums = sorted(rng.sample(range(100, 990), nk))
        names = rng.sample(d["names"], nk)
        attrs = [a for a, s in zip(d["attrs"], sizes) for _ in range(s)]
        rng.shuffle(attrs)
        keys = ["%s%d" % (d["kp"], x) for x in nums]
        arows = []
        for k, nm, a in zip(keys, names, attrs):
            row = [k, nm, a]
            if price:
                row.append(rng.randint(*d["price"]))
            arows.append(row)
        sel = [r for r in arows if r[2] == attr]
        brows = []
        for r in sel:  # every selected key appears in every period
            for p in d["periods"]:
                brows.append([r[0], p, rng.randint(d["lo"], d["hi"])])
        for _ in range(rng.randint(100, 150)):
            brows.append([rng.choice(keys), rng.choice(d["periods"]), rng.randint(d["lo"], d["hi"])])
        rng.shuffle(brows)
        inper = [b for b in brows if period is None or b[1] == period]
        tot = {r[0]: sum(b[2] for b in inper if b[0] == r[0]) for r in sel}
        if price:
            prc = {r[0]: r[3] for r in sel}
            tot = {k: v * prc[k] for k, v in tot.items()}
        vals = sorted(tot.values(), reverse=True)
        if len(set(vals)) != len(vals):
            continue
        if tmpl in ("count", "thsum"):
            T = vals[1 + (len(vals) > 4)]  # 2nd or 3rd largest: boundary key is included
            hit = [k for k, v in tot.items() if v >= T]
            if not (2 <= len(hit) < len(vals)):
                continue
        if tmpl == "top" and vals[0] - vals[1] < (d["hi"] - d["lo"]):
            continue
        break
    ans_sc = sc
    allsum = sum(b[2] for b in brows)
    if tmpl == "sum" or tmpl == "value":
        ans = sum(tot.values())
        if period is not None:
            dec = sum(b[2] * (prc[b[0]] if price else 1) for b in brows if b[0] in tot)
        else:
            dec = allsum
    elif tmpl == "thsum":
        ans = sum(tot[k] for k in hit)
        dec = sum(v for v in tot.values() if v > T)
    elif tmpl == "count":
        ans = len(hit)
        dec = len([v for v in tot.values() if v > T])
    else:  # top
        top = max(tot, key=lambda k: tot[k])
        ans = [r[1] for r in arows if r[0] == top][0]
        dec = [r[1] for r in sel if r[0] != top][0]
    natp = ("%d 月" % int(period[-2:]) if zh else MONTHS[int(period[-2:]) - 1]) if period else ""
    prompt = prompt.replace("{a}", attr).replace("{p}", natp)
    assert "{" not in prompt.replace("{t}", "") and (period is None or natp in prompt), cid
    assert (tmpl in ("count", "thsum")) == ("{t}" in prompt), cid
    prompt = prompt.replace("{t}", fmt(T, ans_sc if tmpl == "thsum" else sc) if tmpl in ("count", "thsum") else "")
    unit = "件" if prompt.endswith("多少件？") else d["unit"]
    if tmpl == "top":
        expect = {"output_contains_any": [ans, top], "required_tools": ["data_query"], "max_output_chars": 500}
        shown, isint, mode = ans, False, "name"
    else:
        if tmpl == "count":
            mode, lst = count_forms(ans, zh, d["cu"])
            shown = str(ans)
        else:
            shown = fmt(ans, ans_sc)
            mode, lst = forms(shown, zh, unit, ans_sc == 1)
        if mode == "token":
            expect = {"output_contains": lst, "output_contains_token": True}
        else:
            expect = {"output_contains_any": lst}
        expect["required_tools"] = ["data_query"]
        expect["max_output_chars"] = 500
    decs = fmt(dec, ans_sc) if tmpl in ("sum", "value", "thsum") else (str(dec))
    assert str(dec) != str(ans) and fmt(dec, ans_sc) != shown if tmpl != "top" else dec != ans, cid
    ref = ans if tmpl == "top" else shown + (" " + unit if zh else "")
    if tmpl == "count":
        ref = ("%d %s" % (ans, d["cu"].split("|")[0])) if zh else ("%d of them" % ans)
    if "output_contains_any" in expect:
        assert any(x in ref for x in expect["output_contains_any"]), (cid, ref)
    else:
        assert all(x in ref for x in expect["output_contains"]), (cid, ref)
    cfg = dict(tmpl=tmpl, zh=zh, hA=hA, hB=hB, attr=attr, period=period, price=price,
               sc=sc, ans_sc=ans_sc, unit=unit, cu=d["cu"], pathA=d["fa"], pathB=d["fb"],
               T=(T if tmpl in ("count", "thsum") else None))
    files = {d["fa"]: csvtext(hA[:4] if price else hA[:3], arows),
             d["fb"]: csvtext(hB, brows)}
    gl = ""
    if obscure:
        ncA = 4 if price else 3
        gl = ("\n表头说明：" if zh else "\nColumn guide: ") + ("；" if zh else "; ").join("%s=%s" % (h, m) for h, m in zip(hA[:ncA] + hB, d["glA"][:ncA] + d["glB"])) + "\n"
    files["README.md"] = d["readme"] + gl
    import hashlib
    cfg["sha"] = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(files.items())}
    # ---- verify
    verify = '''
import csv
import hashlib
import io
import json

case = json.load(open("case.json"))
CFG = %s
%s
f = case["files"]
assert {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(f.items())} == CFG["sha"]
A = list(csv.DictReader(io.StringIO(f[CFG["pathA"]])))
B = list(csv.DictReader(io.StringIO(f[CFG["pathB"]])))
hA, hB = CFG["hA"], CFG["hB"]
sel = [r for r in A if r[hA[2]] == CFG["attr"]]
assert 3 <= len(sel) <= 6 and len(B) >= 60
sc = CFG["sc"]
tot = {}
for r in sel:
    vs = [int(b[hB[2]]) for b in B if b[hB[0]] == r[hA[0]] and (CFG["period"] is None or b[hB[1]] == CFG["period"])]
    assert vs
    tot[r[hA[0]]] = sum(vs) * (int(r[hA[3]]) if CFG["price"] else 1)
t = CFG["tmpl"]
asc = CFG["ans_sc"]
zh = CFG["zh"]
if t == "top":
    top = max(tot, key=lambda k: tot[k])
    print(json.dumps({"expected_contains_any": [[r[hA[1]] for r in A if r[hA[0]] == top][0], top]}, ensure_ascii=False))
else:
    if t in ("count", "thsum"):
        hit = [v for v in tot.values() if v >= CFG["T"]]
    if t == "count":
        mode, lst = count_forms(len(hit), zh, CFG["cu"])
    else:
        v = sum(hit) if t == "thsum" else sum(tot.values())
        mode, lst = forms(fmt(v, asc), zh, CFG["unit"], asc == 1)
    if mode == "token":
        print(json.dumps({"expected_number": float(lst[0])}))
    else:
        print(json.dumps({"expected_contains_any": lst}, ensure_ascii=False))
''' % (repr(cfg), FORMS_SRC)
    # ---- notes
    pA, pB = d["fa"], d["fb"]
    per = ('，filter {"%s":"%s"}' % (hB[1], period)) if zh and period else (', filter {"%s":"%s"}' % (hB[1], period) if period else "")
    nsel = len(sel)
    steps = {
        "sum": "对 %s 汇总：group_by %s，operation sum，field %s%s；取这 %d 个键的合计相加" % (pB, hB[0], hB[2], per, nsel),
        "value": "对 %s 汇总：group_by %s，operation sum，field %s%s；每个键的合计乘 %s 表里的单价后相加" % (pB, hB[0], hB[2], per, pA),
        "count": "对 %s 汇总：group_by %s，operation sum，field %s%s；与阈值 %s 比较（含等于），数出达标的键" % (pB, hB[0], hB[2], per, fmt(T, sc) if tmpl == "count" else ""),
        "thsum": "对 %s 汇总：group_by %s，operation sum，field %s%s；只把合计不低于 %s（含等于）的键加起来" % (pB, hB[0], hB[2], per, fmt(T, sc) if tmpl == "thsum" else ""),
        "top": "对 %s 汇总：group_by %s，operation sum，field %s%s；比较这 %d 个键的合计，取最大者对应的名称" % (pB, hB[0], hB[2], per, nsel),
    }[tmpl]
    answer_text = ans if tmpl == "top" else (str(ans) if tmpl == "count" else shown)
    notes = '''
## Traps
- TR-MULTISRC: %s 只有 %s、%s、%s，没有「%s」；%s 有「%s」却没有数值。data_query 没有 join，要先用 %s 对「%s」做等值过滤拿到键集合（%d 个），再到 %s 汇总。只看一张表答不出。
- TR-DEFN: %s
- 诱饵值：%s（忽略%s或把不属于该%s的行也算进去）。%s

## Reference solution
1. data_query：path %s，filter {"%s":"%s"}，select %s → %d 个键。
2. data_query：%s。
3. 用计算器核对加总 / 比较，得 %s。
终答 1–2 句：给出结果 %s，并说明是按 %s 里属于「%s」的键、到 %s 汇总得出。判据：值判据（写法变体放 any）；用过 data_query；不限 read_file 次数（README、名册、流水各读一次是正常路径）。

## Why the answer is unique
键集合由 %s 的等值过滤唯一确定（%d 个键，均在 %s 中出现），每个键的数值逐行求和，没有歧义%s。
''' % (pB, hB[0], hB[1], hB[2], hA[2], pA, hA[2], pA, hA[2],
       nsel, pB,
       ("阈值「不少于」含等于，边界键的合计恰好等于阈值；按「大于」算会漏掉它，得 %s。" % decs) if tmpl in ("count", "thsum") else ("单价在 %s 的第 4 列，按数量不乘价会得到数量合计。" % pA if price else "无额外口径坑，口径明确。"),
       decs, "月份条件" if period else "属性条件", d["entw"],
       ("列名不直观（%s），写错会得到空结果或「field missing」报错，需改正后重查。" % "、".join(hA[:3] + hB)) if obscure else "",
       pA, hA[2], attr, hA[0], nsel, steps, answer_text, answer_text, pA, attr, pB, pA, nsel, pB,
       "，表头已在 README 中说明" if obscure else "")
    write_case(
        cid,
        desc="Join %s with %s: filter the dimension table by %s=%s, then %s from the fact table%s" % (pA, pB, hA[2], attr, {"sum": "sum per-key totals", "value": "value quantities at table prices", "count": "count keys at or above a threshold", "thsum": "sum the keys at or above a threshold", "top": "name the key with the largest total"}[tmpl], "; obscure column names" if obscure else ""),
        task_type="join", family=_fam(slug, tmpl),
        level="L2", ref_calls=4,
        traps=["TR-MULTISRC"] + (["TR-DEFN"] if tmpl in ("count", "thsum") else []) ,
        decoys=dict([("TR-MULTISRC", decs)] + ([("TR-DEFN", decs)] if tmpl in ("count", "thsum") else [])),
        axes=["CHN", "OBS"], files=files,
        turns=[{"prompt": prompt, "expect": expect}],
        verify=verify, notes=notes)


# ------------------------------------------------------------------ domains
ZH_PEOPLE = ("陈思远 林雅婷 王子豪 刘欣怡 张浩然 赵梓萱 孙明哲 周佳琪 吴俊杰 郑晓彤 冯立新 蒋雨泽 韩若曦 唐嘉树 许诗涵 曹子墨 邓国梁 彭婉清 魏志刚 苏婧怡 卢晨阳 谢文博 董梦琪 沈博文 叶秋实 钟灵毓 袁思齐 贺天宇").split()
ZH_GOODS_A = ("双头荧光笔 速干中性笔 活页笔记本 A4复印纸 订书机 回形针盒 文件夹 便利贴 记号笔 修正带 直尺 剪刀 胶棒 计算器 台历 打孔机 档案袋 白板擦 笔筒 印台 标签贴 裁纸刀 画板 水彩笔").split()
ZH_GOODS_E = ("红玫瑰 白百合 粉康乃馨 向日葵 蓝绣球 洋桔梗 郁金香 满天星 尤加利 非洲菊 勿忘我 芍药 马蹄莲 薰衣草 雏菊 栀子 紫罗兰 小苍兰 龙胆 蝴蝶兰 水仙 风信子").split()
ZH_SHOPS = ("青松路店 梧桐里店 临江道店 云栖街店 白鹭湾店 南湖苑店 星河城店 听雨轩店 紫荆坊店 落霞桥店 玉兰园店 柳岸里店 枫林湾店 桃源村店 海棠路店 竹影巷店 锦绣坊店 晨曦道店 沁园春店 金桂里店 银杏街店 碧波园店").split()
ZH_COURSES = ("Python入门 数据分析基础 摄影构图 水彩速写 财务报表解读 短视频剪辑 演讲与表达 吉他弹唱 书法楷书 咖啡拉花 电子乐器入门 瑜伽基础 日语N5 英语口语 PPT设计 Excel进阶 理财入门 手机摄影 素描基础 小红书运营 思维导图 时间管理").split()
ZH_HOUSES = ("栖云小筑 听潮居 半山叙 晴川阁 竹里馆 临溪舍 揽月轩 归雁楼 松风院 映雪斋 采薇居 拾光屋 云深处 水云间 观澜阁 墨香舍 南山闲 北窗里 渔舟唱 荷风榭 秋水庐 暖阳房").split()
ZH_MACH = ("海德堡-1 海德堡-2 小森-3 小森-4 罗兰-5 罗兰-6 高宝-7 高宝-8 三菱-9 三菱-10 柯尼卡-11 柯尼卡-12 方正-13 方正-14 北人-15 北人-16 川田-17 川田-18 恒大-19 恒大-20 京瓷-21 京瓷-22").split()
D("express", zh=True, attrs=["东门站", "北城站", "江湾站", "西岸站"], names=ZH_PEOPLE, kp="KD", periods=["2026-03", "2026-04", "2026-05"],
  lo=18, hi=96, price=None, sc=1, unit="件", cu="人|位|名|个", fa="站点/快递员名册.csv", fb="站点/派件记录.csv",
  hA=["工号", "姓名", "站点"], hB=["工号", "月份", "派件数"], altA=["gh", "xm", "zd"], altB=["gh", "ym", "pjs"],
  glA=["工号", "姓名", "所属站点"], glB=["工号", "月份", "当日派件数"], entw="快递员",
  readme="东门、北城、江湾、西岸四个快递站的派件统计。名册一人一行；派件记录按天累计，每行是某位快递员某月内一天的派件数，同一个人一个月里会有很多行。\n")
D("stationery", zh=True, attrs=["书写工具", "纸品", "办公小件"], names=ZH_GOODS_A, kp="WJ", periods=["2026-06", "2026-07", "2026-08"],
  lo=12, hi=120, price=(3, 48), sc=1, unit="元", cu="款|种|个", fa="商品/商品档案.csv", fb="出货/出货流水.csv",
  hA=["货号", "品名", "品类", "单价"], hB=["货号", "月份", "出货量"], altA=["hh", "pm", "pl", "dj"], altB=["hh", "yf", "chl"],
  glA=["货号", "品名", "品类", "单价（元/件）"], glB=["货号", "月份", "单笔出货件数"], entw="货号",
  readme="文具批发部的商品档案和出货流水。单价按件计，单位元；出货流水每行是一笔出货，同一货号一个月内有多笔。\n")
D("flower", zh=True, attrs=["玫瑰类", "百合类", "杂花类", "叶材类"], names=ZH_GOODS_E, kp="HP", periods=["2026-02", "2026-03", "2026-04"],
  lo=20, hi=150, price=(2, 15), sc=1, unit="元", cu="款|种|个", fa="档案/花材品种.csv", fb="出货/出货明细.csv",
  hA=["品种号", "品名", "类别", "单价"], hB=["品种号", "月份", "枝数"], altA=["pzh", "pm", "lb", "dj"], altB=["pzh", "yf", "zs"],
  glA=["品种号", "品名", "类别", "单价（元/枝）"], glB=["品种号", "月份", "单笔出货枝数"], entw="品种",
  readme="花材批发档口的品种档案和出货明细。单价按枝计，单位元；出货明细每行是一笔出货。\n")
D("homestay", zh=True, attrs=["古城区", "湖滨区", "山景区"], names=ZH_HOUSES, kp="FY", periods=["2026-05", "2026-06", "2026-07"],
  lo=1, hi=6, price=None, sc=1, unit="间夜", cu="套|间|个", fa="房源/房源表.csv", fb="订单/入住记录.csv",
  hA=["房源号", "房源名", "片区"], hB=["房源号", "月份", "间夜数"], altA=["fyh", "mc", "pq"], altB=["fyh", "yf", "jy"],
  glA=["房源号", "房源名", "所在片区"], glB=["房源号", "月份", "单笔订单间夜数"], entw="房源",
  readme="民宿平台某运营团队管理的房源和入住订单。入住记录每行是一笔订单，同一房源一个月内会有多笔；间夜数 = 房间数 × 夜数。\n")
D("courses", zh=True, attrs=["技能类", "艺术类", "职场类"], names=ZH_COURSES, kp="KC", periods=["2026-09", "2026-10", "2026-11"],
  lo=1, hi=9, price=None, sc=1, unit="人", cu="门|个", fa="教务/课程目录.csv", fb="教务/报名流水.csv",
  hA=["课程号", "课程名", "类别"], hB=["课程号", "月份", "报名人数"], altA=["kch", "kcm", "lx"], altB=["kch", "yf", "bmrs"],
  glA=["课程号", "课程名", "课程类别"], glB=["课程号", "月份", "单次报名的人数（团报算多人）"], entw="课程",
  readme="成人兴趣培训学校的课程目录和报名流水。报名流水每行是一次报名（可能是团报），同一门课一个月里有多次。\n")
D("press", zh=True, attrs=["一车间", "二车间", "三车间"], names=ZH_MACH, kp="JT", periods=["2026-01", "2026-02", "2026-03"],
  lo=200, hi=1800, price=None, sc=1, unit="张", cu="台|个", fa="设备/机台台账.csv", fb="生产/开机记录.csv",
  hA=["机台号", "机型", "车间"], hB=["机台号", "月份", "印张数"], altA=["jth", "jx", "cj"], altB=["jth", "yf", "yzs"],
  glA=["机台号", "机型", "所在车间"], glB=["机台号", "月份", "单次开机的印张数"], entw="机台",
  readme="一家印刷厂的机台台账和开机记录。开机记录每行是机台的一次开机任务，同一台机器一个月里有很多次。\n")
D("volunteer", zh=True, attrs=["社区组", "助老组", "环保组", "赛事组"], names=ZH_PEOPLE, kp="ZY", periods=["2026-04", "2026-05", "2026-06"],
  lo=1, hi=6, price=None, sc=1, unit="小时", cu="人|位|名|个", fa="名单/志愿者名册.csv", fb="服务/服务记录.csv",
  hA=["编号", "姓名", "小组"], hB=["编号", "月份", "服务时长"], altA=["bh", "xm", "xz"], altB=["bh", "yf", "sc"],
  glA=["志愿者编号", "姓名", "所属小组"], glB=["志愿者编号", "月份", "单次服务时长（小时）"], entw="志愿者",
  readme="某公益协会的志愿者名册和服务记录。服务记录每行是一次出勤，同一位志愿者一个月里可以有多次。\n")
D("grouptrade", zh=True, attrs=["东区", "西区", "南区", "北区"], names=ZH_PEOPLE, kp="TZ", periods=["2026-08", "2026-09", "2026-10"],
  lo=3, hi=40, price=None, sc=1, unit="单", cu="位|人|名|个", fa="团长/团长名单.csv", fb="订单/团购订单.csv",
  hA=["团长号", "团长", "片区"], hB=["团长号", "月份", "订单数"], altA=["tzh", "tz", "pq"], altB=["tzh", "yf", "dds"],
  glA=["团长编号", "团长姓名", "负责片区"], glB=["团长编号", "月份", "单批订单数"], entw="团长",
  readme="社区团购平台的团长名单和订单汇总。订单表每行是团长某月里一批（一次截单）收到的订单数，同一团长一个月里有多批。\n")

EN_PEOPLE = ("Marta Kowalski,Devon Pryce,Ines Okafor,Tomas Lindqvist,Aiko Brennan,Hugo Delacroix,Priya Raman,Callum Reeve,Noor Haddad,Felix Ostrow,"
             "Greta Hallam,Rafael Quintero,Sana Whitlock,Jonas Mbeki,Lena Farrow,Oskar Dunmore,Yara Castellan,Ewan Thackeray,Mina Sorensen,Dario Falk,"
             "Nia Ellsworth,Anders Vail,Tessa Moreno,Idris Calloway,Wren Halvorsen,Kofi Albright").split(",")
EN_BEERS = ("Harbour Pale,Copper Ale,Stonebridge Stout,Fenland Lager,Gorse IPA,Salt Marsh Gose,Old Mill Porter,Highland Amber,Orchard Cider,Heron Wheat,"
            "Tidewater Bitter,Black Quay Dark,Meadow Saison,Lantern Pils,Rookery Red,Kiln Brown,Thistle Gold,Mossgate Helles,Ember Rye,Cobble Blonde,Foxglove Sour,Beacon Session").split(",")
EN_FILMS = ("Night Ferry,The Quiet Orchard,Salt and Iron,Paper Moons,Last Tram to Elm Street,Glass Harbour,A Small Fire,Winter Cartographers,Hollow Crown,Blue Hour,"
            "The Long Thaw,Understudy,Marigold Road,Rain Over Lisbon,Tin Soldiers,Northern Lights Cafe,Borrowed Time,The Lamplighters").split(",")
EN_TALKS = ("Scaling Postgres,Rust for Embedded,Why Tests Rot,Edge Caching 101,Observability on a Budget,Type Systems in Practice,Build Systems Compared,"
            "Rethinking CI,Memory Safety Tales,Zero-Downtime Migrations,Async Without Tears,Queues at Scale,API Versioning,Fuzzing Finds Bugs,Design Docs That Work,"
            "Incident Reviews,Cost-Aware Cloud,Open Source Burnout,WebAssembly Today,Schema Evolution").split(",")
EN_VINES = ("Block A1,Block A2,Block B1,Block B2,Block C1,Block C2,Block D1,Block D2,Block E1,Block E2,Block F1,Block F2,Block G1,Block G2,Block H1,Block H2,Block J1,Block J2,Block K1,Block K2,Block L1,Block L2").split(",")
D("vineyard", zh=False, attrs=["Ridge", "Valley", "Coastal"], names=EN_PEOPLE, kp="PK", periods=["2026-08", "2026-09", "2026-10"],
  lo=40, hi=320, price=None, sc=1, unit="kg", cu="pickers|workers|people", fa="harvest/pickers.csv", fb="harvest/picking_log.csv",
  hA=["picker_id", "name", "vineyard"], hB=["picker_id", "month", "kg"], altA=["pk_id", "nm", "vyd"], altB=["pk_id", "mth", "wt"],
  glA=["picker ID", "picker name", "vineyard they are assigned to"], glB=["picker ID", "month", "kilograms picked in one shift"], entw="picker",
  readme="Seasonal harvest records for a family vineyard. pickers.csv has one row per picker; picking_log.csv has one row per shift, so a picker appears many times in a month.\n")
D("support", zh=False, attrs=["Billing", "Platform", "Mobile", "Integrations"], names=EN_PEOPLE, kp="AG", periods=["2026-03", "2026-04", "2026-05"],
  lo=2, hi=25, price=None, sc=1, unit="tickets", cu="agents|people|reps", fa="support/agents.csv", fb="support/resolved_daily.csv",
  hA=["agent_id", "name", "team"], hB=["agent_id", "month", "resolved"], altA=["ag", "fullname", "grp"], altB=["ag", "mo", "closed_n"],
  glA=["agent ID", "agent name", "support team"], glB=["agent ID", "month", "tickets closed in one day"], entw="agent",
  readme="SaaS support desk. agents.csv lists agents and their team; resolved_daily.csv has one row per agent per working day with the number of tickets closed.\n")
D("cinema", zh=False, attrs=["Drama", "Comedy", "Documentary"], names=EN_FILMS, kp="FM", periods=["2026-06", "2026-07", "2026-08"],
  lo=30, hi=260, price=None, sc=1, unit="tickets", cu="films|titles|movies", fa="programme/films.csv", fb="box_office/sales.csv",
  hA=["film_id", "title", "genre"], hB=["film_id", "month", "tickets"], altA=["fid", "ttl", "gn"], altB=["fid", "mo", "tk"],
  glA=["film ID", "film title", "genre"], glB=["film ID", "month", "tickets sold at one screening"], entw="film",
  readme="Independent cinema programme and box office. sales.csv has one row per screening; a film is shown many times a month.\n")
D("brewery", zh=False, attrs=["Ale", "Lager", "Dark"], names=EN_BEERS, kp="BR", periods=["2026-04", "2026-05", "2026-06"],
  lo=2, hi=40, price=(18, 64), sc=1, unit="GBP", cu="beers|labels|products", fa="catalogue/beers.csv", fb="dispatch/dispatch_log.csv",
  hA=["beer_code", "name", "style", "case_price"], hB=["beer_code", "month", "cases"], altA=["bc", "label", "stl", "cp"], altB=["bc", "mo", "cs"],
  glA=["beer code", "beer name", "style family", "wholesale price per case in GBP"], glB=["beer code", "month", "cases in one dispatch"], entw="beer",
  readme="Craft brewery catalogue and dispatch log. case_price is the wholesale price per case in GBP; dispatch_log.csv has one row per dispatch, so a beer appears many times a month.\n")
D("meetup", zh=False, attrs=["Backend", "Frontend", "Ops"], names=EN_TALKS, kp="TK", periods=["2026-01", "2026-02", "2026-03"],
  lo=8, hi=70, price=None, sc=1, unit="attendees", cu="talks|sessions", fa="talks/talks.csv", fb="talks/checkins.csv",
  hA=["talk_id", "title", "track"], hB=["talk_id", "month", "attendees"], altA=["tid", "subject", "trk"], altB=["tid", "mo", "head_count"],
  glA=["talk ID", "talk title", "track"], glB=["talk ID", "month", "attendees counted at one repeat session"], entw="talk",
  readme="A developer community's talk catalogue and check-in sheet. checkins.csv has one row per session of a talk (talks are repeated across venues), with the head count.\n")
D("fleet", zh=False, attrs=["Northgate", "Riverside", "Docklands"], names=EN_PEOPLE, kp="VH", periods=["2026-02", "2026-03", "2026-04"],
  lo=40, hi=260, price=None, sc=1, unit="km", cu="vehicles|vans|drivers", fa="fleet/vehicles.csv", fb="fleet/trips.csv",
  hA=["vehicle_id", "driver", "depot"], hB=["vehicle_id", "month", "km"], altA=["veh", "drv", "loc"], altB=["veh", "mo", "dist"],
  glA=["vehicle ID", "assigned driver", "home depot"], glB=["vehicle ID", "month", "kilometres of one trip"], entw="vehicle",
  readme="Delivery fleet records. vehicles.csv has one row per van and its depot; trips.csv has one row per trip.\n")


# ------------------------------------------------------------------ cases
# (slug, tmpl, attr index, period index or None, obscure column names, prompt)
CASES = [
    ("express", "sum", 0, 0, False, "{a}的快递员{p}一共派了多少件？名册和派件记录都在站点文件夹里。"),
    ("express", "count", 1, 1, True, "{a}的快递员里，{p}派件总数不少于 {t} 件的有几位？"),
    ("express", "top", 2, 2, False, "{a}的快递员里，{p}派件最多的是谁？"),
    ("express", "thsum", 3, 0, False, "{a}这边，{p}派件总数达到 {t} 件及以上的快递员，他们加起来一共派了多少件？"),
    ("stationery", "value", 0, 0, True, "{p}{a}的出货额一共是多少元？按商品档案里的单价算。"),
    ("stationery", "value", 1, 2, False, "{a}在{p}的出货额是多少元？单价以档案为准。"),
    ("stationery", "count", 2, 1, False, "{a}里，{p}出货量不少于 {t} 件的有几款？"),
    ("stationery", "sum", 1, None, False, "{a}这一类，出货流水里所有记录加起来一共出了多少件？"),
    ("flower", "value", 0, 1, False, "{p}{a}的出货额一共多少元？档案和出货明细在不同文件里。"),
    ("flower", "value", 2, 2, True, "{a}在{p}卖了多少钱？单价以品种档案为准。"),
    ("flower", "top", 1, 0, False, "{p}{a}里哪个品种出货的枝数最多？"),
    ("homestay", "sum", 0, 0, False, "{a}的房源{p}一共住了多少间夜？"),
    ("homestay", "thsum", 1, 1, True, "{a}的房源里，{p}间夜数不少于 {t} 的，合起来一共多少间夜？"),
    ("homestay", "count", 2, 2, False, "{a}的房源中，{p}累计入住不少于 {t} 间夜的有几套？"),
    ("courses", "sum", 0, 1, False, "{a}课程{p}一共有多少人报名？"),
    ("courses", "top", 1, 0, True, "{p}报名人数最多的{a}课程是哪一门？"),
    ("courses", "count", 2, 2, False, "{a}课程里，{p}报名人数不少于 {t} 的有几门？"),
    ("press", "sum", 1, 2, False, "{a}的机台{p}一共印了多少张？"),
    ("press", "thsum", 0, 1, True, "{a}里{p}印张数不少于 {t} 的机台，一共印了多少张？"),
    ("press", "top", 2, 0, False, "{a}里{p}印得最多的是哪一台？"),
    ("volunteer", "sum", 3, 0, True, "{a}的志愿者{p}一共服务了多少小时？"),
    ("volunteer", "count", 0, 1, False, "{a}里{p}服务时长不少于 {t} 小时的志愿者有几位？"),
    ("volunteer", "thsum", 2, 2, False, "{a}的志愿者里，{p}累计服务不少于 {t} 小时的人，服务时长一共是多少小时？"),
    ("grouptrade", "sum", 0, 2, False, "{a}的团长们{p}一共收了多少单？"),
    ("grouptrade", "count", 1, 0, True, "{a}的团长里，{p}单量不少于 {t} 单的有几位？"),
    ("grouptrade", "thsum", 3, 1, False, "{a}这边{p}订单数不少于 {t} 的团长，他们的单量合计是多少？"),
    ("vineyard", "sum", 0, None, False, "How many kilograms did the pickers on the {a} vineyard bring in over the whole season?"),
    ("vineyard", "count", 1, 1, True, "Among the {a} pickers, how many picked at least {t} kg in {p}?"),
    ("vineyard", "top", 2, 2, False, "Who picked the most grapes in {p} among the {a} crew?"),
    ("vineyard", "thsum", 0, 0, False, "Add up the {p} kilograms of every {a} picker who brought in {t} kg or more that month."),
    ("support", "sum", 0, 0, False, "How many tickets did the {a} team close in {p}?"),
    ("support", "count", 1, 1, True, "In {p}, how many {a} agents closed at least {t} tickets?"),
    ("support", "top", 2, 2, False, "Which {a} agent closed the most tickets in {p}?"),
    ("support", "thsum", 3, 0, True, "For {p}, what is the combined ticket count of the {a} agents who closed {t} or more?"),
    ("cinema", "sum", 1, 0, False, "How many tickets did our {a} titles sell in {p}?"),
    ("cinema", "count", 0, 1, True, "How many {a} films sold at least {t} tickets in {p}?"),
    ("cinema", "top", 2, 2, False, "Which {a} title sold the most tickets in {p}?"),
    ("cinema", "thsum", 0, 2, False, "Of the {a} films, those with {t} or more tickets in {p} sold how many tickets altogether?"),
    ("brewery", "value", 0, 0, False, "What was the wholesale value, in GBP, of the {a} beers we dispatched in {p}?"),
    ("brewery", "value", 1, 1, True, "At catalogue case prices, what is the total value in GBP of {p} dispatches of our {a} beers?"),
    ("brewery", "value", 2, 2, False, "How much, in GBP, were the {a} beers we sent out in {p} worth at wholesale?"),
    ("brewery", "count", 0, 1, False, "In {p}, how many of our {a} beers had at least {t} cases dispatched?"),
    ("meetup", "sum", 0, 0, False, "How many people attended {a} talks in {p}?"),
    ("meetup", "count", 1, 1, False, "How many {a} talks drew at least {t} attendees in total in {p}?"),
    ("meetup", "top", 2, 2, True, "Which {a} talk had the biggest total attendance in {p}?"),
    ("meetup", "thsum", 0, 2, False, "Counting only {a} talks with {t} or more attendees in {p}, what is the total attendance?"),
    ("fleet", "sum", 0, 0, False, "How many kilometres did the {a} depot's vans cover in {p}?"),
    ("fleet", "count", 1, 1, False, "How many vans out of the {a} depot drove {t} km or more in {p}?"),
    ("fleet", "top", 2, 2, True, "Which driver at the {a} depot covered the most distance in {p}?"),
    ("fleet", "thsum", 0, 1, False, "Total up the kilometres in {p} for {a} depot vans that did {t} km or more."),
]
assert len(CASES) == 50

if __name__ == "__main__":
    for i, (slug, tmpl, ai, pi, obs, prompt) in enumerate(CASES):
        build(8440 + i, slug, tmpl, ai, pi, obs, prompt)
    print("m6c: %d cases, zh %d, obscure %d" % (len(CASES), sum(DOMAINS[c[0]]["zh"] for c in CASES), sum(c[4] for c in CASES)))
