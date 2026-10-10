# DISTILL-CANARY-081de869 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

ENV_VAR = {
    "cache_size_mb": "INGEST_CACHE_MB",
    "request_timeout_s": "INGEST_REQUEST_TIMEOUT_S",
    "worker_threads": "INGEST_WORKERS",
}


def read_env(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def read_profile(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


environment = read_env(files["deploy/production.env"])
profile = read_profile(files["config/production.yaml"])
defaults = read_profile(files["config/defaults.yaml"])

# README.md: environment, then profile, then shipped defaults.
key = "cache_size_mb"
var = ENV_VAR[key]
if var in environment:
    value = int(environment[var])
elif key in profile:
    value = int(profile[key])
else:
    value = int(defaults[key])

print(json.dumps({"expected_number": value}))
