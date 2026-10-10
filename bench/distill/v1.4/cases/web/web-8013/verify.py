# DISTILL-CANARY-5d332e5c : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
home = [w for w in pages if "qinfangjiayuan" in w["url"]][0]
assert "物业" in home["content"] and "2.8" in home["content"]
assert not any("装卸费" in w.get("content", "") for w in pages)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "物业", "小区"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
