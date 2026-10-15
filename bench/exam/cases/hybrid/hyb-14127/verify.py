# EXAM-CANARY-80da3a7a : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = {k: v for k, v in case["files"].items() if k.startswith("exports/")}
sz = sorted(((len(v.encode()), k) for k, v in files.items()), reverse=True)
big, second = sz[0], sz[1]
print(json.dumps({"expected_number": big[0] - second[0]}))
