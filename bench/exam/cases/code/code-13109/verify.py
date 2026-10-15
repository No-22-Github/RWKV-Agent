# EXAM-CANARY-3358520d : exam gap-fill case
import json, re

case = json.load(open("case.json", encoding="utf-8"))
definer, callers = None, []
for path, text in case["files"].items():
    if not path.endswith(".py"):
        continue
    if re.search(r"^def calc_discount\(", text, re.M):
        definer = path
    for line in text.splitlines():
        code = line.split("#", 1)[0]
        if re.search(r"\bcalc_discount\(", code) and not code.startswith("def "):
            callers.append(path)
            break
print(json.dumps({"expected_string": definer, "callers": sorted(callers)}))
