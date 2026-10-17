"""b21n sub 3: count_markers 33525-33536."""
import random

from common import make, L, P_SEARCH, P_BASH, P_READ
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


HEAD = ("import re\ndef count(word, inc=('',), exc=(), per=False):\n    n = {}\n    for p, t in sorted(files.items()):\n"
        "        if not p.startswith(tuple(inc)) or (exc and p.startswith(tuple(exc))):\n            continue\n"
        "        for l in t.split(chr(10)):\n            if re.search(r'(#|//|/\\*|^\\s*\\*|--|;)\\s*' + word + r'\\b', l):\n                n[p] = n.get(p, 0) + 1\n    return n if per else sum(n.values())\n")


def ctruth(expr, want):
    return HEAD + "ans = %s\nassert str(ans) == %r, ans\n" % (expr, want)


def spr(base, marks):
    """insert marker lines: marks = [(index, text)] (index into base before insertion; processed from the end)."""
    out = list(base)
    for i, tx in sorted(marks, reverse=True):
        out.insert(min(i, len(out)), tx)
    return out


@reg
def c25():
    a = spr(py_mod(["feed", "post"], 251, None, 4).split("\n"), [(3, "# TODO: paginate"), (9, "    # TODO handle empty feed"), (16, "# TODO(kai): cache this")])
    b = spr(py_mod(["tag", "user"], 252, None, 3).split("\n"), [(5, "# TODO: drop py2 branch"), (12, "TODO_FILE = 'todo.txt'  # path, not a marker")])
    c = py_mod(["row", "key"], 253, None, 3) + "\nmsg = 'remember the TODO list'\ntodo_items = []\n"
    f = {"src/feed.py": "\n".join(a), "src/tags.py": "\n".join(b), "src/util.py": c,
         "vendor/lib.py": "# TODO: vendored, not ours\n# TODO: another\n", "docs/plan.md": "TODO: write docs\n", "tests/test_feed.py": "# TODO add tests\n"}
    make("code-33525", sub="count", task_type="count_markers", desc="Count TODO comments in src only; decoys in vendor, docs, strings and names",
         files=f, turns=[{"p": "src 目录里有多少条 TODO 注释？只数 src 下面注释里的 TODO 标记，vendor、docs、tests 不算，变量名和字符串里的也不算。只回答数字。",
                          "inc": ["4"]}],
         truth=ctruth("count('TODO', inc=('src/',))", "4"), decoy="9", policy=P_BASH, ref_calls=3,
         refs=[("grep -rE '(#|//) *TODO\\b' src | wc -l", "4")],
         notes=N("TR-DECOY: vendor/docs/tests, TODO_FILE, string 'TODO list', todo_items.", "grep comment TODO in src; count.", "4."))


@reg
def c26():
    r = random.Random(26)
    parts = {}
    plan = {"api/users.js": 3, "api/orders.js": 5, "api/search.js": 2, "api/health.js": 0, "api/auth.js": 4}
    for k, (p, n) in enumerate(plan.items()):
        base = js_mod(["req", "res"], 260 + k, 3).split("\n")
        parts[p] = "\n".join(spr(base, [(2 + 3 * i, "// FIXME: %s" % r.choice(["race on retry", "leaks handle", "wrong status code", "n+1 query", "no timeout", "double encode"])) for i in range(n)]))
    parts["api/auth.js"] += "\nconst FIXME_LEVEL = 3;\n"
    parts["README.md"] = "FIXME list lives in the issue tracker.\n"
    # 'FIXME-ish' line: FIXME followed by '-' keeps the word boundary, so it counts as a marker: auth.js has 5
    make("code-33526", sub="count", task_type="count_markers", desc="Which file has the most FIXME comments",
         files=parts, turns=[{"p": "Which file under api/ has the most FIXME comments, and how many? A FIXME_LEVEL constant is not a marker.",
                              "inc": ["api/orders.js", "5"]}],
         truth=ctruth("max(count('FIXME', inc=('api/',), per=True).items(), key=lambda kv: (kv[1], kv[0]))", "x").replace("assert str(ans) == 'x', ans\n", "assert ans == ('api/orders.js', 5), ans\nans = 'api/orders.js'\n"),
         decoy="api/auth.js", policy=P_BASH, ref_calls=4, refs=[("grep -rc 'FIXME:' api", "orders.js:5")],
         notes=N("TR-DECOY: FIXME_LEVEL, README.", "count per file.", "orders.js 5"))


