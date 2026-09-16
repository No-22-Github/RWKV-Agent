# WORKBANK-CANARY-3e7a19c4 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
sizes = {path: len(content.encode("utf-8")) for path, content in case["files"].items()}
print(json.dumps({"expected_number": max(sizes.values())}))
