"""b21n sub 4: fix_edge_case 33537-33548 (expect.files equals; other files unchanged)."""
import random

from common import make, L, lineno, P_SEARCH, P_BASH, P_RWL, P_SRW, P_SRL, P_BW
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


def pad(lines_before, n, tag, r):
    return ["%s_%d = %d" % (tag, i, r.randint(2, 90)) for i in range(n)] + lines_before


@reg
def c37():
    r = random.Random(37)
    body = pad(["", "def is_adult(age):", "    # 18 and over counts as an adult", "    return age > 18", "", "", "def is_minor(age):", "    return age < 18", ""], 12, "LIMIT", r)
    f = {"members/rules.py": L("\"\"\"Membership rules.\"\"\"", "", *body),
         "members/signup.py": "from members.rules import is_adult\n\n\ndef allowed(age):\n    return is_adult(age)\n",
         "members/promo.py": "def senior_discount(age):\n    return age > 65\n", "members/util.py": py_mod(["member", "plan"], 371, None, 3),
         "tests/test_rules.py": "from members.rules import is_adult\n\n\ndef test_edge():\n    assert is_adult(18)\n    assert not is_adult(17)\n"}
    ln = lineno(f, "members/rules.py", "return age > 18")
    make("code-33537", sub="fix", task_type="fix_edge_case", desc="Off-by-one: 18 should count as adult",
         files=f, ops=[("sub", "members/rules.py", "    return age > 18\n", "    return age >= 18\n")],
         turns=[{"p": "刚好 18 岁的用户被当成了未成年人，注册被拒了。帮我把 members/rules.py 里的判断修好（18 岁及以上算成年），别动别的文件。改完读回来确认，告诉我改的是第几行。",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_RWL, ref_calls=4, axes=("OBS", "VER"),
         notes=N("TR-DECOY: `age > 65` and `age < 18` elsewhere.", "find is_adult; > to >=; read back.", "line %d becomes `age >= 18`." % ln))


@reg
def c38():
    f = {"lib/stats.js": "// moving averages\nexport function movingAvg(xs, k) {\n  const out = [];\n  for (let i = 0; i < xs.length - 1; i++) {\n    const w = xs.slice(Math.max(0, i - k + 1), i + 1);\n    out.push(w.reduce((a, b) => a + b, 0) / w.length);\n  }\n  return out;\n}\n\nexport function pairs(xs) {\n  const out = [];\n  for (let i = 0; i < xs.length - 1; i++) {\n    out.push([xs[i], xs[i + 1]]);\n  }\n  return out;\n}\n",
         "lib/index.js": "export * from './stats.js';\n", "lib/fmt.js": js_mod(["row", "col"], 381, 3), "test/stats.test.js": "// movingAvg([1,2,3], 2) should return 3 values\n", "package.json": "{\"name\": \"stats\", \"type\": \"module\"}\n"}
    ln = lineno(f, "lib/stats.js", "i < xs.length - 1", 1)
    make("code-33538", sub="fix", task_type="fix_edge_case", desc="movingAvg drops the last element; pairs must keep its -1",
         files=f, ops=[("sub", "lib/stats.js", "  for (let i = 0; i < xs.length - 1; i++) {\n    const w", "  for (let i = 0; i < xs.length; i++) {\n    const w")],
         turns=[{"p": "movingAvg([1,2,3], 2) returns only 2 values, but it should return one per input element. Fix it in lib/stats.js without changing pairs(), which is correct as it is. Read the code back and tell me which line you changed.",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_SRW, ref_calls=5,
         notes=N("TR-DECOY: pairs has the same loop header and must stay.", "locate movingAvg loop; drop -1; read back.", "line %d only." % ln))


@reg
def c39():
    f = {"cmd/ring/buf.go": "package ring\n\ntype Buf struct {\n\tdata []int\n\tcap  int\n}\n\nfunc New(n int) *Buf {\n\treturn &Buf{cap: n}\n}\n\n// Push keeps at most cap items.\nfunc (b *Buf) Push(x int) {\n\tif len(b.data) > b.cap {\n\t\tb.data = b.data[1:]\n\t}\n\tb.data = append(b.data, x)\n}\n\nfunc (b *Buf) Len() int {\n\treturn len(b.data)\n}\n",
         "cmd/ring/buf_test.go": "package ring\n\n// Push 4 items into New(3): Len() must be 3\nfunc TestCap() {}\n", "cmd/ring/stats.go": go_mod("ring", ["slot", "hit"], 391),
         "cmd/main.go": "package main\n\nfunc main() {}\n", "go.mod": "module example.com/ring\n\ngo 1.22\n"}
    ln = lineno(f, "cmd/ring/buf.go", "if len(b.data) > b.cap")
    make("code-33539", sub="fix", task_type="fix_edge_case", desc="Ring buffer keeps cap+1 items: > should be >=",
         files=f, ops=[("sub", "cmd/ring/buf.go", "if len(b.data) > b.cap {", "if len(b.data) >= b.cap {")],
         turns=[{"p": "往 New(3) 里塞 4 个数以后 Len() 居然是 4，应该最多 3。帮我修一下 cmd/ring/buf.go 里的 Push，只改那一个判断。改完读回确认，说一下改了第几行。",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=4,
         notes=N("TR-DECOY: only one comparison, tests mention.", "locate Push; > to >=.", "line %d." % ln))


@reg
def c40():
    f = {"bin/rotate.sh": "#!/usr/bin/env bash\n# keep at most KEEP backups\nKEEP=5\ncount=$(ls backups | wc -l)\n\nwhile [ \"$count\" -gt \"$KEEP\" ]; do\n  oldest=$(ls backups | head -n 1)\n  rm -f \"backups/$oldest\"\n  count=$((count - 1))\ndone\n",
         "bin/notify.sh": "#!/usr/bin/env bash\nif [ \"$1\" -gt 3 ]; then echo many; fi\n", "bin/lib.sh": sh_mod(["fs", "tar"], 401, 3),
         "docs/ops.md": "rotate.sh keeps at most KEEP backups.\n"}
    # intended: this version is correct; the bug is the warning threshold in notify.sh
    ln = lineno(f, "bin/notify.sh", '-gt 3')
    make("code-33540", sub="fix", task_type="fix_edge_case", desc="notify.sh should warn at 3 or more failures",
         files=f, ops=[("sub", "bin/notify.sh", '-gt 3', '-ge 3')],
         turns=[{"p": "bin/notify.sh 应该在失败次数达到 3 次（含 3 次）时就报 many，现在要 4 次才报。修一下这一处比较，别碰 rotate.sh（它的 -gt 是对的）。读回来确认并告诉我是第几行。",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=4,
         notes=N("TR-DECOY: rotate.sh has a correct -gt.", "edit notify.sh only.", "line %d: -gt 3 to -ge 3." % ln))


@reg
def c41():
    r = random.Random(41)
    body = ["export function clampPage(page: number, total: number): number {", "  if (page < 1) return 1;", "  if (page > total) return total + 1;", "  return page;", "}", "",
            "export function pageCount(items: number, size: number): number {", "  return Math.ceil(items / size);", "}", ""]
    f = {"src/paging.ts": L(*(["// paging helpers"] + ["export const SIZE_%d = %d;" % (i, r.randint(5, 50)) for i in range(10)] + [""] + body)),
         "src/list.ts": "import { clampPage } from './paging';\n\nexport const show = (p: number, t: number) => clampPage(p, t);\n",
         "src/util.ts": js_mod(["page", "row"], 411, 3, ts=True), "tests/paging.md": "clampPage(9, 5) must be 5, not 6\n"}
    ln = lineno(f, "src/paging.ts", "return total + 1")
    make("code-33541", sub="fix", task_type="fix_edge_case", desc="clampPage returns total+1 beyond the last page",
         files=f, ops=[("sub", "src/paging.ts", "return total + 1;", "return total;")],
         turns=[{"p": "Asking for a page past the end gives total + 1 instead of the last page. Fix clampPage in src/paging.ts, change only what is wrong, then read it back and tell me the line number.",
                 "inc": [str(ln)]},
                {"p": "Thanks. Does pageCount have the same kind of problem? Just tell me, don't edit.", "inc": ["pageCount"], "forb": ["write_file", "replace_lines", "append_file"]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=6,
         notes=N("TR-DECOY: pageCount is correct (Math.ceil).", "fix clampPage; turn 2 read-only judgement.", "line %d; pageCount fine." % ln))


@reg
def c42():
    f = {"report/dates.py": "from datetime import date, timedelta\n\n\ndef days_between(a, b):\n    \"\"\"Inclusive: both a and b count.\"\"\"\n    return (b - a).days\n\n\ndef week_end(d):\n    return d + timedelta(days=6)\n",
         "report/summary.py": "from report.dates import days_between\n\n\ndef span(a, b):\n    return days_between(a, b)\n", "report/util.py": py_mod(["day", "week"], 421, None, 3),
         "tests/test_dates.py": "from datetime import date\nfrom report.dates import days_between\n\n\ndef test_same_day():\n    assert days_between(date(2026, 9, 1), date(2026, 9, 1)) == 1\n"}
    ln = lineno(f, "report/dates.py", "return (b - a).days")
    make("code-33542", sub="fix", task_type="fix_edge_case", desc="Inclusive day count is off by one",
         files=f, ops=[("sub", "report/dates.py", "return (b - a).days\n", "return (b - a).days + 1\n")],
         turns=[{"p": "days_between 文档写的是两端都算，但同一天算出来是 0，测试要的是 1。把 report/dates.py 里那个函数修好，只改它的返回值那一行。读回来告诉我第几行。",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_RWL, ref_calls=4,
         notes=N("TR-DECOY: week_end's 6 is intentional.", "add + 1.", "line %d." % ln))


@reg
def c43():
    f = {"search/bsearch.py": "def find(xs, target):\n    \"\"\"Index of target in sorted xs, or -1.\"\"\"\n    lo, hi = 0, len(xs) - 1\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if xs[mid] == target:\n            return mid\n        if xs[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n",
         "search/lower.py": "def lower_bound(xs, t):\n    lo, hi = 0, len(xs)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if xs[mid] < t:\n            lo = mid + 1\n        else:\n            hi = mid\n    return lo\n",
         "search/util.py": py_mod(["key", "node"], 431, None, 3), "tests/test_find.py": "from search.bsearch import find\n\n\ndef test_single():\n    assert find([7], 7) == 0\n"}
    ln = lineno(f, "search/bsearch.py", "while lo < hi:")
    make("code-33543", sub="fix", task_type="fix_edge_case", desc="Binary search misses single-element lists; lower_bound is correct",
         files=f, ops=[("sub", "search/bsearch.py", "    while lo < hi:\n", "    while lo <= hi:\n")],
         turns=[{"p": "find([7], 7) 返回 -1，应该是 0。检查一下 search/bsearch.py 的 find，把循环条件修对（lower.py 的写法是另一种二分，是对的，不要动）。改完读回确认，告诉我改的是第几行。",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_RWL, ref_calls=4, trap="TR-DECOY", extra_traps=("TR-NEARNAME",),
         notes=N("TR-NEARNAME/DECOY: lower.py has the same loop header and is correct.", "change < to <= in find only.", "line %d." % ln))


@reg
def c44():
    f = {"lib/take.js": "// take helpers\nexport function takeFirst(xs, n) {\n  return xs.slice(0, n - 1);\n}\n\nexport function takeLast(xs, n) {\n  return xs.slice(xs.length - n);\n}\n\nexport function skip(xs, n) {\n  return xs.slice(n);\n}\n",
         "lib/use.js": "import { takeFirst } from './take.js';\n\nexport const top3 = (xs) => takeFirst(xs, 3);\n", "lib/fmt.js": js_mod(["cell", "col"], 441, 3),
         "docs/take.md": "takeFirst([1,2,3,4], 3) => [1,2,3]\n"}
    ln = lineno(f, "lib/take.js", "xs.slice(0, n - 1)")
    ops = [("sub", "lib/take.js", "xs.slice(0, n - 1)", "xs.slice(0, n)")]
    make("code-33544", sub="fix", task_type="fix_edge_case", desc="takeFirst returns n-1 items",
         files=f, ops=ops,
         turns=[{"p": "top3 只返回了 2 个元素。根因在 takeFirst，按 docs/take.md 里的例子修好它，别改其他函数。读回来确认并告诉我第几行。", "inc": [str(ln)]},
                {"p": "顺便看下 takeLast 和 skip 有没有同样的问题？只回答有没有，不要改。", "inc": [], "any": ["没有", "没问题", "正确", "不存在", "无问题", "都对", "not affected", "no problem", "fine", "correct"], "forb": ["write_file", "replace_lines", "append_file"]}],
         truth="ans = 'x'\n", policy=P_SRW, ref_calls=6,
         notes=N("TR-DECOY: takeLast/skip use slice but are right.", "fix takeFirst; turn 2 read-only judgement.", "line %d; others fine." % ln))


@reg
def c45():
    f = {"internal/pad/pad.go": "package pad\n\n// Cells returns every index of s.\nfunc Cells(s string) []int {\n\tvar out []int\n\tfor i := 0; i <= len(s); i++ {\n\t\tout = append(out, i)\n\t}\n\treturn out\n}\n\n// Last returns the final byte.\nfunc Last(s string) byte {\n\treturn s[len(s)-1]\n}\n",
         "internal/pad/pad_test.go": "package pad\n\n// Cells(\"ab\") must be [0 1]\n", "internal/render/r.go": go_mod("render", ["cell", "row"], 451), "main.go": "package main\n\nfunc main() {}\n"}
    ln = lineno(f, "internal/pad/pad.go", "i <= len(s)")
    make("code-33545", sub="fix", task_type="fix_edge_case", desc="Go loop runs one past the end",
         files=f, ops=[("sub", "internal/pad/pad.go", "i <= len(s)", "i < len(s)")],
         turns=[{"p": "Cells(\"ab\") returns three indexes and a caller panics on the last one. Fix the loop bound in internal/pad/pad.go, leave Last alone, then read the file back and tell me which line you changed.",
                 "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=4,
         notes=N("TR-DECOY: Last uses len(s)-1 legitimately.", "<= to <.", "line %d." % ln))


@reg
def c46():
    f = {"scripts/range.py": "def evens_upto(n):\n    \"\"\"Even numbers from 2 up to and including n.\"\"\"\n    return [i for i in range(2, n) if i % 2 == 0]\n\n\ndef squares(n):\n    return [i * i for i in range(1, n + 1)]\n",
         "scripts/main.py": "from scripts.range import evens_upto, squares\n\nprint(evens_upto(10), squares(3))\n", "scripts/util.py": py_mod(["num", "seq"], 461, None, 3), "README.md": "evens_upto(10) -> [2, 4, 6, 8, 10]\n"}
    ln = lineno(f, "scripts/range.py", "range(2, n)")
    make("code-33546", sub="fix", task_type="fix_edge_case", desc="evens_upto excludes n; squares is right",
         files=f, ops=[("sub", "scripts/range.py", "range(2, n) if", "range(2, n + 1) if")],
         turns=[{"p": "evens_upto(10) 少了 10。README 里写的结果才是对的。修一下 scripts/range.py，squares 那个函数没问题别动。改完读回确认，告诉我是第几行。",
                 "inc": [str(ln)]},
                {"p": "main.py 里的输出现在应该是什么？", "inc": ["[2, 4, 6, 8, 10]"], "forb": ["write_file", "replace_lines", "append_file"]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=6,
         notes=N("TR-DECOY: squares range(1, n + 1).", "n -> n + 1 in evens_upto; turn 2 read.", "line %d." % ln))


@reg
def c47():
    f = {"deploy/gate.sh": "#!/usr/bin/env bash\n# block the deploy when coverage is below the floor\nFLOOR=80\ncov=\"$1\"\n\nif [ \"$cov\" -lt \"$FLOOR\" ]; then\n  echo block\n  exit 1\nfi\necho ok\n",
         "deploy/warn.sh": "#!/usr/bin/env bash\ncov=\"$1\"\nif [ \"$cov\" -lt 90 ]; then echo warn; fi\n", "deploy/lib.sh": sh_mod(["gate", "tag"], 471, 3),
         "docs/gate.md": "Coverage of exactly 80 passes; 79 blocks.\n"}
    # gate.sh is correct (-lt 80 blocks 79 only). Bug is in warn.sh? Make bug explicit in gate: change to -le to show the opposite? keep: bug is that exactly 80 blocks -> use -le
    f["deploy/gate.sh"] = f["deploy/gate.sh"].replace('-lt "$FLOOR"', '-le "$FLOOR"')
    ln = lineno(f, "deploy/gate.sh", '-le "$FLOOR"')
    make("code-33547", sub="fix", task_type="fix_edge_case", desc="Gate blocks exactly-at-floor coverage",
         files=f, ops=[("sub", "deploy/gate.sh", '-le "$FLOOR"', '-lt "$FLOOR"')],
         turns=[{"p": "覆盖率刚好 80 的时候 gate.sh 也被拦下了，按 docs/gate.md 的说法 80 应该能过。修一下 deploy/gate.sh，只改那个比较。读回来确认，告诉我第几行。", "inc": [str(ln)]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=4,
         notes=N("TR-DECOY: warn.sh has a correct -lt 90.", "-le to -lt.", "line %d." % ln))


@reg
def c48():
    f = {"app/retry.ts": "export function shouldRetry(attempt: number, max: number): boolean {\n  return attempt > max;\n}\n\nexport function backoff(attempt: number): number {\n  return 2 ** attempt * 100;\n}\n",
         "app/client.ts": "import { shouldRetry, backoff } from './retry';\n\nexport async function call(fn: () => Promise<void>, max = 3) {\n  for (let a = 0; ; a++) {\n    try { return await fn(); } catch (e) {\n      if (!shouldRetry(a, max)) throw e;\n      await new Promise((r) => setTimeout(r, backoff(a)));\n    }\n  }\n}\n",
         "app/util.ts": js_mod(["call", "wait"], 481, 3, ts=True), "docs/retry.md": "max=3 means at most 3 retries; shouldRetry(2, 3) is true, shouldRetry(3, 3) is false.\n"}
    ln = lineno(f, "app/retry.ts", "return attempt > max")
    ops = [("sub", "app/retry.ts", "return attempt > max;", "return attempt < max;")]
    make("code-33548", sub="fix", task_type="fix_edge_case", desc="shouldRetry has the comparison reversed; then document",
         files=f, ops=ops,
         turns=[{"p": "重试逻辑好像反了：失败一次就不重试了。按 docs/retry.md 的说明修一下 app/retry.ts 里的判断，别动 backoff。改完读回确认并告诉我是第几行。", "inc": [str(ln)]},
                {"p": "client.ts 里调用它的地方需要跟着改吗？", "inc": [], "any": ["不需要", "不用", "无需", "不必", "没必要", "no change", "not need", "no need", "doesn't need", "does not need", "don't need"], "forb": ["write_file", "replace_lines", "append_file"]}],
         truth="ans = 'x'\n", policy=P_SRL, ref_calls=6,
         notes=N("TR-DECOY: caller negates it correctly.", "flip > to <; T2 read-only.", "line %d." % ln))
