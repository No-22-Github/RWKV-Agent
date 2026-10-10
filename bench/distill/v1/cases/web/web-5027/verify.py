# DISTILL-CANARY-19d6e3aa : distillation case
"""Recompute the Emberton v1 signing notice period from the migration page."""
import datetime
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
notice_iso = re.search(r"notice published (\d{4}-\d{2}-\d{2})", page).group(1)
stop_iso = re.search(r"stops answering on (\d{4}-\d{2}-\d{2})", page).group(1)
stated = int(re.search(r"notice goes out (\d+) days", page).group(1))
notice = datetime.date.fromisoformat(notice_iso)
stop = datetime.date.fromisoformat(stop_iso)
gap = (stop - notice).days
if gap != stated:
    raise SystemExit("the stated notice period does not match the two dates")
print(json.dumps({"expected_number": gap}))
