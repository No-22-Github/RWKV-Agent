# DISTILL-CANARY-efa8fa5f : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["site/README.txt"].startswith("Static site notes.")
assert case["files"]["site/blog/archive.htm.bak"].startswith("backup of")
out = {}
for path, text in case["files"].items():
    if path.endswith(".htm") and not path.startswith("site/vendor/"):
        assert text.startswith("<html><body>" + path), path
        out[path[:-4] + ".html"] = text
    elif path.endswith(".htm"):
        assert path.startswith("site/vendor/"), path
print(json.dumps({"files": out}))
