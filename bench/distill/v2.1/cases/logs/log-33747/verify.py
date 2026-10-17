# DISTILL-CANARY-efb06359 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '545c88f11f7bdd769ebb65ccaf66960ef86cec52358e607266e7b7a83d1e859b', "fixture changed"
def cnt(f,lo,hi): return sum(1 for l in files[f].splitlines() if lo<=l[:19]<hi and ' ERROR ' in l)
a=cnt('edge-us.log','2026-09-14T12:00:00','2026-09-14T13:00:00')
b=cnt('edge-cn.log','2026-09-14T20:00:00','2026-09-14T21:00:00')
answers=[str(a+b), 'edge-us' if a>b else 'edge-cn']
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
