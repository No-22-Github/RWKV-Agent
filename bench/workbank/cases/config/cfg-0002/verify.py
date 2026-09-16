# WORKBANK-CANARY-52be7d10 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]


def parse_env(text):
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        values[key.strip()] = value.strip()
    return values


def parse_flat_yaml(text):
    values = {}
    for line in text.splitlines():
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        values[key.strip()] = value.strip()
    return values


def parse_yaml_section(text, section):
    values = {}
    inside = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            inside = stripped.endswith(":") and stripped[:-1].strip() == section
            continue
        if inside and ":" in stripped:
            key, _, value = stripped.partition(":")
            values[key.strip()] = value.strip()
    return values


defaults = parse_yaml_section(files["deploy/defaults.yaml"], "ledger-sync")
service = parse_flat_yaml(files["services/ledger-sync.yaml"])
env = parse_env(files["environments/ledger-sync.env"])

if "MAX_CONNECTIONS" in env:
    effective = int(env["MAX_CONNECTIONS"])
elif "max_connections" in service:
    effective = int(service["max_connections"])
elif "max_connections" in defaults:
    effective = int(defaults["max_connections"])
else:
    raise SystemExit("max_connections not found in any layer")
print(json.dumps({"expected_number": effective}))
