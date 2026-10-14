# DISTILL-CANARY-46e0d29a : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import io
import re
import tokenize
marked_files = set()
kinds = set()
for path in sorted(files):
    if not path.endswith(".py"):
        continue
    for tok in tokenize.generate_tokens(io.StringIO(files[path]).readline):
        if tok.type == tokenize.COMMENT:
            m = re.match(r"#\s*(TODO|FIXME)", tok.string)
            if m:
                marked_files.add(path.split("/")[-1])
                kinds.add(m.group(1))
facts = sorted(marked_files) + sorted(kinds)
print(json.dumps({"expected_contains_any": facts}))
