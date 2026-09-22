# WORKBANK-CANARY-3a7f2c9d : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
text = case["files"]["environments/eu-west.env"]

env = {}
for line in text.splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        continue
    key, _, value = stripped.partition("=")
    env[key.strip()] = value.strip()

if "TARIFF_CALC_PORT" not in env:
    raise SystemExit("TARIFF_CALC_PORT not set for eu-west")
print(json.dumps({"expected_number": int(env["TARIFF_CALC_PORT"])}))
