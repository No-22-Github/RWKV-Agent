import json

case = json.load(open("case.json"))
files = case["files"]
FLAG = "express_checkout"


def parse_flags(text):
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        values[key.strip()] = value.strip().lower()
    return values


defaults = parse_flags(files["flags/defaults.yaml"])
tenant = parse_flags(files["flags/tenants/atlasgrocer.yaml"])

allowlist = set()
in_list = False
for line in files["docs/flag-guide.md"].splitlines():
    stripped = line.strip()
    if stripped.startswith("#"):
        in_list = "beta allowlist" in stripped.lower()
        continue
    if in_list and stripped.startswith("- "):
        allowlist.add(stripped[2:].strip())

if FLAG not in defaults:
    raise SystemExit("flag %s absent from defaults" % FLAG)

default_on = defaults[FLAG] == "true"
tenant_value = tenant.get(FLAG)
if tenant_value is None:
    effective = default_on
else:
    tenant_on = tenant_value == "true"
    if tenant_on and not default_on and FLAG not in allowlist:
        effective = default_on
    else:
        effective = tenant_on
print(json.dumps({"expected": "yes" if effective else "no"}))
