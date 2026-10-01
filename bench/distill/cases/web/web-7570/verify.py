# DISTILL-CANARY-9afbdc18 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.linyidoor.example/support/codes-2026" in e.get("url", ""))
fragments = ["门磁超时", "关严"]
phrases = []
for frag in fragments:
    lowered = frag.lower() in page["content"].lower()
    assert lowered, "fragment not grounded in fixture: " + frag
    phrases.append(frag)
    phrases.append(frag[0].upper() + frag[1:])
print(json.dumps({"expected_contains_any": phrases}))
