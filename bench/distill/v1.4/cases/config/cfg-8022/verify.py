# DISTILL-CANARY-1f5377ad : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/醒发柜.yaml"].splitlines()[0] == "设备: 醒发柜"
assert files["config/门店覆盖/望京店.yaml"].splitlines()[0] == "门店: 望京店"
assert "回差" not in files["config/醒发柜.yaml"]
assert "回差" not in files["config/门店覆盖/望京店.yaml"]
doc = files["docs/醒发柜参数.md"].splitlines()
assert any("内置回差" in l and "固件" in l for l in doc)
assert any("预热补偿℃" in l and "预热" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
