# DISTILL-CANARY-a64f4a55 : distillation case
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
antwerp = [w for w in pages if "antwerp" in w["url"]][0]
assert "45" in antwerp["content"]
cities = [w for w in pages if w["url"].endswith("/cities")][0]
assert "Utrecht" in cities["content"] and "planned" in cities["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "Antwerp", "different city", "planned"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
