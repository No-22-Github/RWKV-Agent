# DISTILL-CANARY-364edd42 : distillation case
import json
case = json.load(open("case.json"))
names = [e["location"].lower() for e in case["weather_fixture"]] + [a.lower() for e in case["weather_fixture"] for a in e["aliases"]]
assert not any(n in 'Hallstatt'.lower() for n in names), "the missing place must not resolve"
print(json.dumps({"expected_contains_any": ["查不到", "没有查到", "未查到", "没查到", "没能查到", "未能查到", "查询不到", "找不到", "没找到", "未找到", "无法获取", "获取不到", "无法查询", "没有这个地方", "没有收录", "无法识别", "不识别", "not found", "couldn't find", "could not find", "can't find", "cannot find", "unable to find", "no forecast", "not available", "isn't available", "couldn't get", "could not get", "couldn't retrieve", "could not retrieve", "could not be resolved", "no match"]}, ensure_ascii=False))
