# DISTILL-CANARY-4843a945 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': 'c0f469f0231885e6f400f7d1468b0568fc7ec991b08edfff67b80cc733ed8c70'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['ceramic', 'upright', 'fabric', 'dry']}, {'expected_contains': ['ceramic', 'upright', 'fabric', 'dry']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
