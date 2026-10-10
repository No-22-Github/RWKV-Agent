# DISTILL-CANARY-69599283 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://heron-gw.org/releases'][0]["content"]
files = case["files"]
f = files["运维/部署笔记.md"]
cur = re.match(r"生产网关：Heron (\d+\.\d+\.\d+)", f).group(1)
stable = re.findall(r"\| (\d+\.\d+\.\d+) \| stable \|", off)
assert cur in stable and cur != stable[0]
val = stable[0]
assert val == '3.6.2'
print(json.dumps({"expected_contains_any": ["3.6.2"]}, ensure_ascii=False))
