# DISTILL-CANARY-8f43819a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a5384b3f077a04609f2d674acef7a50474087bb0ed4321d4a06bfd270de40746', "fixture changed"
import re
def solve(files):
    led = {l.split(",")[0] for l in files["finance/ledger.csv"].splitlines()[1:]}
    bank = {json.loads(l)["ref"] for l in files["finance/bank.jsonl"].splitlines()}
    oa = sorted(led - bank)
    return {"turns": [{"number": len(oa), "items": oa}], "decoys": {"TR-DECOY": len(bank - led), "TR-TRUNC": len(led)}}

ans = solve(case["files"])
n = ans["turns"][-1]["number"]
print(json.dumps({"expected_number": float(n) if "." in str(n) else int(n)}))
