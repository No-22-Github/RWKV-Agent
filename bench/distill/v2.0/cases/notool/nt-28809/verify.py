# DISTILL-CANARY-051cfbec : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': 'b16d3b254a77b9cc2eb83af50b5d6fe4bf7faf10ecf67838e7ac7ff4895786cb'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['error', 'file type']}, {'expected_contains': ['error', 'file type']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
