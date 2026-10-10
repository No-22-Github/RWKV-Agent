# DISTILL-CANARY-1b8f52a0 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out
base = parse(files["config/app.yaml"])
overlay = parse(files["config/prod.overlay.yaml"])
merged = dict(base)
merged.update(overlay)
facts = [merged["log_level"], merged["artifact_store"], merged["metrics"]]
print(json.dumps({"expected_contains_any": facts}))
