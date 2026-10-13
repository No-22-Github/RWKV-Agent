# DISTILL-CANARY-0b2110c8 : distillation case
import json
case = json.load(open("case.json"))
names = [e["location"].lower() for e in case["weather_fixture"]] + [a.lower() for e in case["weather_fixture"] for a in e["aliases"]]
assert not any(n in '稻城亚丁'.lower() for n in names), "the missing place must not resolve"
print(json.dumps({"expected_contains_any": ["查不到", "没有查到", "未查到", "查询不到", "找不到", "没找到", "未找到", "无法获取", "获取不到", "无法查询", "没有这个地方", "没有收录", "not found", "couldn't find", "could not find", "can't find", "cannot find", "unable to find", "no forecast", "not available", "isn't available"]}, ensure_ascii=False))
