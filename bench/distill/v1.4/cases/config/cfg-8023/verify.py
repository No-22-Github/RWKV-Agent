# DISTILL-CANARY-dbacf2d5 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/风炉.yaml"].splitlines()[0] == "设备: 风炉"
assert files["config/门店覆盖/三里屯店.yaml"].splitlines()[0] == "门店: 三里屯店"
assert "均温延时" not in files["config/风炉.yaml"]
assert "均温延时" not in files["config/门店覆盖/三里屯店.yaml"]
doc = files["docs/风炉参数.md"].splitlines()
assert any("自带程序" in l and "机型版本" in l for l in doc)
assert any("降温提醒分" in l and "无关" in l for l in doc)
words = ['没设', '没有设置', '未设置', '没有配置', '未配置', '没配置', '没有这一项', '没有这项', '没有这个键', '没有这个参数', '都没有', '查不到']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
