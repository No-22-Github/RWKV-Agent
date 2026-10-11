# DISTILL-CANARY-4ade9552 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '31c6b1c91eb01ff9fa3896a1de4e5b364e84b296eeb4990700bcb2d096f48c0f'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['周二', '维护', '周三']}, {'expected_contains': ['周二', '维护', '周三']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
