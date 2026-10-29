# DISTILL-CANARY-17d6bd8c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a34af29f241ab0e64b5eb409fef02b62487b9d1e39185b4c7dfb0b79ba0cfe80', "fixture changed"
FACTS = json.loads('[{"line": "func (c *tokenCache) purgeExpired()", "decoy": "func (c *tokenCache) evictOldest()", "al": 306, "dl": 11}, {"line": "janitorInterval = 90 * time.Second", "decoy": "staleAfter = 30 * time.Minute", "al": 432, "dl": 9}]')
ls = files['pkg/auth/token_cache.go'].split("\n")
def at(sub):
    h = [i + 1 for i, l in enumerate(ls) if sub in l]
    assert len(h) == 1, (sub, h)
    return h[0]
for f in FACTS:
    assert at(f["line"]) == f["al"] and at(f["decoy"]) == f["dl"], f
    assert f["al"] > 230 and f["dl"] < 150
print(json.dumps({"expected_string": 'purgeExpired'}, ensure_ascii=False))
