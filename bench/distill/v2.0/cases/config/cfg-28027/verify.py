# DISTILL-CANARY-c51cf247 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/管线机.yaml"].splitlines()[0] == "设备: 管线机"
assert files["config/网点覆盖/滨湖小学.yaml"].splitlines()[0] == "网点: 滨湖小学"
assert "UV 延时" not in files["config/管线机.yaml"]
assert "UV 延时" not in files["config/网点覆盖/滨湖小学.yaml"]
doc = files["docs/管线机参数.md"].splitlines()
assert any("内置延时" in l and "固件" in l for l in doc)
assert any("保温时长分" in l and "保温" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
