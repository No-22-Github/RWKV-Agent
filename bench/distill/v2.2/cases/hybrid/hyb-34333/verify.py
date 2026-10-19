# DISTILL-CANARY-668b741a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a9fa6b774faea90a3395a037c7d433929d7886f1847381c4b0d4b7bfe6eb25ec', "fixture changed"
def compute():
    import math
    return [math.factorial(10), 2 * math.factorial(9)]

GIVEN = ["10 个", "小李", "小王"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
