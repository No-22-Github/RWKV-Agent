# DISTILL-CANARY-2cb10e75 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '206468ed525aeb1cd45298bad665a8d215af07662bcdd842d6a752365830ab58', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["星河乐谱的 .xhs 文件以后还能打开吗？我有很多老谱子。", "转换是在哪个菜单里？"], item
print(json.dumps({"expected_string": "xhscore"}, ensure_ascii=False))
