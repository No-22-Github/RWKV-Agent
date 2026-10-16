# DISTILL-CANARY-81ef15fe : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f84a5edd1244d55aa250ecc828ec79f6190f95f5ca2b8af6ed939d62571bf12', "fixture changed"
import re
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

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
