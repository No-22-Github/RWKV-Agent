# DISTILL-CANARY-700a13d9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '08cee039510d64d30b0fd37a90900af17fcf05095b8d0597108fd40aff57a27c', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^MAX_UPLOAD_BYTES\\s*=', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 15

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
