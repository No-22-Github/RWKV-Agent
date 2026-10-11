# DISTILL-CANARY-773e1f1a : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '7d30dc9d109c984e291b161fd3db56c64e65662471609a65e72414b208eaf396'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['Amber', 'balcony', 'Violet', 'courtyard']}, {'expected_contains': ['Amber', 'balcony', 'Violet', 'courtyard']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
