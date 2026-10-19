# DISTILL-CANARY-2fde5f12 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd9660e9a2da22faa56d85e5034219e43ed7dd7827f7c2d1bcdf029fe5bac1245', "fixture changed"
def compute():
    return [1840 / 9200 * 100]

GIVEN = ["9200", "1840"]
PROMPTS = "\n".join(t["prompt"] for t in case["turns"])
assert all(g in PROMPTS for g in GIVEN)
ANS = compute()
assert len(ANS) == len(case["turns"])
for turn, v in zip(case["turns"], ANS):
    assert abs(turn["expect"]["expected_number"] - v) < 1e-9
print(json.dumps({"expected_number": float(ANS[0])}))
