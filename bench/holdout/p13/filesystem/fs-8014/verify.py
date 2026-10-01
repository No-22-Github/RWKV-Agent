# DISTILL-CANARY-ab5119f0 : p13 holdout eval case (eval-only, never for training)
import hashlib
import json
from collections import Counter

case = json.load(open("case.json"))
hashes = Counter(
    hashlib.md5(content.encode("utf-8")).hexdigest()
    for content in case["files"].values()
)
pairs = sum(n * (n - 1) // 2 for n in hashes.values() if n >= 2)
print(json.dumps({"expected_number": pairs}))
