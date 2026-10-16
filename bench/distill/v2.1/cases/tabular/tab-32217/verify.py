# DISTILL-CANARY-b2cc4570 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b962fb4a2e3bbd3e8a18c2b992b6735968602a4ebd13ebc83f660134cb38f639', "fixture changed"
import re
def solve(files):
    d = json.loads(files["菜谱/recipes.json"])["recipes"]
    a = [r for r in d if "鸡蛋" in r["ingredients"]]
    b = [r for r in d if any("鸡蛋" in x for x in r["ingredients"])]
    return {"turns": [{"number": len(a), "items": []}, {"number": sum(r["kcal"] for r in a), "items": []}], "decoys": {"TR-DECOY": len(b)}}

ans = solve(case["files"])
def forms(s):
    """Spellings of one number string: plain, thousands-grouped, trailing zeros trimmed."""
    s = str(s)
    out = []

    def add(x):
        if x not in out:
            out.append(x)

    def group(x):
        w, _, f = x.partition(".")
        return format(int(w), ",") + ("." + f if f else "")
    add(s)
    add(group(s))
    if "." in s:
        t = s.rstrip("0").rstrip(".")
        add(t)
        add(group(t))
    return out
out = []
for t in ans["turns"]:
    for f in forms(t["number"]):
        if f not in out:
            out.append(f)
print(json.dumps({"expected_contains_any": out}))
