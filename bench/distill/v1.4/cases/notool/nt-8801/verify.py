# DISTILL-CANARY-84f34ee0 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'README.md': '84eda1982832416885b4cb0adc8b48309ec57b45eb73cf7b1f11b44bb88cb442'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h

answers = [{'expected_contains': ['浏览器', '版本']}, {'expected_contains': ['浏览器', '版本']}]
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
