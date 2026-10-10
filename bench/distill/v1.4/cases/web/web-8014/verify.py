# DISTILL-CANARY-3a995161 : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "cold-store-2024" in w["url"]][0]
assert "0.6" in old["content"] and "2024" in old["title"]
notice = [w for w in pages if w["url"].endswith("/notice")][0]
assert "下线" in notice["content"] and "不再更新" in notice["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没",
         "旧版", "下线", "不再更新", "过时", "过期", "当期"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
