# DISTILL-CANARY-e85c2940 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import configparser
base = configparser.ConfigParser()
base.read_string(files["conf/base.ini"])
tenant = configparser.ConfigParser()
tenant.read_string(files["conf/tenant-huadong.ini"])
merged = {}
for section in ("limits", "retention"):
    for key, value in base.items(section):
        merged[key] = value
    for key, value in tenant.items(section):
        merged[key] = value
facts = [merged["daily_api_calls"], merged["bulk_rows"], merged["days"]]
print(json.dumps({"expected_contains_any": facts}))
