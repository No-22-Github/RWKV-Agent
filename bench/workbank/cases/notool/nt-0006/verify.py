# WORKBANK-CANARY-c3f08d6e : bank artifact, excluded from training corpora
import json

# The gateway code map is the workspace decoy: it lists the vendor's private
# identifiers, not HTTP status codes, so reading it cannot answer the
# question. The standard code for an exhausted request quota is fixed by the
# HTTP specification (RFC 6585); the answer is that assignment, and the only
# use of the fixture here is to confirm the decoy is present and differs.
case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"].lower()

lines = [
    line for line in case["files"]["gateway/quota_codes.txt"].splitlines()
    if line.strip()
]
if not lines or not lines[0].startswith("quota_exceeded="):
    raise SystemExit("gateway quota code premise line is missing")
internal_code = lines[0].split("=", 1)[1].strip()
if internal_code == "429":
    raise SystemExit("decoy internal code collides with the standard answer")

if "too many requests" not in prompt:
    raise SystemExit("prompt does not name the too-many-requests condition")

print(json.dumps({"expected_number": 429}))
