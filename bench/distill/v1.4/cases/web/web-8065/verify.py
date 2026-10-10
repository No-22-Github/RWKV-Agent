# DISTILL-CANARY-44b4b8ee : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'help.halcyonmail.com/limits' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'sysadmin-notes.net/halcyon-mail-limits' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '450' in sec["content"]

print(json.dumps({"expected_string": '450'}, ensure_ascii=False))
