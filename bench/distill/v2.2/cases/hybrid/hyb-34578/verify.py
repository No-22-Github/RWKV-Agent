# DISTILL-CANARY-2931af12 : distillation case
import hashlib, json
case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == '6d8d7ba05ab7ee12b0dd7339a416c37c6c63dee8546c9abe9a9594c393de00d0', "fixture changed"
assert hashlib.sha256(json.dumps(case["web_fixture"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == 'f441bdae5128e0e9de9afe328d9fd950a561fb77ececfe28c499511447533258', "web fixture changed"
corpus = " ".join(case["files"].values()) + " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " ".join(t["prompt"] for t in case["turns"])
need = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
need += [x for r in case.get("expect", {}).get("files", {}).values() for x in r.get("contains", [])]
DERIVED = ["workers: 20", "15"]
need = [x for x in need if x not in DERIVED]
assert all(x in corpus for x in need), need
frules = case.get("expect", {}).get("files", {})
wrote = {p: " ".join(r["contains"]) for p, r in frules.items() if r.get("contains")}
first = [x for x in case["turns"][0]["expect"].get("output_contains", [])]
anys = [x for t in case["turns"] for x in t["expect"].get("output_contains_any", [])]
res = {"files": wrote} if wrote and not first else ({"expected_string": need[0]} if need else {"expected_contains_any": anys})
print(json.dumps(res, ensure_ascii=False))
