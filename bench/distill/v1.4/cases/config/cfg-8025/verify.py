# DISTILL-CANARY-76ad5155 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/RO-400.yaml"].splitlines()[0] == "设备: 厨下反渗透机"
assert files["config/网点覆盖/龙泉苑.yaml"].splitlines()[0] == "网点: 龙泉苑"
assert "冲洗间隔" not in files["config/RO-400.yaml"]
assert "冲洗间隔" not in files["config/网点覆盖/龙泉苑.yaml"]
doc = files["docs/RO-400参数.md"].splitlines()
assert any("内置间隔" in l and "固件版本" in l for l in doc)
assert any("冲洗时长秒" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
