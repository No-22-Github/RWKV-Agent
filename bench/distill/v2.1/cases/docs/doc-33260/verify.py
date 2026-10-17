# DISTILL-CANARY-5cb1278d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4f1d416b24d6fdcc00191fd7017a07080f9f4460ae1cfb042bfee7f8866f3325', "fixture changed"
files = case["files"]

import posixpath, re, urllib.parse
def broken_links(files, doc):
    base = posixpath.dirname(doc)
    out = []
    text = files[doc]
    targets = re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", text) + re.findall(r"(?m)^\[[^\]]+\]:\s*(\S+)", text)
    for t in targets:
        if re.match(r"^([a-z]+:|#)", t):
            continue
        p = urllib.parse.unquote(t.split("#")[0].split("?")[0])
        if not p:
            continue
        full = posixpath.normpath(posixpath.join(base, p))
        if full not in files:
            out.append(t.split("#")[0])
    return out
got = [b for d in ['wiki/Home.md'] for b in broken_links(files, d)]
WANT = json.loads('["Guide/Intro.md"]')
assert sorted(got) == sorted(WANT), (got, WANT)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
inc += [x for r in case.get("expect", {}).get("files", {}).values() for x in r.get("contains", [])]
assert all(w in inc for w in WANT), WANT
first = case["turns"][0]["expect"].get("output_contains", [WANT[0]])[0]
assert not first.isdigit() or first == str(len(WANT)), first
print(json.dumps({"expected_string": first}, ensure_ascii=False))
