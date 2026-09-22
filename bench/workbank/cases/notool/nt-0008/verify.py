# WORKBANK-CANARY-6d1c9f30 : bank artifact, excluded from training corpora
import json

# A SHA-256 digest is 32 bytes, i.e. 64 hexadecimal characters, fixed by
# FIPS 180-4. The workspace snapshot carries the retired 32-character field
# length (a byte count used as a character count) and the answer must not be
# taken from it; the snapshot is read here only to confirm the stale decoy is
# present and differs from the answer.
case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"].lower()

lines = [
    line for line in case["files"]["security/digest_snapshot.txt"].splitlines()
    if line.strip()
]
if not lines or not lines[0].startswith("digest_length_hex="):
    raise SystemExit("digest snapshot premise line is missing")
stale = int(lines[0].split("=", 1)[1])
if stale == 64:
    raise SystemExit("stale snapshot collides with the answer")

if "sha-256" not in prompt:
    raise SystemExit("prompt does not name SHA-256")

print(json.dumps({"expected_number": 64}))
