# DISTILL-CANARY-bb79494d : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://www.quaysidecentre.example/halls'][0]["content"]
files = case["files"]
f = files["venue/hire-notes.txt"]
hall = re.match(r"Shortlisted at Quayside Centre: (\w+ \w+) \(", f).group(1)
val = re.search(r"\| %s \| (\d+) \|" % hall, off).group(1)
assert val == '340'
print(json.dumps({"expected_contains_any": ["340 people", "340 seats", "340 guests", "340 in theatre", "340 theatre", "340 delegates", "seats 340", "340 (theatre", "capacity of 340", "340 attendees"]}, ensure_ascii=False))
