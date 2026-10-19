# DISTILL-CANARY-17b4ec35 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0dba11d2a2ab268c7d1b6ce5b9ae341e0b2ed920e39a4b0ec1a2294aafae259e', "fixture changed"
def compute():
    return [(540 - 480) / 480 * 100]

GIVEN = ["480", "540"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
