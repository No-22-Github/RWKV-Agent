# DISTILL-CANARY-ef5c6c14 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/面团冷藏柜.yaml"].splitlines()[0] == "设备: 面团冷藏柜"
assert files["config/门店覆盖/中央工厂.yaml"].splitlines()[0] == "库位: 中央工厂一楼"
assert "冷藏回调" not in files["config/面团冷藏柜.yaml"]
assert "冷藏回调" not in files["config/门店覆盖/中央工厂.yaml"]
doc = files["docs/面团冷藏柜参数.md"].splitlines()
assert any("内置回调" in l and "固件版本" in l for l in doc)
assert any("报警回调分" in l and "无关" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
