# DISTILL-CANARY-54cc4f4a : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 56
def solve(files):
    best = None
    for p, t in files.items():
        if p.startswith("报价/"):
            for r in t.splitlines()[1:]:
                f = r.split(",")
                if f[0] == "A-100" and (best is None or int(f[1]) < best[1]):
                    best = (p[3:-4], int(f[1]))
    s, price = best
    final = dict(files)
    final["采购/默认供应商.csv"] = "".join(("A-100," + s if r.startswith("A-100,") else r) + chr(10) for r in files["采购/默认供应商.csv"].splitlines())
    for p, t in files.items():
        if p.startswith("采购/下单/"):
            rows = []
            for r in t.splitlines():
                f = r.split(",")
                rows.append(",".join(["A-100", s, str(price), f[3]]) if f[0] == "A-100" else r)
            final[p] = "".join(r + chr(10) for r in rows)
    return [{"all": [s, str(price)]}, None], final, {"s": s, "price": price}
files = case["files"]
answers, final, info = solve(files)
for turn, ans in zip(case["turns"], answers):
    if ans is None:
        continue
    if "any" in ans:
        assert turn["expect"]["output_contains_any"] == ans["any"], (turn["expect"], ans)
    else:
        assert turn["expect"]["output_contains"] == ans["all"], (turn["expect"], ans)
out = {p: t for p, t in final.items() if files.get(p) != t}
print(json.dumps({"files": out}, ensure_ascii=False))
