# DISTILL-CANARY-fb4ed8bc : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["certs/INDEX.txt"].splitlines()
assert index[0] == "week | certificate | note"
body = "\n".join(index[1:])
assert "not scanned yet" in body
assert "certs/week-37-wash-certificate.md" in body
assert not any(p.startswith("certs/week-37-hygiene") for p in files)
assert any(p.startswith("certs/week-36-hygiene") for p in files)
words = ["not scanned", "hasn't been scanned", "not yet scanned", "no hygiene certificate", "not issued", "pending", "next week"]
print(json.dumps({"expected_contains_any": words}))
