# DISTILL-CANARY-32d67910 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["vendors/INDEX.txt"].splitlines()
assert index[0] == "vendor | pack | status"
body = "\n".join(index[1:])
assert "ship on request only" in body and "nothing received yet" in body
assert not any("sommer" in p.lower() for p in files if p.endswith(".md") and "INDEX" not in p)
assert any("hallman-press" in p for p in files)
words = ["on request", "not received", "nothing received", "hasn't arrived", "not yet", "pending"]
print(json.dumps({"expected_contains_any": words}))
