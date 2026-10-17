# DISTILL-CANARY-2456e177 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5b8851c5010cdd1deae26ef36ac6111e3af8b0ed19ae79cedecb649a131d95ee', "fixture changed"
OPS = json.loads('[["sub", "core/posts.py", "from core.slugify import slugify", "from core.slugify import slugify as make_slug"], ["sub", "core/posts.py", "\'/p/\' + slugify(title)", "\'/p/\' + make_slug(title)"], ["sub", "core/tags.py", "from core.slugify import slugify", "from core.slugify import slugify as make_slug"], ["sub", "core/tags.py", "\'tag:\' + slugify(name)", "\'tag:\' + make_slug(name)"]]')
end = dict(files)
for _, path, old, new in OPS:
    assert end[path].count(old) == 1, (path, old)
    end[path] = end[path].replace(old, new)
print(json.dumps({"files": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))
