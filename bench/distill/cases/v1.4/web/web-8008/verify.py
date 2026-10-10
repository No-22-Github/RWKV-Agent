# DISTILL-CANARY-58ae1966 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if "fennel-lang.org" in w["url"]][0]
news = [w for w in case["web_fixture"] if "techdaily.cn" in w["url"]][0]["content"]
assert off.get("error") and "2026 年 11 月" in news
print(json.dumps({"expected_string": "11 月"}, ensure_ascii=False))
