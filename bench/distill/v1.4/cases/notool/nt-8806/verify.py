# DISTILL-CANARY-f022312f : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '3133883f253a0c21de3d38db12d6eb7ad4b61fd055b4f2790c7f54291e07b0bf'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['Cedar', 'lunch', 'ID']}, {'expected_contains': ['Cedar', 'lunch', 'ID']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
