# DISTILL-CANARY-25957f94 : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "prices-2024" in w["url"]][0]
assert "1.20" in old["content"] and "2024" in old["title"]
notices = [w for w in pages if w["url"].endswith("/notices")][0]
assert "retired" in notices["content"] and "no longer" in notices["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "retired", "no longer", "2024", "outdated", "out of date", "old price"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
