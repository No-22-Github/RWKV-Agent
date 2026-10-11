# DISTILL-CANARY-e6305412 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '413aea843806d3a359cc220b32b005fcd9d799319fc54a5b14e2eac1e04af8a1'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['开门前', '投影仪']}, {'expected_contains': ['开门前', '投影仪']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
