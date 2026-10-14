# DISTILL-CANARY-427f5d38 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("各子系统配置")
assert f["配置/门禁/读卡器.yaml"].startswith("读卡器:")
m = re.search(r"开门延时秒:\s*(\d+)", f["配置/门禁/读卡器.yaml"])
assert m
assert re.search(r"夏季制冷温度:\s*(\d+)", f["配置/温控/教室空调.yaml"])
assert re.search(r"玩具消毒间隔天:\s*(\d+)", f["配置/消毒/消毒周期.yaml"])
ask = ["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"]
print(json.dumps({"expected_number": int(m.group(1)), "expected_contains_any": ask}, ensure_ascii=False))
