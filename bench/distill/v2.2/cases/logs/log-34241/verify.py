# DISTILL-CANARY-bf600a57 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '039976e0f9de420344744db2999a817413b72af26a4311ae665fd547c73e373e', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
_val = sum(1 for l in files['patrol/cache-queue-patrol.out'].splitlines() if 'ERROR' in l and 'cache' in l)
assert "%g" % _val == '3', (_val, '3')
DERIVED = json.loads('["3"]')
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in corpus or item in DERIVED, item
print(json.dumps({"expected_string": "3"}, ensure_ascii=False))
