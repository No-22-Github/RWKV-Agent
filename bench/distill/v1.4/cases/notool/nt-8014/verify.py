# DISTILL-CANARY-9952e7d2 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("15", "9", "*", "*", "1-5")
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店后台定时任务")
print(json.dumps({"expected_contains_any": ["周一到周五", "周一至周五", "星期一到星期五", "星期一至星期五", "工作日"]}, ensure_ascii=False))
