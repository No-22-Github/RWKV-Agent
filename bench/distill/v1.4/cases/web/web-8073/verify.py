# DISTILL-CANARY-a683010c : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'ostrandercoop.org/join' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'neighborhoodnews.example.com/ostrander-coop' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '310' in sec["content"]

print(json.dumps({"expected_string": '310'}, ensure_ascii=False))
