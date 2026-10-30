import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "docs.northwind.example" in e.get("url", ""))
versions = [line.split()[1] for line in page["content"].splitlines() if line.startswith("## ")]
latest = max(versions, key=lambda v: [int(part) for part in v.split(".")])
print(json.dumps({"expected": latest}))
