# DISTILL-CANARY-d8be5302 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '393f78a7db59bcd633fb4d72a960488e3e9d395a382c100e4333a23b87f74316'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['水杯', '饮水']}, {'expected_contains': ['水杯', '饮水']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
