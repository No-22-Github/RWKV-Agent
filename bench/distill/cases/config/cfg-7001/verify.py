# DISTILL-CANARY-2ea8b573 : distillation case
import configparser
import json

case = json.load(open("case.json"))
merged = configparser.ConfigParser()
for name in ["config/defaults.ini", "config/site-hangzhou.ini", "config/instance-push-07.ini"]:
    merged.read_string(case["files"][name])
print(json.dumps({"expected_number": merged.getint("push", "batch_size")}))
