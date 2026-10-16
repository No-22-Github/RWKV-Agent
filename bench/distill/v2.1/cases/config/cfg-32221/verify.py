# DISTILL-CANARY-c4caf7d1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a78396e57e2c66cf9c3c01206ed7bd6ce418b1d1b045edb6f9439d7e4799adfe', "fixture changed"
import re
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

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
