# DISTILL-CANARY-f04c80f0 : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "fee-2023" in w["url"]][0]
assert "4.5" in old["content"] and "2023" in old["title"]
notice = [w for w in pages if w["url"].endswith("/notice")][0]
assert "废止" in notice["content"] and "另行发文" in notice["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没",
         "废止", "另行发文", "不再更新", "旧版"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
