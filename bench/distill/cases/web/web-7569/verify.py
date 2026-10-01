# DISTILL-CANARY-aa5f8586 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.nuanshanheater.example/codes" in e.get("url", ""))
fragments = ["风压异常", "清理排烟管后复位"]
phrases = []
for frag in fragments:
    lowered = frag.lower() in page["content"].lower()
    assert lowered, "fragment not grounded in fixture: " + frag
    phrases.append(frag)
    phrases.append(frag[0].upper() + frag[1:])
print(json.dumps({"expected_contains_any": phrases}))