@reg
def c27():
    g1 = spr(go_mod("ring", ["slot", "buf"], 271, 4).split("\n"), [(8, "\t// TODO: grow the ring"), (13, "\t// FIXME: off by one on wrap"), (20, "// TODO(ana): lock-free")])
    g2 = spr(go_mod("ring", ["peer", "msg"], 272, 3).split("\n"), [(9, "// FIXME: panics on nil"), (14, "\t// TODO: metrics"), (18, "\t// TODO: tracing"), (21, "var todoCount int // not a marker")])
    f = {"ring/ring.go": "\n".join(g1), "ring/peer.go": "\n".join(g2), "ring/ring_test.go": "package ring\n\n// TODO more cases\n// FIXME flaky on CI\n",
         "main.go": "package main\n\nfunc main() {\n\tprintln(\"TODO: nothing to see\")\n}\n", "NOTES.txt": "TODO TODO FIXME in the wiki\n"}
    make("code-33527", sub="count", task_type="count_markers", desc="TODO and FIXME counts separately over non-test Go files",
         files=f, turns=[{"p": "统计一下 ring 目录（不含测试文件 _test.go）里的注释标记：TODO 有几条，FIXME 有几条？字符串里和变量名里的不算。",
                          "inc": ["4", "2"]}],
         truth=ctruth("count('TODO', inc=('ring/ring.go', 'ring/peer.go'))", "4"), decoy="6", policy=P_BASH, ref_calls=4,
         refs=[("grep -hE '// *TODO' ring/ring.go ring/peer.go | wc -l", "4")],
         notes=N("TR-DECOY: test file, println string, todoCount, NOTES.txt.", "grep each marker in the 2 non-test files.", "TODO 4, FIXME 2."))


@reg
def c28():
    rows = ["# crawler schedule", ""] + yaml_conf(["feed", "page"], 281, 5).split("\n")
    rows = spr(rows, [(3, "# TODO(lena): move to cron"), (9, "# TODO(omar): raise interval"), (14, "# TODO(lena): per-host limits")])
    sh = spr(sh_mod(["fetch", "parse"], 282, 3).split("\n"), [(4, "# TODO(lena): quote args"), (9, "# TODO(omar): shellcheck"), (12, "# TODO: unowned")])
    f = {"conf/schedule.yml": "\n".join(rows), "bin/crawl.sh": "\n".join(sh), "bin/notes.md": "owners: TODO(lena) lists are in the wiki\n",
         "bin/parse.py": py_mod(["cell", "link"], 283, "# TODO(lena): rewrite in go", 2)}
    make("code-33528", sub="count", task_type="count_markers", desc="TODO items assigned to one owner across yaml, shell and python",
         files=f, turns=[{"p": "How many TODO comments are assigned to lena (written as TODO(lena))? Count comments in conf/ and bin/ code files; skip the markdown note. Just the number.",
                          "inc": ["4"]}],
         truth=ctruth("sum(len([1 for l in t.split(chr(10)) if re.search(r'(#|//)\\s*TODO\\(lena\\)', l)]) for p, t in files.items() if not p.endswith('.md'))", "4"),
         decoy="5", policy=P_BASH, ref_calls=3, refs=[("grep -rE '# *TODO\\(lena\\)' conf bin --include=* | wc -l", "4")],
         notes=N("TR-DECOY: markdown mention, other owners, unowned TODO.", "grep TODO(lena).", "4."))


