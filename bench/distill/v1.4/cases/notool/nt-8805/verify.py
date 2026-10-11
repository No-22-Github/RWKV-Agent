# DISTILL-CANARY-9835e290 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '4f919a7aaf108684e3091777668984981f32267c30476412dbb5c95e22bfe9e9'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['青色', '冷藏', '橙色', '常温']}, {'expected_contains': ['青色', '冷藏', '橙色', '常温']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
