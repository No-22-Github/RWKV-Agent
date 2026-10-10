# DISTILL-CANARY-dcc09ad1 : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Autoscaling limits per service.")
text = case["files"]["deploy/autoscale.ini"]
assert text.startswith("[search]")
out, section = [], None
for l in text.splitlines(keepends=True):
    if l.startswith("["):
        section = l.strip()
    if section == "[search]" and l.startswith("max_replicas = "):
        l = "max_replicas = 9" + l[len("max_replicas = 12"):]
    out.append(l)
print(json.dumps({"files": {"deploy/autoscale.ini": "".join(out)}}))
