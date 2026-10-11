# DISTILL-CANARY-649f0c6d : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': 'd34d790403701215397aa85a6a7cad6aec2be7633064270cf26a85133a584545'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['周岚', '校对', '郭越', '排版']}, {'expected_contains': ['周岚', '校对', '郭越', '排版']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
