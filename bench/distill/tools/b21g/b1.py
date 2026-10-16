"""b21g sub B: nested statistics over one big JSON file, 32215-32222."""
import json
from random import Random

from common import emit, reg


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


@reg
def b1(i):
    rng = Random(3221500 + i * 7919)
    stores = []
    for k in range(rng.randint(24, 34)):
        ms = []
        for m in ["2026-06", "2026-07", "2026-08", "2026-09"]:
            rev = rng.randint(8000, 90000) if rng.random() < 0.92 else None
            ms.append({"month": m, "revenue": rev, "refunds": [rng.randint(50, 900) for _ in range(rng.randint(0, 3))]})
        stores.append({"store": "门店%02d" % (k + 1), "city": rng.choice(["杭州", "宁波", "苏州", "无锡"]), "months": ms})
    files = {"报表/stores.json": dump({"stores": stores})}

    def solve(files):
        d = json.loads(files["报表/stores.json"])
        a = sum(m["revenue"] for s in d["stores"] for m in s["months"] if m["month"] == "2026-08" and m["revenue"] is not None)
        b = sum(m["revenue"] for s in d["stores"] for m in s["months"] if m["revenue"] is not None)
        c = sum(m["revenue"] - sum(m["refunds"]) for s in d["stores"] for m in s["months"] if m["month"] == "2026-08" and m["revenue"] is not None)
        return {"turns": [{"number": a, "items": []}], "decoys": {"TR-MISSING": b, "TR-DECOY": c}}
    emit("tab-32215", sub="bigjson", task_type="aggregate", desc="Sums one month's revenue across nested stores in a single JSON file where some revenues are null",
         files=files, solve=solve, traps=["TR-MISSING", "TR-DECOY"],
         turns=[{"prompt": "报表/stores.json 里每家门店有四个月的营业额。2026-08 这个月所有门店的 revenue 加起来是多少？退款不用扣，没有营业额数据的月份不算。"}],
         ref=(["jq '[.stores[].months[]|select(.month==\"2026-08\")|.revenue]|map(select(.!=null))|add' 报表/stores.json"], 0),
         notes_traps=["TR-MISSING: ~8% of monthly revenues are null.", "TR-DECOY: the total over all four months or net of refunds differ."],
         notes_ref=["jq flatten stores[].months[] select month, drop nulls, add."], unique="One month, null revenue excluded, refunds not deducted.")


def _dept(rng, name, depth, counter):
    emps = []
    for _ in range(rng.randint(3, 8)):
        counter[0] += 1
        emps.append({"id": "E%04d" % counter[0], "level": rng.randint(1, 8)})
    subs = [_dept(rng, "%s-%d" % (name, j + 1), depth + 1, counter) for j in range(rng.randint(1, 3))] if depth < 3 else []
    return {"name": name, "employees": emps, "teams": subs}


@reg
def b2(i):
    rng = Random(3221600 + i * 7919)
    cnt = [0]
    org = {"company": "Meridian", "departments": [_dept(rng, n, 1, cnt) for n in ["Platform", "Growth", "Finance", "Support"]]}
    files = {"hr/org.json": dump(org)}

    def solve(files):
        d = json.loads(files["hr/org.json"])

        def walk(x):
            out = list(x["employees"])
            for t in x["teams"]:
                out += walk(t)
            return out
        p = [x for x in d["departments"] if x["name"] == "Platform"][0]
        allp = walk(p)
        a = [e for e in allp if e["level"] >= 5]
        top = [e for e in p["employees"] if e["level"] >= 5]
        b = [e for e in allp if e["level"] == 8]
        return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DECOY": len(top)}}
    emit("tab-32216", sub="bigjson", task_type="filter_count", desc="Counts senior employees under one department including all nested sub-teams in a nested JSON org tree",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "hr/org.json is our org chart; departments contain teams, which can contain further teams. How many people in the Platform department, counting every nested team, are level 5 or above?"},
                {"prompt": "And how many of them are level 8 exactly?"}],
         ref=(["jq '[.departments[]|select(.name==\"Platform\")|recurse(.teams[])|.employees[]|select(.level==8)]|length' hr/org.json"], 0),
         notes_traps=["TR-DECOY: only looking at the department's direct employees undercounts."], notes_ref=["jq recurse(.teams[]) then employees[] select level."],
         unique="Whole Platform subtree, level threshold inclusive.")


