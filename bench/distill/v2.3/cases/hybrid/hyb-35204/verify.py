# DISTILL-CANARY-3b9b0341 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7e58a62d03be2b756c1bbc735cf59237de7c4abb18cd6d5a7f9e6e606be02c77', "fixture changed"
EDITS = [["文档/社区团购-价目.md", "| 五常大米 | 56 | 袋 |", "| 五常大米 | 61.6 | 袋 |"], ["文档/社区团购-价目.md", "| 山茶油 | 128 | 瓶 |", "| 山茶油 | 120 | 瓶 |"]]
ADDS = []
VALS = []
WRITES = {}
files = dict(case["files"])
final = {}
for path, old, new in EDITS:
    cur = final.get(path, files[path])
    assert cur.count(old) == 1, (path, old)
    final[path] = cur.replace(old, new)
for path, text in ADDS:
    final[path] = final.get(path, files.get(path, "")) + text
for path, subs in WRITES.items():
    final[path] = "\n".join(subs)
pool0 = " ".join(files.values()) + " " + " ".join(t["prompt"] for t in case["turns"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert final[path] == rule["equals"], path
    elif "contains" in rule:
        if path in final:
            assert all(s in final[path] for s in rule["contains"]), path
        else:
            assert path not in files, path
    elif rule.get("unchanged"):
        assert path in files and path not in final, path
pool = " ".join(files.values()) + " " + " ".join(files) + " " + " ".join(final.values()) + " " + " ".join(t["prompt"] for t in case["turns"]) + " " + " ".join(VALS)
for turn in case["turns"]:
    for s in turn["expect"].get("output_contains", []):
        assert s in pool or (s.isdigit() and len(s) <= 3), s
print(json.dumps({"files": final, "answers": [t["expect"].get("output_contains", []) for t in case["turns"]]}, ensure_ascii=False))
