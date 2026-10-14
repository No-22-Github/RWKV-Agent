# DISTILL-CANARY-525ce076 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {} and case["web_fixture"] == []
assert len(case["turns"]) == 1 and case["turns"][0]["prompt"].strip()
assert case["turns"][0]["expect"] == {"output_excludes": ["UNKNOWN"]} and "expect" not in case
assert "tool_policy" not in case and "offered_tools" not in case
t = case["tags"]
assert t["batch"] == "b20d" and t["license"] == "CC-BY-4.0" and t["source_dataset"] == 'dengxiaodi/deepseek-v4.1-flash-distill-zh-2k'
assert t["source_id"] == 1960 and t["source_category"] == '中国历史'
print(json.dumps({"files": case["files"]}))  # no answer to recompute; echo the (empty) fixture so gate --strict-shape recognises the shape
