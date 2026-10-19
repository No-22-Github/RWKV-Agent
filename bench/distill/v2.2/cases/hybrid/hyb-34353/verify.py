# DISTILL-CANARY-30ba7966 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a9fa6b774faea90a3395a037c7d433929d7886f1847381c4b0d4b7bfe6eb25ec', "fixture changed"
def compute():
    return [round(150000 * 1.0385 ** 7, 2), round(150000 * 1.0385 ** 10, 2)]

GIVEN = ["15 万", "3.85%", "7 年"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
