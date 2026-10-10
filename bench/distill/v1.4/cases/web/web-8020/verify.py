# DISTILL-CANARY-54aeac3a : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "subscriptions-2025" in w["url"]][0]
assert "24.90" in old["content"] and "2025" in old["title"]
city = [w for w in pages if w["url"].endswith("/lyon")][0]
assert "retired" in city["content"] and "no longer" in city["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "retired", "no longer", "2025", "outdated", "out of date"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
