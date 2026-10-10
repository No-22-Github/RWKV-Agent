# DISTILL-CANARY-77a12512 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("30", "18", "1", "*", "*")
print(json.dumps({"expected_contains_any": ["每月 1 日", "每月1日", "每个月的 1 日", "每月一号", "每个月的一号", "月初第一天", "每月 1 号", "每月1号", "每个月 1 号", "每个月1号"]}, ensure_ascii=False))
