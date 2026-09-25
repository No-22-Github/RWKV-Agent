# DISTILL-CANARY-12bdd753 : distillation case
import json
import re


def attempts(page):
    match = re.search(r"up to (\d+) delivery attempts", page["content"])
    return int(match.group(1))


case = json.load(open("case.json"))
pages = sorted(case["web_fixture"], key=lambda page: page["published_at"])
assert attempts(pages[0]) != attempts(pages[-1])
print(json.dumps({"expected_number": attempts(pages[-1])}))
