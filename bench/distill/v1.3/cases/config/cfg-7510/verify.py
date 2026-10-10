# DISTILL-CANARY-d6710c8a : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out
enrich = parse(files["conf/enrich.flags"])
ingest = parse(files["conf/ingest.flags"])
facts = [enrich["mode"], ingest["mode"],
         enrich["sink"].rsplit(".", 1)[1], ingest["sink"].rsplit(".", 1)[1]]
print(json.dumps({"expected_contains_any": facts}))
