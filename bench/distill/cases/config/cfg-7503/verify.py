# DISTILL-CANARY-f04d9b37 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import configparser
parser = configparser.ConfigParser()
parser.read_string(files["conf/scheduler.ini"])
facts = [
    str(parser.getint("queue", "retry_backoff_seconds")),
    parser.get("alerts", "webhook"),
    parser.get("alerts", "quiet_hours"),
]
print(json.dumps({"expected_contains_any": facts}))
