# DISTILL-CANARY-bdd1cea4 : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
target = [w for w in pages if "tinglan-load" in w["url"]][0]
assert target.get("error", "").startswith("HTTP 404")
col = [w for w in pages if w["url"].endswith(".gov.cn/bridge")][0]
assert "下线" in col["content"] and "改版" in col["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "404", "下线", "改版"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