@reg
def c29():
    base = lambda s, n: js_mod(["a", "b", "c"], s, n, ts=True).split("\n")
    f = {"src/a.ts": "\n".join(spr(base(291, 3), [(2, "// TODO: types"), (6, "// HACK: cast away"), (9, "// FIXME: wrong unit")])),
         "src/b.ts": "\n".join(spr(base(292, 3), [(3, "// HACK: pad by 1"), (5, "/* TODO: split */"), (8, "// hack: lowercase is not a marker")])),
         "src/c.ts": "\n".join(spr(base(293, 2), [(1, "// FIXME"), (4, "const HACKS = 3;")])),
         "node_modules/x/index.ts": "// TODO: upstream\n// FIXME: upstream\n// HACK: upstream\n",
         "README.md": "HACK: none\n"}
    make("code-33529", sub="count", task_type="count_markers", desc="Total of TODO FIXME HACK in src, skipping lowercase and constant names",
         files=f, turns=[{"p": "In src/, how many comment markers are there in total (TODO, FIXME and HACK, uppercase, in comments)? node_modules and the README don't count. Give me the total and the number for each kind.",
                          "inc": ["6", "2"]}],
         truth=("import re\ntot = 0\nfor p, t in files.items():\n    if p.startswith('src/'):\n        for l in t.split(chr(10)):\n            if re.search(r'(//|/\\*)\\s*(TODO|FIXME|HACK)\\b', l):\n                tot += 1\nans = tot\nassert ans == 6, ans\n"),
         decoy="11", policy=P_BASH, ref_calls=4, refs=[("grep -rEn '(//|/\\*) *(TODO|FIXME|HACK)' src | wc -l", "6")],
         notes=N("TR-DECOY: node_modules, lowercase hack, HACKS constant.", "grep -E with alternation over src.", "total 6 (2 each)."))


@reg
def c30():
    py = lambda s, mk: "\n".join(spr(py_mod(["order", "item"], s, None, 3).split("\n"), mk))
    f = {"shop/cart.py": py(301, [(4, "# TODO: coupons"), (10, "# FIXME: rounding"), (15, "# TODO: bundles")]),
         "shop/pay.py": py(302, [(3, "# FIXME: retry on 502"), (8, "# FIXME: idempotency key"), (12, "# TODO: 3ds")]),
         "shop/ship.py": py(303, [(6, "# TODO: carriers"), (11, "# FIXME: weight units")]) + "\nnotes = ['FIXME later', 'TODO soon']\n",
         "scripts/seed.py": "# TODO: seed data\n# FIXME: seed order\n", "shop/__init__.py": ""}
    make("code-33530", sub="count", task_type="count_markers", desc="TODO count then FIXME count in shop/, re-counted per turn",
         files=f, turns=[{"p": "shop 包里一共有多少条 TODO 注释？scripts 不算。", "inc": ["4"]},
                         {"p": "FIXME 呢？同样只数 shop 包里的注释。", "inc": ["4"], "any": ["FIXME"]}],
         truth=ctruth("count('TODO', inc=('shop/',))", "4"), decoy="6", policy=P_BASH, ref_calls=5,
         refs=[("grep -rE '# *TODO' shop | wc -l", "4"), ("grep -rE '# *FIXME' shop | wc -l", "4")],
         notes=N("TR-DECOY: strings in list, scripts/.", "grep twice.", "TODO 4, FIXME 4."))


