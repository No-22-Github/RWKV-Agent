# DISTILL-CANARY-a24cbd02 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "429" in prompt and "401" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-of-house tablet")
words = ["too many", "rate limit", "rate limited", "unauthorized", "credentials", "not authenticated"]
print(json.dumps({"expected_contains_any": words}))
