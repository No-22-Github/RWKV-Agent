# DISTILL-CANARY-c148cc39 : distillation case
import json
import re

case = json.load(open("case.json"))
page = [w for w in case["web_fixture"] if w["url"] == "https://orchidjs.dev/versions"][0]["content"]
print(json.dumps({"expected_string": re.search(r"\| latest（正式） \| (\S+) \|", page).group(1)}))
