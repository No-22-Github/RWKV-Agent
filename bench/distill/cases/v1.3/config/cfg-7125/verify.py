# DISTILL-CANARY-8451c1f8 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/services.yaml"]

sections = {}
current = None
for line in text.splitlines():
    if not line.strip() or line.strip().startswith("#"):
        continue
    if not line.startswith(" "):
        current = line.strip().rstrip(":")
        sections[current] = {}
    else:
        key, sep, value = line.strip().partition(":")
        if sep == "" or current is None:
            raise SystemExit("fixture guard failed: unparsable line " + repr(line))
        sections[current][key.strip()] = value.strip()

# Both near-named service blocks must exist and disagree on the asked key.
for name in ("ticket-api", "ticket-api-sandbox"):
    if name not in sections or "rate_limit_per_min" not in sections[name]:
        raise SystemExit("fixture guard failed: block " + str(name) + " is broken")
if sections["ticket-api"]["rate_limit_per_min"] == sections["ticket-api-sandbox"]["rate_limit_per_min"]:
    raise SystemExit("fixture guard failed: the two services no longer differ")

print(json.dumps({"expected_number": int(sections["ticket-api"]["rate_limit_per_min"])}))
