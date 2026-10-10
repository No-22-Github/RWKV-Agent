# DISTILL-CANARY-896da81d : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.lanchengpower.cn/tariff/residential'][0]["content"]
m = re.search('第二档：月用电量 (\\d+)—', off)
assert m and m.group(1) == '261'
print(json.dumps({"expected_contains_any": ["261 度", "261度", "第二档从 261", "261 度起"]}, ensure_ascii=False))