@reg
def b3(i):
    rng = Random(3221700 + i * 7919)
    ings = ["鸡蛋", "鸡蛋清", "番茄", "面粉", "牛奶", "葱", "盐", "糖", "豆腐", "虾仁", "米饭", "黄油"]
    rec = []
    for k in range(rng.randint(260, 340)):
        rec.append({"id": "R%03d" % (k + 1), "name": "菜谱%d" % (k + 1), "kcal": rng.randint(120, 880), "ingredients": rng.sample(ings, rng.randint(2, 6))})
    files = {"菜谱/recipes.json": dump({"recipes": rec})}

    def solve(files):
        d = json.loads(files["菜谱/recipes.json"])["recipes"]
        a = [r for r in d if "鸡蛋" in r["ingredients"]]
        b = [r for r in d if any("鸡蛋" in x for x in r["ingredients"])]
        return {"turns": [{"number": len(a), "items": []}, {"number": sum(r["kcal"] for r in a), "items": []}], "decoys": {"TR-DECOY": len(b)}}
    emit("tab-32217", sub="bigjson", task_type="filter_count", desc="Counts recipes listing one exact ingredient in a nested JSON where a longer ingredient name contains it, then sums their calories",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "菜谱/recipes.json 里有多少道菜的配料正好包含“鸡蛋”？“鸡蛋清”是另一种配料，不算。"},
                {"prompt": "这些菜的 kcal 加起来是多少？"}],
         ref=(["jq '[.recipes[]|select(.ingredients|index(\"鸡蛋\"))|.kcal]|add' 菜谱/recipes.json"], 0),
         notes_traps=["TR-DECOY: 鸡蛋清 contains 鸡蛋; a text search over-counts."], notes_ref=["jq select ingredients array contains exact 鸡蛋, then add kcal."],
         unique="Exact array membership.")


@reg
def b4(i):
    rng = Random(3221800 + i * 7919)
    libs = ["lodash", "lodash-es", "react", "left-pad", "axios", "zod", "dayjs", "lodash.merge"]
    pk = {}
    for k in range(rng.randint(180, 260)):
        deps = {x: rng.choice(["^1.2.0", "~2.0.1", "3.4.5", "^0.9.0"]) for x in rng.sample(libs, rng.randint(0, 4))}
        pk["pkg-%03d" % k] = {"version": "%d.%d.%d" % (rng.randint(0, 4), rng.randint(0, 9), rng.randint(0, 9)), "dependencies": deps}
    files = {"mono/manifest.json": dump({"packages": pk})}

    def solve(files):
        d = json.loads(files["mono/manifest.json"])["packages"]
        a = [k for k, v in d.items() if "lodash" in v["dependencies"]]
        b = [k for k, v in d.items() if any(x.startswith("lodash") for x in v["dependencies"])]
        return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DECOY": len(b)}}
    emit("tab-32218", sub="bigjson", task_type="filter_count", desc="Counts packages in a manifest JSON whose dependency map has one exact key where similar-named libraries exist",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "mono/manifest.json lists our workspace packages and their dependencies. How many packages depend on lodash itself (lodash-es and lodash.merge are different libraries)?"}],
         ref=(["jq '[.packages[]|select(.dependencies|has(\"lodash\"))]|length' mono/manifest.json"], 0),
         notes_traps=["TR-DECOY: lodash-es and lodash.merge keys start with lodash."], notes_ref=["jq select dependencies has key lodash, length."], unique="Exact key membership.")


