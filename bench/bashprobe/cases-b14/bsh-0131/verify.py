# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'be4cf5d5a78d918ee9829d97783f206e319a040490797c57b6e2f953d6c7455b', "fixture changed"
import re


def sel(op, path):
    if not path.startswith(op.get("prefix", "")):
        return False
    if op.get("name") and not re.search(op["name"], path):
        return False
    return not any(x in path for x in op.get("exclude", []))


def final(files, ops):
    out = dict(files)
    for op in ops:
        kind = op["op"]
        for path in sorted(out):
            if not sel(op, path):
                continue
            text = out[path]
            if kind == "line":
                table = dict(op["map"])
                text = "\n".join(table.get(l, l) for l in text.split("\n"))
            elif kind == "sub":
                text = re.sub(op["pattern"], op["repl"], text)
            elif kind == "del":
                text = "".join(l for l in text.splitlines(True) if not re.fullmatch(op["pattern"], l.rstrip("\n")))
            elif kind == "head":
                if not text.startswith(op["line"] + "\n"):
                    text = op["line"] + "\n" + text
            elif kind == "rename":
                new = re.sub(op["pattern"], op["repl"], path) if op["repl"] is not None else path.rsplit("/", 1)[0] + "/" + path.rsplit("/", 1)[1].replace(" ", "_")
                if new != path:
                    out[new] = out.pop(path)
                continue
            out[path] = text
    return out

OPS = json.loads('[{"op": "line", "prefix": "k8s/", "name": "deploy\\\\.yaml$", "exclude": ["/jobs/"], "map": [["  replicas: 1", "  replicas: 2"]]}, {"op": "line", "prefix": "k8s/", "name": "deploy\\\\.yaml$", "exclude": ["/jobs/"], "map": [["              memory: 256Mi", "              memory: 512Mi"]]}]')
end = final(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"].get(p) != t}}, ensure_ascii=False))
