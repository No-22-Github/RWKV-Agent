# DISTILL-CANARY-d24ae071 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '637488259ec40d61f0ed0a983f74570c499a64295a554b80d21309b1ea432082'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['Mira', 'captions', 'Soren', 'sound']}, {'expected_contains': ['Mira', 'captions', 'Soren', 'sound']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
