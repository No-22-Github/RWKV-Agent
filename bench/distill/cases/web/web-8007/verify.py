# DISTILL-CANARY-575f16dc : distillation case
import json

case = json.load(open("case.json"))
ref = [w for w in case["web_fixture"] if w["url"] == "https://halyard.sh/docs/errors"][0]["content"]
line = [l for l in ref.splitlines() if l.startswith("- E4127:")][0]
assert "newer" in line
print(json.dumps({"expected_contains_any": ["lockfile", "lock file"]}))
