# DISTILL-CANARY-54750ad3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# 云澜市桥梁养护管理平台')
assert files['docs/迁移说明.md'].splitlines()[0] == '# 迁移说明'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'schedule_span_inspection' not in defs
assert 'schedule_span_repair' in defs
print(json.dumps({"expected_contains_any": ['没有', '不存在', '找不到', '没找到', '未找到', '尚未', '还没', '已删除', '已下线', '检测平台', '市级']}, ensure_ascii=False))
