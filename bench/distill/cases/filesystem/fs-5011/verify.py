# DISTILL-CANARY-88aa7005 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

sizes = {path: len(content.encode("utf-8")) for path, content in case["files"].items()}
largest = max(sorted(sizes), key=lambda path: sizes[path])
print(json.dumps({"expected_number": sizes[largest]}))
