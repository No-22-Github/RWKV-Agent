# DISTILL-CANARY-2419df9a : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.tarn-net.cn/support/ax6/warranty'][0]["content"]
m = re.search('整机保修 (\\d+) 个月', off)
assert m and m.group(1) == '36'
print(json.dumps({"expected_contains_any": ["36 个月", "36个月", "三年", "3 年", "3年"]}, ensure_ascii=False))
