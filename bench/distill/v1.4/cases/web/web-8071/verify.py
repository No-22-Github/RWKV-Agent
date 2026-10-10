# DISTILL-CANARY-7b8eef4a : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'quillbird.dev/docs/config' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'stackhelp.example.org/q/quillbird-timeout' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '120' in sec["content"]

print(json.dumps({"expected_string": '120'}, ensure_ascii=False))
