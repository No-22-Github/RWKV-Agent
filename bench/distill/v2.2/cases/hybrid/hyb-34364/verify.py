# DISTILL-CANARY-941d5153 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
def compute():
    import math
    v = [1284, 967, 1503, 1121, 876, 1390, 1042, 1218]
    m = sum(v) / len(v)
    return [round(math.sqrt(sum((x - m) ** 2 for x in v) / len(v)), 2)]

GIVEN = ["1284", "1218"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
