# DISTILL-CANARY-897f49f3 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/软水机.yaml"].splitlines()[0] == "设备: 中央软水机"
assert files["config/网点覆盖/清晏园.yaml"].splitlines()[0] == "网点: 清晏园"
assert "再生启动硬度" not in files["config/软水机.yaml"]
assert "再生启动硬度" not in files["config/网点覆盖/清晏园.yaml"]
doc = files["docs/软水机参数.md"].splitlines()
assert any("自学习" in l and "固件版本" in l for l in doc)
assert any("再生周期天" in l and "定时" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
