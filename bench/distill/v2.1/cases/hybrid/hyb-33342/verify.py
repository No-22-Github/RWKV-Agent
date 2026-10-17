# DISTILL-CANARY-639084f5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '90a51c045676faa39843355b928ec360c8051458a25983e2c4bcbdfc469837f5', "fixture changed"
def compute(files, web):
    import re
    r = [w for w in web if w["url"].endswith("/rates")][0]["content"]
    t = [w for w in web if w["url"].endswith("/taxes")][0]["content"]
    room = int(re.search(r"Deluxe room: \$(\d+)", r).group(1))
    n = int(re.search(r"nights: (\d+)", files["travel/booking.txt"]).group(1))
    base = room * n
    tax = int(re.search(r"Occupancy tax: (\d+)%", t).group(1))
    fee = int(re.search(r"Resort fee: \$(\d+)", t).group(1))
    x = round(base * (1 + tax / 100.0) + fee * n, 2)
    return {}, [[str(base)], list(dict.fromkeys(["%.2f" % x, ("%.2f" % x).rstrip("0").rstrip("."), "{:,.2f}".format(x)]))]

FINAL, ANS = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    assert set(a) <= set(e.get("output_contains", [])) | set(e.get("output_contains_any", [])), a
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}, "answers": ANS}, ensure_ascii=False))
