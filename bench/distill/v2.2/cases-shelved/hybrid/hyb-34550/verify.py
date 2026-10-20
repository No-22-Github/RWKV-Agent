# DISTILL-CANARY-f63dd728 : distillation case
import hashlib, json
case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == 'a72788eff273ef2567a5ca967327258d02f0eefe71945dd42ebe6b29d8698aa1', "fixture changed"
assert hashlib.sha256(json.dumps(case["web_fixture"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == 'd1c2181f9671e4e3867f2e21eaa8ea1e313f86cd69212c0fe2f5a2e882ce7cbd', "web fixture changed"
corpus = " ".join(case["files"].values()) + " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " ".join(t["prompt"] for t in case["turns"])
need = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
need += [x for r in case.get("expect", {}).get("files", {}).values() for x in r.get("contains", [])]
DERIVED = []
need = [x for x in need if x not in DERIVED]
assert all(x in corpus for x in need), need
frules = case.get("expect", {}).get("files", {})
wrote = {p: " ".join(r["contains"]) for p, r in frules.items() if r.get("contains")}
first = [x for x in case["turns"][0]["expect"].get("output_contains", [])]
anys = [x for t in case["turns"] for x in t["expect"].get("output_contains_any", [])]
res = {"files": wrote} if wrote and not first else ({"expected_string": need[0]} if need else {"expected_contains_any": anys})
print(json.dumps(res, ensure_ascii=False))
