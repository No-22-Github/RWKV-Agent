# DISTILL-CANARY-e8590793 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.weavergateparking.example/codes" in e.get("url", ""))
fragments = ["validated", "help button"]
phrases = []
for frag in fragments:
    lowered = frag.lower() in page["content"].lower()
    assert lowered, "fragment not grounded in fixture: " + frag
    phrases.append(frag)
    phrases.append(frag[0].upper() + frag[1:])
print(json.dumps({"expected_contains_any": phrases}))
