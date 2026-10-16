# DISTILL-CANARY-7bbdbbfb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '620ed1798b6bf7ea6b4879cb814fb6d9d444c46c6b72de872a560ead1cc48bdf', "fixture changed"

def apply(files, ops):
    out = dict(files)
    for op in ops:
        if op[0] == "sub":
            _, path, old, new = op
            assert out[path].count(old) == 1, (path, old)
            out[path] = out[path].replace(old, new)
        elif op[0] == "app":
            out[op[1]] = out[op[1]] + op[2]
    return out

OPS = json.loads('[["sub", "src/utils/date_fmt.py", "def fmt_date(d):", "def format_date(d):"], ["sub", "src/report.py", "import fmt_date", "import format_date"], ["sub", "src/report.py", "\' + fmt_date(d)", "\' + format_date(d)"], ["sub", "src/export.py", "import fmt_date", "import format_date"], ["sub", "src/export.py", "[fmt_date(d), v]", "[format_date(d), v]"], ["sub", "tests/test_date.py", "import fmt_date", "import format_date"], ["sub", "tests/test_date.py", "assert fmt_date(d)", "assert format_date(d)"]]')
end = apply(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"][p] != t}}, ensure_ascii=False))
