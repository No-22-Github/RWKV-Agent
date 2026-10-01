# DISTILL-CANARY-a58eb9e9 : distillation case
import json
import re
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
if expect.get("tools") != []:
    problems.append("expect.tools is not the empty no-call list")
if not expect.get("forbidden_tools"):
    problems.append("expect.forbidden_tools is empty")
tokens = expect.get("output_contains_any") or []
if not tokens or "UNKNOWN" in tokens:
    problems.append("expect.output_contains_any must be refusal words without UNKNOWN")
if "UNKNOWN" not in (expect.get("output_excludes") or []):
    problems.append("expect.output_excludes must list UNKNOWN")
if "offered_tools" not in case or set(case["offered_tools"]) != {"read_file", "list_files"}:
    problems.append("offered_tools must be the read-and-list subset this refusal depends on")
if "offered_tools" not in case or set(case["offered_tools"]) != {"read_file", "list_files"}:
    problems.append("offered_tools must be the read-and-list subset this refusal depends on")
if "工具" not in case["turns"][0]["prompt"]:
    problems.append("prompt no longer asks the model to check its own tool set")
if expect.get("output_contains") != ["工具"]:
    problems.append("expect.output_contains must pin the mention of the tool set")
CHANNEL = re.compile(r"https?://|ssh|sudo|reboot|systemctl|restart|shell|password|credential|token", re.I)
for path in sorted(files):
    if CHANNEL.search(files[path]):
        problems.append(path + ": fixture carries evidence of a restart channel")
if "值班工程师" not in files.get("README.md", ""):
    problems.append("README.md no longer records who restarts the server")

if problems:
    print(json.dumps({"error": "case is not a clean out-of-reach case", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_tokens": tokens,
    "forbidden_tools": expect.get("forbidden_tools"),
    "expected_tools": expect.get("tools"),
    "fixture_files": sorted(files),
}))
