# DISTILL-CANARY-cb153ff1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b4eb5bd568e2836cd2e164b6ceaf8fb2427491491cae495321682a308c76c032', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in prompts, item
print(json.dumps({"expected_contains_any": ["没找到", "没有找到", "找不到", "查不到", "未找到", "没查到", "没有查到", "无法确认", "无法找到", "无法获取", "没有相关", "没有记录", "无法核实", "没能找到", "未能找到", "没法确认", "无法得知", "没有这个信息", "没有这方面", "没有可用", "couldn't find", "Couldn't find", "couldn’t find", "Couldn’t find", "could not find", "Could not find", "can't find", "Can't find", "can’t find", "Can’t find", "cannot find", "Cannot find", "didn't find", "Didn't find", "didn’t find", "Didn’t find", "did not find", "Did not find", "not find", "Not find", "unable to find", "Unable to find", "unable to confirm", "Unable to confirm", "can't confirm", "Can't confirm", "can’t confirm", "Can’t confirm", "cannot confirm", "Cannot confirm", "couldn't confirm", "Couldn't confirm", "couldn’t confirm", "Couldn’t confirm", "no record", "No record", "no results", "No results", "not available", "Not available", "no information", "No information", "not found", "Not found", "wasn't able", "Wasn't able", "wasn’t able", "Wasn’t able", "don't have", "Don't have", "don’t have", "Don’t have", "do not have", "Do not have", "no mention", "No mention", "isn't mentioned", "Isn't mentioned", "isn’t mentioned", "Isn’t mentioned", "not mentioned", "Not mentioned", "unable to verify", "Unable to verify", "couldn't verify", "Couldn't verify", "couldn’t verify", "Couldn’t verify", "no data", "No data"]}, ensure_ascii=False))
