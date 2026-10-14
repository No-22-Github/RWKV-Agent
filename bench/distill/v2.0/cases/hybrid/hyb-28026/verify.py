# DISTILL-CANARY-ad2d55fb : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.qinghe-code.cn/courses/fees'][0]["content"]
files = case["files"]
f = files["家庭/报名记录.txt"]
k = re.match(r"班型：(\S+)", f).group(1)
val = re.search(r"\| %s \| (\d+) 元" % k, off).group(1)
assert val == '168'
print(json.dumps({"expected_contains_any": ["168 元", "168元", "168 块"]}, ensure_ascii=False))