@reg
def c31():
    g = lambda s, mk: "\n".join(spr(go_mod("svc", ["job", "lease"], s, 3).split("\n"), mk))
    f = {"svc/job.go": g(311, [(8, "// TODO: timeouts"), (12, "// TODO: cancel")]), "svc/lease.go": g(312, [(9, "// FIXME: renew race")]),
         "scripts/run.sh": "\n".join(spr(sh_mod(["boot", "stop"], 313, 2).split("\n"), [(5, "# TODO: trap EXIT")])),
         "scripts/lint.sh": "#!/usr/bin/env bash\necho ok\n", "README.md": "# svc\nTODO: write me\n"}
    make("code-33531", sub="count", task_type="count_markers", desc="Which code files contain TODO comments (list)",
         files=f, turns=[{"p": "哪些代码文件里有 TODO 注释？README 不算，只列文件路径，一行一个。", "inc": ["svc/job.go", "scripts/run.sh"], "exc": ["svc/lease.go", "scripts/lint.sh"]}],
         truth=ctruth("sorted(count('TODO', exc=('README',), per=True))", "['scripts/run.sh', 'svc/job.go']").replace("assert str(ans) == \"['scripts/run.sh', 'svc/job.go']\", ans\n", "assert ans == ['scripts/run.sh', 'svc/job.go'], ans\nans = 'svc/job.go'\n"),
         decoy="README.md", policy=P_SEARCH, ref_calls=3, refs=[("grep -rl 'TODO' svc scripts", "job.go")],
         notes=N("TR-DECOY: FIXME file, README.", "grep -rl TODO.", "svc/job.go, scripts/run.sh."))


@reg
def c32():
    py = lambda s, mk: "\n".join(spr(py_mod(["metric", "gauge"], s, None, 3).split("\n"), mk))
    f = {"mon/collect.py": py(321, [(4, "# FIXME: units"), (9, "# FIXME: dedupe"), (14, "# FIXME: sampling")]), "mon/emit.py": py(322, [(5, "# FIXME: batch size")]),
         "mon/ui.js": "// FIXME: dark mode\n// FIXME: i18n\n", "mon/cfg.yml": "# FIXME: rotate keys\nkeys: []\n", "mon/log.py": "msg = 'FIXME in text'\n"}
    make("code-33532", sub="count", task_type="count_markers", desc="FIXME comments in Python files only",
         files=f, turns=[{"p": "Count the FIXME comments in the Python files of mon/ (only .py; the JS and YAML ones don't count). I want one number.", "inc": ["4"]}],
         truth=ctruth("sum(v for p, v in count('FIXME', inc=('mon/',), per=True).items() if p.endswith('.py'))", "4"),
         decoy="7", policy=P_BASH, ref_calls=3, refs=[("grep -rE '# *FIXME' mon --include=*.py | wc -l", "4")],
         notes=N("TR-DECOY: js/yml FIXMEs, text in log.py.", "grep --include=*.py.", "4."))


@reg
def c33():
    def js(s, mk):
        return "\n".join(spr(js_mod(["card", "deck"], s, 3).split("\n"), mk))
    f = {"ui/card.js": js(331, [(2, "// TODO: a11y"), (6, "// TODO: focus ring"), (9, "// TODO: rtl")]), "ui/deck.js": js(332, [(3, "// TODO: virtualize"), (7, "// TODO: keyboard nav")]),
         "ui/theme.js": js(333, [(4, "// TODO: tokens")]), "ui/legacy/old.js": "// TODO: delete\n// TODO: delete\n// TODO: delete\n// TODO: delete\n"}
    make("code-33533", sub="count", task_type="count_markers", desc="TODO count excluding legacy, then which file has most",
         files=f, turns=[{"p": "ui 里（不含 legacy 子目录）一共有多少条 TODO？", "inc": ["6"]},
                         {"p": "这些 TODO 里哪个文件最多？", "inc": ["ui/card.js"]}],
         truth=ctruth("count('TODO', inc=('ui/',), exc=('ui/legacy',))", "6"), decoy="10", policy=P_BASH, ref_calls=5,
         refs=[("grep -rc 'TODO' ui/card.js ui/deck.js ui/theme.js", "card.js:3")],
         notes=N("TR-DECOY: legacy dir inflates count and would win per-file.", "grep -r excluding legacy.", "6; card.js with 3."))


