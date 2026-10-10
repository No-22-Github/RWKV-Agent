# DISTILL-CANARY-5238b43d : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.maple-print.cn/support/warranty'][0]["content"]
files = case["files"]
f = files["采购/设备清单.txt"]
k = re.match(r"打印机：Maple (P\d+)", f).group(1)
val = re.search(r"\| %s \| (\d+) 个月" % k, off).group(1)
assert val == '24'
print(json.dumps({"expected_contains_any": ["24 个月", "24个月", "两年", "2 年", "2年"]}, ensure_ascii=False))
