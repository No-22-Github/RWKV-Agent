# DISTILL-CANARY-9d31c7e4 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
env = {}
for line in files["deploy/service.env"].splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, _, value = line.partition("=")
    env[key.strip()] = value.strip()
facts = [env["SERVICE_NAME"], env["LISTEN_PORT"], env["LOG_LEVEL"]]
print(json.dumps({"expected_contains_any": facts}))
