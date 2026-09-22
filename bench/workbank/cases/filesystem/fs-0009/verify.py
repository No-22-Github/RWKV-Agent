# WORKBANK-CANARY-4b7c1e92 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
files = case["files"]
# The district's telemetry gateway definition is the telemetry/ file whose
# first line opens the `gateway:` block the README describes.
candidates = sorted(path for path, content in files.items()
                    if path.startswith("telemetry/") and content.startswith("gateway:"))
answer = candidates[0] if len(candidates) == 1 else "UNKNOWN"
print(json.dumps({"expected": answer}))
