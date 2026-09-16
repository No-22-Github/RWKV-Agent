# WORKBANK-CANARY-e2f83b56 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
svgs = {p: c for p, c in case["files"].items()
        if p.startswith("assets/") and p.endswith(".svg")}
by_content = {}
for path, content in svgs.items():
    by_content.setdefault(content, []).append(path)
dup_names = sorted({paths[0].rsplit("/", 1)[-1]
                    for paths in by_content.values() if len(paths) > 1})
print(json.dumps({
    "expected_count": len(svgs),
    "expected_duplicate": dup_names[0] if len(dup_names) == 1 else "AMBIGUOUS",
}))
