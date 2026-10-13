# DISTILL-CANARY-3b9d83c6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9bb3eb03613cefecf3f2777badd7ef1c5c221d1e489dc4ba5b5d9dac5499cfa4', "fixture changed"
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

OPS = json.loads('[{"op": "line", "prefix": "渠道配置/", "name": "支付\\\\.conf$", "exclude": ["/沙箱/"], "map": [["回调地址=https://pay.old.example.cn/notify", "回调地址=https://pay.example.cn/v2/notify"]]}]')
end = final(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"].get(p) != t}}, ensure_ascii=False))
