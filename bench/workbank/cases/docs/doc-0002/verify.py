# WORKBANK-CANARY-5d0f3b62 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

MONTHS = {name: i + 1 for i, name in enumerate([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])}

memos = []
for path in ("policy/claims-timing-memo.md", "policy/expense-window-memo.md"):
    text = files[path]
    head = text.splitlines()[0]
    dm = re.search(r"issued (\d{1,2}) ([A-Z][a-z]+) (\d{4})", head)
    wm = re.search(r"within (\d+) days", text)
    if not dm or not wm:
        raise SystemExit("memo %s: issue date or submission window not found" % path)
    key = (int(dm.group(3)), MONTHS[dm.group(2)], int(dm.group(1)))
    memos.append((key, int(wm.group(1))))

memos.sort()
print(json.dumps({"expected": "%d days" % memos[-1][1]}))