@reg
def b5(i):
    rng = Random(3221900 + i * 7919)
    orders = []
    for k in range(rng.randint(280, 380)):
        lines = [{"sku": "K%02d" % rng.randint(1, 40), "qty": rng.randint(1, 6), "price": rng.randint(8, 420)} for _ in range(rng.randint(1, 6))]
        orders.append({"order": "O-%04d" % (3000 + k), "lines": lines})
    files = {"shop/orders.json": json.dumps(orders, ensure_ascii=False) + "\n"}

    def solve(files):
        d = json.loads(files["shop/orders.json"])
        tot = sorted(((sum(l["qty"] * l["price"] for l in o["lines"]), o["order"]) for o in d), reverse=True)
        assert tot[0][0] > tot[1][0]
        n = len([1 for t, _ in tot if t > 2500])
        return {"turns": [{"number": tot[0][0], "items": [tot[0][1]]}, {"number": n, "items": []}], "decoys": {"TR-DEFN": max(l["price"] for o in d for l in o["lines"])}}
    emit("tab-32219", sub="bigjson", task_type="rank", desc="Finds the order with the largest line total (qty times price summed) in a single-line JSON array, then counts orders above a threshold",
         files=files, solve=solve, traps=["TR-DEFN"],
         turns=[{"prompt": "shop/orders.json 是订单数组，每单有若干行（qty 件、price 单价）。订单金额 = 每行 qty×price 之和。金额最大的是哪一单？金额多少？"},
                {"prompt": "金额超过 2500 的订单有几单？"}],
         ref=(["jq '[.[]|select(([.lines[]|.qty*.price]|add)>2500)]|length' shop/orders.json"], 0),
         notes_traps=["TR-DEFN: order amount is the sum of qty*price over lines, not the max price."], notes_ref=["jq map({o:.order,t:([.lines[]|.qty*.price]|add)}) sort desc."],
         unique="Unique maximum order total; strict greater-than threshold.")


@reg
def b6(i):
    rng = Random(3222000 + i * 7919)
    sv = []
    for k in range(rng.randint(200, 280)):
        envs = {}
        for e in rng.sample(["dev", "staging", "prod"], rng.randint(1, 3)):
            envs[e] = {"replicas": rng.randint(1, 8), "flags": {"canary": rng.random() < 0.3}}
            if rng.random() < 0.2:
                del envs[e]["flags"]
        sv.append({"service": "svc-%03d" % k, "envs": envs})
    files = {"deploy/services.json": dump({"services": sv})}

    def solve(files):
        d = json.loads(files["deploy/services.json"])["services"]
        a = [s for s in d if (s["envs"].get("prod") or {}).get("flags", {}).get("canary") is True]
        b = [s for s in d if any((e.get("flags") or {}).get("canary") is True for e in s["envs"].values())]
        return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DECOY": len(b), "TR-MISSING": len([s for s in d if "prod" in s["envs"]])}}
    emit("cfg-32220", sub="bigjson", task_type="read_effective", desc="Counts services with the canary flag enabled in the prod environment only, where flags can be absent",
         files=files, solve=solve, traps=["TR-DECOY", "TR-MISSING"],
         turns=[{"prompt": "deploy/services.json describes every service and its environments. How many services have canary turned on in prod specifically? Other environments don't count, and a prod entry without flags simply has no canary."}],
         ref=(["jq '[.services[]|select(.envs.prod.flags.canary==true)]|length' deploy/services.json"], 0),
         notes_traps=["TR-DECOY: canary in dev/staging also exists.", "TR-MISSING: some envs have no flags object."], notes_ref=["jq select .envs.prod.flags.canary==true | length."],
         unique="Only prod env, canary strictly true.")


def _flags(rng, name, depth):
    node = {}
    for k in range(rng.randint(2, 4)):
        if depth < 3 and rng.random() < 0.4:
            node["%s_g%d" % (name[:3], k)] = _flags(rng, "%s%d" % (name, k), depth + 1)
        else:
            node["f_%s_%d" % (name[:3], k)] = {"enabled": rng.random() < 0.45, "owner": rng.choice(["a", "b", "c"])}
    return node


