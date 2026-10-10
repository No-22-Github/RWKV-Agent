# DISTILL-CANARY-f2d3d942 : distillation case
import csv
import hashlib
import io
import json

case = json.load(open("case.json"))
CFG = {'tmpl': 'thsum', 'zh': False, 'hA': ['film_id', 'title', 'genre'], 'hB': ['film_id', 'month', 'tickets'], 'attr': 'Drama', 'period': '2026-08', 'price': False, 'sc': 1, 'ans_sc': 1, 'unit': 'tickets', 'cu': 'films|titles|movies', 'pathA': 'programme/films.csv', 'pathB': 'box_office/sales.csv', 'T': 1465, 'sha': {'README.md': '12788687a097c499873e6b03c08cee9a262a44e66c5da3cf78cd43419096f1f7', 'box_office/sales.csv': 'ae7bc61e283f107692f1a7fa6241297e52c7e70dd07f53b24aca906cbe188a64', 'programme/films.csv': '76876c9556080a1fc8c27ec4b6b67f34cea3f61b324238114b0ff081c1c9113f'}}

def fmt(v, sc):
    if sc == 1:
        return str(v)
    return ("%.1f" % (v / sc)).rstrip("0").rstrip(".")

def comma(s):
    if "." in s:
        a, b = s.split(".")
        return "{:,}".format(int(a)) + "." + b
    return "{:,}".format(int(s))

def forms(s, zh, unit, isint):
    """-> ("token", [s]) or ("any", [...]) accepted writings of the value s."""
    base = [s] if comma(s) == s else [s, comma(s)]
    if zh:
        out = []
        for b in base:
            out += [b + " " + unit, b + unit]
        if "." in s and len(s) >= 5:
            out += base
        return "any", sorted(set(out))
    if isint and len(s) <= 3:
        return "token", [s]
    return "any", sorted(set(base))

def count_forms(n, zh, cu):
    if zh:
        out = []
        for c in cu.split("|"):
            out += ["%d %s" % (n, c), "%d%s" % (n, c), "%s%s" % ("零一二三四五六七八九"[n], c), "%s %s" % ("零一二三四五六七八九"[n], c)]
        return "any", sorted(set(out))
    return "token", ["%d" % n]

f = case["files"]
assert {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(f.items())} == CFG["sha"]
A = list(csv.DictReader(io.StringIO(f[CFG["pathA"]])))
B = list(csv.DictReader(io.StringIO(f[CFG["pathB"]])))
hA, hB = CFG["hA"], CFG["hB"]
sel = [r for r in A if r[hA[2]] == CFG["attr"]]
assert 3 <= len(sel) <= 6 and len(B) >= 60
sc = CFG["sc"]
tot = {}
for r in sel:
    vs = [int(b[hB[2]]) for b in B if b[hB[0]] == r[hA[0]] and (CFG["period"] is None or b[hB[1]] == CFG["period"])]
    assert vs
    tot[r[hA[0]]] = sum(vs) * (int(r[hA[3]]) if CFG["price"] else 1)
t = CFG["tmpl"]
asc = CFG["ans_sc"]
zh = CFG["zh"]
if t == "top":
    top = max(tot, key=lambda k: tot[k])
    print(json.dumps({"expected_contains_any": [[r[hA[1]] for r in A if r[hA[0]] == top][0], top]}, ensure_ascii=False))
else:
    if t in ("count", "thsum"):
        hit = [v for v in tot.values() if v >= CFG["T"]]
    if t == "count":
        mode, lst = count_forms(len(hit), zh, CFG["cu"])
    else:
        v = sum(hit) if t == "thsum" else sum(tot.values())
        mode, lst = forms(fmt(v, asc), zh, CFG["unit"], asc == 1)
    if mode == "token":
        print(json.dumps({"expected_number": float(lst[0])}))
    else:
        print(json.dumps({"expected_contains_any": lst}, ensure_ascii=False))
