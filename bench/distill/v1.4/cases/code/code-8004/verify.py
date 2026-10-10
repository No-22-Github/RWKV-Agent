# DISTILL-CANARY-1991b894 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# 兰溪花市订花小程序后端')
assert files['docs/变更说明.md'].splitlines()[0] == '# 变更说明'
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\w+)\(", text, re.M))
        defs.update(re.findall(r"^class (\w+)", text, re.M))
assert 'build_floral_quote' not in defs
assert 'build_floral_picklist' in defs
print(json.dumps({"expected_contains_any": ['没有', '不存在', '找不到', '没找到', '未找到', '尚未', '还没', '已移除', '已删除', '迁', '定价服务']}, ensure_ascii=False))