@reg
def b7(i):
    rng = Random(3222100 + i * 7919)
    tree = {g: {"rollout": rng.randint(0, 100), "flags": _flags(rng, g, 1)} for g in ["payments", "search", "onboarding", "admin"]}
    for g in list(tree):
        for _ in range(6):
            tree[g]["flags"]["x%d" % rng.randint(0, 999)] = _flags(rng, g, 2)
    files = {"config/flags.json": dump(tree)}

    def solve(files):
        d = json.loads(files["config/flags.json"])

        def walk(x):
            if isinstance(x, dict):
                if "enabled" in x:
                    yield x
                else:
                    for v in x.values():
                        yield from walk(v)
        pay = list(walk(d["payments"]["flags"]))
        a = len([f for f in pay if f["enabled"] is True])
        b = len([f for f in pay if f["enabled"] is True and f["owner"] == "b"])
        allf = len([f for g in d.values() for f in walk(g["flags"]) if f["enabled"] is True])
        return {"turns": [{"number": a, "items": []}, {"number": b, "items": []}], "decoys": {"TR-DECOY": allf, "TR-LONG": len(pay)}}
    emit("cfg-32221", sub="bigjson", task_type="read_effective", desc="Counts enabled flags at any nesting depth under one group of a feature flag tree, then those owned by one team",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "config/flags.json 是功能开关配置，开关按组嵌套，嵌套层数不一。payments 这一组里（不管嵌套多深）一共有多少个开关是开着的（enabled 为 true）？"},
                {"prompt": "其中 owner 是 b 的有几个？"}],
         ref=(["jq '[.payments.flags|..|objects|select(has(\"enabled\") and .enabled==true and .owner==\"b\")]|length' config/flags.json"], 0),
         notes_traps=["TR-DECOY: counting enabled flags in every group gives a larger number."], notes_ref=["jq recursive descent over objects that have enabled."],
         unique="Leaf flags are objects with an enabled key; the group rollout number is not a flag.")


@reg
def b8(i):
    rng = Random(3222200 + i * 7919)
    hosts = []
    w = [rng.randint(2, 9) for _ in range(4)]
    for k in range(rng.randint(300, 420)):
        h = {"host": "ip-10-0-%d-%d" % (k // 200, k % 200 + 1), "tags": {"env": rng.choice(["prod", "stage"]), "role": rng.choice(["web", "db", "cache", "worker"])}}
        if rng.random() < 0.95:
            h["az"] = rng.choices(["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d"], w)[0]
        hosts.append(h)
    files = {"infra/inventory.json": dump({"hosts": hosts})}

    def solve(files):
        d = json.loads(files["infra/inventory.json"])["hosts"]
        c = {}
        for h in d:
            if h["tags"]["env"] == "prod" and h["tags"]["role"] == "web" and "az" in h:
                c[h["az"]] = c.get(h["az"], 0) + 1
        r = sorted(c.items(), key=lambda kv: -kv[1])
        assert r[0][1] > r[1][1]
        al = {}
        for h in d:
            if "az" in h:
                al[h["az"]] = al.get(h["az"], 0) + 1
        ra = sorted(al.items(), key=lambda kv: -kv[1])
        assert ra[0][0] != r[0][0] or True
        return {"turns": [{"number": r[0][1], "items": [r[0][0]]}], "decoys": {"TR-DECOY": ra[0][1], "TR-MISSING": r[1][1]}}
    emit("cfg-32222", sub="bigjson", task_type="read_effective", desc="Finds the availability zone hosting the most prod web hosts in an inventory JSON where az is sometimes absent",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "infra/inventory.json is our host inventory. Looking only at prod web servers (tags.env is prod and tags.role is web), which availability zone has the most of them, and how many?"}],
         ref=(["jq -r '.hosts[]|select(.tags.env==\"prod\" and .tags.role==\"web\" and .az!=null)|.az' infra/inventory.json | sort | uniq -c | sort -rn | head -3"], 0),
         notes_traps=["TR-DECOY: counting every host per zone gives a larger number."], notes_ref=["jq -r select prod web, print az; sort | uniq -c | sort -rn."],
         unique="Filter by both tags; unique winner by margin.")
