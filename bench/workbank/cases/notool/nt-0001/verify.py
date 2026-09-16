import json
import re

# The expectation is derived from the rate stated in the prompt (the workspace
# is empty by design), never copied from the expect block.
# IEC MiB = 2**20 bytes; SI MB = 10**6 bytes; 1 h = 3600 s.
case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"]
rate_mib_per_s = float(re.search(r"([\d.]+)\s*MiB/s", prompt).group(1))
bytes_per_hour = rate_mib_per_s * (2 ** 20) * 3600
expected_mb_per_hour = bytes_per_hour / 10 ** 6
print(json.dumps({"expected_number": expected_mb_per_hour}))
