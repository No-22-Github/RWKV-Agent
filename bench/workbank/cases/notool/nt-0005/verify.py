# WORKBANK-CANARY-4b7e2a91 : bank artifact, excluded from training corpora
import json
import re

# The throughput is stated in the prompt and recorded in the workspace note;
# the answer is that same rate expressed per day, derived here from the
# premise line and cross-checked against the prompt, never copied from the
# expect block.
case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"]

premise = case["files"]["jobs/archive_notes.txt"]
first = next(line for line in premise.splitlines() if line.strip())
match = re.search(r"throughput:\s*([\d.]+)\s*TiB per hour", first)
if not match:
    raise SystemExit("archive throughput premise line is missing")
rate = float(match.group(1))

prompt_rate = re.search(r"([\d.]+)\s*TiB per hour", prompt)
if not prompt_rate or abs(float(prompt_rate.group(1)) - rate) > 1e-9:
    raise SystemExit("prompt and workspace premise disagree")

print(json.dumps({"expected_number": rate * 24}))
