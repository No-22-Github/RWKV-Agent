# DISTILL-CANARY-58c2ea74 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import io
import re
import tokenize
total = 0
kinds = set()
for path in sorted(files):
    if not path.endswith(".py"):
        continue
    for tok in tokenize.generate_tokens(io.StringIO(files[path]).readline):
        if tok.type == tokenize.COMMENT:
            m = re.match(r"#\s*(TODO|FIXME)", tok.string)
            if m:
                total += 1
                kinds.add(m.group(1))
facts = [str(total)] + sorted(kinds)
print(json.dumps({"expected_contains_any": facts}))
