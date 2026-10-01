# DISTILL-CANARY-5ade7edf : p13 holdout eval case (eval-only, never for training)
import json

case = json.load(open("case.json"))

def parse_env(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def parse_yaml(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out

env = parse_env(case["files"]["env-vars.txt"])
site = parse_yaml(case["files"]["site.yaml"])
defaults = parse_yaml(case["files"]["defaults.yaml"])
value = env.get("upload_max_mb") or site.get("upload_max_mb") or defaults.get("upload_max_mb")
print(json.dumps({"expected_number": float(value)}))
