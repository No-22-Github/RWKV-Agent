# DISTILL-CANARY-fa1c3b1b : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '11a43422e553cebe56d3b7a07592d9a40f0c76bf0521090174e3349b94c7ff2c'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['gloves', 'aprons']}, {'expected_contains': ['gloves', 'aprons']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
