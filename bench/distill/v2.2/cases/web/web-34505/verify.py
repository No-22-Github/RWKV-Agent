# DISTILL-CANARY-b291b993 : distillation case
import hashlib, json
case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
assert hashlib.sha256(json.dumps(case["web_fixture"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == '323f9d81bd3e50e51c673040f5f22e52742f8ed20e588166ed41e1bd7d17fc65', "web fixture changed"
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
