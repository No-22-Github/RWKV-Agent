# DISTILL-CANARY-415d0ee2 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 201
def solve(files):
    tot, rows = {}, {}
    for p, t in sorted(files.items()):
        if p.startswith("订单/"):
            for r in t.splitlines()[1:]:
                c, v = r.split(",")
                tot[c] = tot.get(c, 0) + int(v)
                rows.setdefault(c, []).append(r)
    order = sorted(tot, key=lambda c: -tot[c])
    assert tot[order[0]] > tot[order[1]]
    final = dict(files)
    for c in tot:
        final["汇总/%s.csv" % c] = "品类,金额" + chr(10) + "".join(r + chr(10) for r in rows[c])
    final["汇总/结论.txt"] = "最大品类：" + order[0] + chr(10)
    return [{"all": [order[0]]}, None], final, {"top": order[0], "cats": sorted(tot)}
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