@reg
def c34():
    f = {"db/schema.sql": "-- TODO: add index on user_id\nCREATE TABLE users (id INT);\n-- TODO: partition\nCREATE TABLE logs (id INT);\n-- NOTE: logs are append only\n",
         "db/seed.sql": "-- TODO: realistic names\nINSERT INTO users VALUES (1);\n-- TODOS are tracked in jira\n",
         "db/migrate.lua": "-- TODO: rollback\nlocal x = 1\n-- TODO: dry run\n-- TODO: locking\n", "db/README.md": "TODO list is in schema.sql\n",
         "db/helpers.sh": "#!/usr/bin/env bash\ntodo_dir=db/todo\n"}
    make("code-33534", sub="count", task_type="count_markers", desc="Count -- style TODO comments, TODOS and NOTE are not markers",
         files=f, turns=[{"p": "db 目录里 `--` 开头的注释中，有多少条 TODO 标记？注意 TODOS（复数）那条不算，README 和变量名也不算。只回答数字。", "inc": ["6"]}],
         truth=ctruth("sum(count('TODO', inc=('db/',), per=True).values())", "6"), decoy="7", policy=P_BASH, ref_calls=3,
         refs=[("grep -rE -- '-- *TODO( |:|$)' db | wc -l", "6")],
         notes=N("TR-DECOY: TODOS, README, todo_dir.", "grep -- TODO.", "6."))


@reg
def c35():
    f = {"src/engine.ts": "/**\n * Engine core.\n * TODO: split into modules\n */\nexport class Engine {\n  /* TODO: lazy init */\n  start() {}\n  // TODO: stop()\n}\n",
         "src/pool.ts": "/*\n * TODO: reuse workers\n * FIXME: leak on abort\n */\nexport const pool = [];\n// not a marker: todo later\n",
         "src/index.ts": "export * from './engine';\nexport * from './pool';\n", "dist/engine.js": "// TODO: generated copy\n// TODO: generated copy 2\n",
         "docs/dev.md": "- TODO: finish docs\n"}
    make("code-33535", sub="count", task_type="count_markers", desc="TODO markers inside block comments and line comments, dist excluded",
         files=f, turns=[{"p": "How many TODO markers are in the TypeScript sources under src/? Block comments (/* */ and /** */) count too. dist/ is generated output and docs aren't code.", "inc": ["4"]}],
         truth=ctruth("count('TODO', inc=('src/',))", "4"), decoy="7", policy=P_BASH, ref_calls=3,
         refs=[("grep -rn 'TODO' src | wc -l", "4")],
         notes=N("TR-DECOY: dist copy, docs, lowercase todo.", "grep TODO in src.", "4."))


@reg
def c36():
    sh = lambda s, mk: "\n".join(spr(sh_mod(["unit", "rollup"], s, 3).split("\n"), mk))
    f = {"ops/backup.sh": sh(361, [(4, "# TODO: verify checksums"), (8, "# FIXME: s3 timeout")]), "ops/rotate.sh": sh(362, [(5, "# FIXME: keep 7 not 5"), (9, "# TODO: compress")]),
         "ops/inventory.yml": "# TODO: add hosts\nhosts: []\n# FIXME: stale entries\n", "ops/old/backup.sh": "# TODO: dead\n# FIXME: dead\n"}
    make("code-33536", sub="count", task_type="count_markers", desc="TODO and FIXME in ops without the old directory; second turn re-asks one kind",
         files=f, turns=[{"p": "ops 目录（不算 old 子目录）里 TODO 和 FIXME 加起来有多少条？", "inc": ["6"]},
                         {"p": "其中 FIXME 占几条？", "inc": ["3"]}],
         truth="import re\nans = sum(1 for p, t in files.items() if p.startswith('ops/') and not p.startswith('ops/old') for l in t.split(chr(10)) if re.search(r'#\\s*(TODO|FIXME)\\b', l))\nassert ans == 6, ans\n",
         decoy="9", policy=P_BASH, ref_calls=5, refs=[("grep -rE '# *(TODO|FIXME)' ops/backup.sh ops/rotate.sh ops/inventory.yml | wc -l", "6")],
         notes=N("TR-DECOY: old/ directory.", "grep both; second turn FIXME only.", "6 then 3."))
