# DISTILL-CANARY-a415133b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd4309da51ac7a1bc9efc8c1e872b21ccdb9f7ee2d1611e8df0f5a6e02e611707', "fixture changed"
import re
def solve(files):
    cl = [json.loads(l) for l in files["报销/claims.jsonl"].splitlines()]
    iv = {l.split(",")[0] for l in files["报销/invoices.csv"].splitlines()[1:]}
    no = [c for c in cl if c["claim"] not in iv]
    t = sum(c["cents"] for c in no)
    ids = sorted(c["claim"] for c in no)
    return {"turns": [{"number": "%d.%02d" % (t // 100, t % 100), "items": ids}], "decoys": {"TR-DECOY": "%d.%02d" % (sum(c["cents"] for c in cl) // 100, sum(c["cents"] for c in cl) % 100)}}

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
