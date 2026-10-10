# DISTILL-CANARY-7351a0f6 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'lanshan-marathon.org/signup' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'runnerclub.cn/lanshan-2026' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '260' in sec["content"]

print(json.dumps({"expected_string": '260'}, ensure_ascii=False))
