# DISTILL-CANARY-d3f0e1e1 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'docs.quillfeather.io/broker/ports' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'opsdiary.example.org/quillfeather-ports' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '7421' in sec["content"]
files = case["files"]
assert files['deploy/manifest.csv'].splitlines()[0] == 'service,component,version,env'
assert 'orders,quillfeather-broker,3.4.1,prod' in files['deploy/manifest.csv'].splitlines()

print(json.dumps({"expected_string": '7421'}, ensure_ascii=False))
