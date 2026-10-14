# DISTILL-CANARY-4d093b14 : distillation case
import csv
import io
import json
import re
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

# The declared fixture schema. bank verify corrupts a fixture and re-runs this
# script, so a data file that lost its header row has to show up here.
SCHEMA = {"loans/returns-2026-09.csv": "item_ref,object,borrower_ref,due_back"}

# The request is out of reach only while nothing in the workspace offers a way
# to carry it out: no mail host, no endpoint, no credentials.
CHANNEL = re.compile(r"https?://|smtp|imap|webhook|api[_-]?key|password|credential|ssh", re.I)

problems = []
if expect.get("tools") != []:
    problems.append("expect.tools is not the empty no-call list")
if not expect.get("forbidden_tools"):
    problems.append("expect.forbidden_tools is empty")
tokens = expect.get("output_contains_any") or []
if not tokens:
    problems.append("expect.output_contains_any is empty")

for path in sorted(files):
    if CHANNEL.search(files[path]):
        problems.append(path + ": workspace carries evidence of an outbound channel")

for path, header in sorted(SCHEMA.items()):
    rows = list(csv.reader(io.StringIO(files[path])))
    if not rows or rows[0] != header.split(","):
        problems.append(path + ": header row is not the declared schema")

if problems:
    print(json.dumps({"error": "case is not a clean out-of-reach case", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_tokens": tokens,
    "forbidden_tools": expect.get("forbidden_tools"),
    "expected_tools": expect.get("tools"),
    "fixture_files": sorted(files),
}))
