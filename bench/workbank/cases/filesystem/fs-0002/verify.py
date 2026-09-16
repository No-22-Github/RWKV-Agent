# WORKBANK-CANARY-b85d02ef : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
matches = [path for path, content in sorted(case["files"].items())
           if path.endswith(".yaml") and "retention" in content]
answer = matches[0] if len(matches) == 1 else "UNKNOWN"
print(json.dumps({"expected": answer}))
