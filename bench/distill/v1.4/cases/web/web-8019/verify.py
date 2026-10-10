# DISTILL-CANARY-6ea8e90e : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
target = [w for w in pages if "helmet-policy" in w["url"]][0]
assert target.get("error", "").startswith("HTTP 404")
index = [w for w in pages if w["url"].endswith("/help")][0]
assert "temporarily offline" in index["content"] and "reorganised" in index["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "404", "offline", "temporarily", "reorganised"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
