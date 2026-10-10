# DISTILL-CANARY-08d09109 : distillation case
import json
import re

case = json.load(open("case.json"))
best = None
for path in ("memos/ops-2026-09-05.txt", "memos/bulletin-2026-09-21.txt"):
    text = case["files"][path]
    head = text.splitlines()[0]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", head)
    if not m:
        raise SystemExit("memo header has no date: " + path)
    if best is None or m.group(1) > best[0]:
        best = (m.group(1), text)
vm = re.search(r"buffer_ms to (\d+)", best[1])
if not vm:
    raise SystemExit("governing memo names no buffer_ms value")
out = []
for line in case["files"]["config/playout.yaml"].splitlines():
    if line.strip().startswith("buffer_ms:"):
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + "buffer_ms: %s  # install guide default" % vm.group(1)
    out.append(line)
print(json.dumps({"files": {"config/playout.yaml": "\n".join(out) + "\n"}}))
