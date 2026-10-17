"""b21n sub 5: explain_readonly 33549-33559 (no write tools; every file unchanged)."""
import random

from common import make, L, lineno, P_RO, P_RO2, P_READ, P_SEARCH
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


def pyexec(expr, files_used, want):
    """truth: exec the listed python fixture files in one namespace, evaluate expr."""
    return ("ns = {}\nfor p in %r:\n    exec(files[p].replace('from ship.rates import *', ''), ns)\nans = str(eval(%r, ns))\nassert str(ans) == %r, ans\n" % (files_used, expr, want))


@reg
def c49():
    f = {"ship/rates.py": "BASE = 4.0\nPER_KG = 1.5\nFREE_ABOVE = 200\nHEAVY_KG = 20\nHEAVY_SURCHARGE = 12.0\n",
         "ship/fee.py": "from ship.rates import *\n\n\ndef shipping_fee(weight_kg, order_total):\n    if order_total >= FREE_ABOVE:\n        return 0.0\n    fee = BASE + PER_KG * weight_kg\n    if weight_kg > HEAVY_KG:\n        fee += HEAVY_SURCHARGE\n    return round(fee, 2)\n",
         "ship/util.py": py_mod(["box", "zone"], 491, None, 3), "tests/test_fee.py": "# shipping_fee(1, 10) == 5.5\n", "README.md": "Shipping is cheap for light parcels.\n"}
    make("code-33549", sub="explain", task_type="explain_readonly", desc="Explain shipping_fee and compute one case",
         files=f, turns=[{"p": "帮我看懂 ship/fee.py 里的 shipping_fee 是怎么算运费的（规则里用到的数值在别的文件里）。然后告诉我 8 公斤、订单金额 120 的运费是多少。只是解释，不要改任何文件。",
                          "inc": ["16"]}],
         truth=pyexec("int(shipping_fee(8, 120))", ["ship/rates.py", "ship/fee.py"], "16"),
         readonly=True, decoy="0", policy=P_RO, ref_calls=3, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY: explain only; constants live in rates.py.", "read both files; 4.0 + 1.5*8.", "16.0."))


@reg
def c50():
    f = {"lib/chunk.js": "// split xs into groups of n\nexport function chunk(xs, n) {\n  const out = [];\n  for (let i = 0; i < xs.length; i += n) {\n    out.push(xs.slice(i, i + n));\n  }\n  return out;\n}\n",
         "lib/flat.js": "export const flat = (xss) => xss.reduce((a, b) => a.concat(b), []);\n", "lib/fmt.js": js_mod(["row", "grp"], 501, 3),
         "lib/index.js": "export * from './chunk.js';\nexport * from './flat.js';\n"}
    make("code-33550", sub="explain", task_type="explain_readonly", desc="Explain chunk and give the size of the last group",
         files=f, turns=[{"p": "Explain what chunk() in lib/chunk.js does. Then tell me how many items the last group has for chunk([1,2,3,4,5,6,7], 3). Please don't edit anything.",
                          "inc": ["1"]}],
         truth="xs = list(range(1, 8))\nn = 3\nans = len([xs[i:i + n] for i in range(0, len(xs), n)][-1])\nassert ans == 1\nans = str(ans)\n",
         readonly=True, decoy="3", policy=P_RO, ref_calls=2, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read chunk.js.", "7 items by 3 leaves [7]; 1 item."))


@reg
def c51():
    f = {"internal/collatz/collatz.go": "package collatz\n\n// Steps counts how many moves it takes to reach 1.\nfunc Steps(n int) int {\n\tsteps := 0\n\tfor n != 1 {\n\t\tif n%2 == 0 {\n\t\t\tn /= 2\n\t\t} else {\n\t\t\tn = 3*n + 1\n\t\t}\n\t\tsteps++\n\t}\n\treturn steps\n}\n",
         "internal/collatz/doc.go": "// Package collatz explores the 3n+1 problem.\npackage collatz\n", "cmd/show/main.go": "package main\n\nfunc main() {}\n", "go.mod": "module example.com/c\n\ngo 1.22\n"}
    make("code-33551", sub="explain", task_type="explain_readonly", desc="Collatz Steps explained, value for 6",
         files=f, turns=[{"p": "internal/collatz 里的 Steps 函数在干什么？如果传 6 进去会返回几？不要改文件。", "inc": ["8"]}],
         truth="n = 6\ns = 0\nwhile n != 1:\n    n = n // 2 if n % 2 == 0 else 3 * n + 1\n    s += 1\nans = str(s)\nassert ans == '8'\n",
         readonly=True, decoy="6", policy=P_RO, ref_calls=2, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read collatz.go; trace 6.", "6 3 10 5 16 8 4 2 1 = 8 steps."))


@reg
def c52():
    f = {"bin/check.sh": "#!/usr/bin/env bash\n# usage: check.sh FILE...\nmissing=0\nfor f in \"$@\"; do\n  if [ ! -e \"$f\" ]; then\n    echo \"missing: $f\"\n    missing=$((missing + 1))\n  fi\ndone\nexit \"$missing\"\n",
         "bin/lib.sh": sh_mod(["file", "path"], 521, 3), "data/a.txt": "a\n", "data/b.txt": "b\n", "README.md": "check.sh a.txt b.txt\n"}
    make("code-33552", sub="explain", task_type="explain_readonly", desc="Exit code of check.sh with 4 args of which 3 are absent",
         files=f, turns=[{"p": "What does bin/check.sh do, and what exit code would it return if I ran `bin/check.sh data/a.txt data/x.txt data/y.txt data/z.txt` from the repo root? Only explain, don't run or change anything.",
                          "inc": ["3"]}],
         truth="args = ['data/a.txt', 'data/x.txt', 'data/y.txt', 'data/z.txt']\nex = {'data/a.txt', 'data/b.txt'}\nans = str(sum(1 for a in args if a not in ex))\nassert ans == '3'\n",
         readonly=True, decoy="4", policy=P_RO, ref_calls=3, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY: explain only.", "read check.sh; list data.", "3 missing -> exit 3."))


@reg
def c53():
    f = {"src/group.ts": "export function groupBy<T>(xs: T[], key: (x: T) => string): Record<string, T[]> {\n  const out: Record<string, T[]> = {};\n  for (const x of xs) {\n    const k = key(x);\n    (out[k] ||= []).push(x);\n  }\n  return out;\n}\n",
         "src/users.ts": "import { groupBy } from './group';\n\nexport const users = [\n  { name: 'ana', team: 'red' },\n  { name: 'bo', team: 'blue' },\n  { name: 'cy', team: 'red' },\n  { name: 'di', team: 'green' },\n  { name: 'ed', team: 'red' },\n];\n\nexport const byTeam = groupBy(users, (u) => u.team);\n",
         "src/util.ts": js_mod(["user", "team"], 531, 3, ts=True)}
    make("code-33553", sub="explain", task_type="explain_readonly", desc="groupBy explained; red team size",
         files=f, turns=[{"p": "src/users.ts 里的 byTeam 最后长什么样？red 这一组有几个人？顺便讲讲 groupBy 是怎么工作的。别改任何文件。", "inc": ["3"]}],
         truth="teams = ['red', 'blue', 'red', 'green', 'red']\nans = str(teams.count('red'))\nassert ans == '3'\n",
         readonly=True, decoy="5", policy=P_RO, ref_calls=3, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read both files.", "red has 3."))


@reg
def c54():
    f = {"contacts/phone.py": "import re\n\n\ndef normalize(raw):\n    digits = re.sub(r\"\\D\", \"\", raw)\n    if digits.startswith(\"00\"):\n        digits = digits[2:]\n    return \"+\" + digits\n",
         "contacts/book.py": py_mod(["entry", "name"], 541, "from contacts.phone import normalize", 3), "tests/test_phone.py": "# normalize('00 44 20 7946 0000') == '+442079460000'\n"}
    make("code-33554", sub="explain", task_type="explain_readonly", desc="Phone normalize explained, value for a formatted number",
         files=f, turns=[{"p": "contacts/phone.py 里的 normalize 做了什么？如果输入 `0044 (20) 7946-0011`，返回的字符串是什么？只解释，不要动文件。", "inc": ["+442079460011"]}],
         truth=pyexec("normalize('0044 (20) 7946-0011')", ["contacts/phone.py"], "+442079460011").replace("exec(files[p].replace('from ship.rates import *', ''), ns)", "exec(files[p], ns)"),
         readonly=True, decoy="0044", policy=P_RO, ref_calls=2, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read phone.py.", "+442079460011."))


@reg
def c55():
    f = {".ci/pipeline.yml": "jobs:\n  lint:\n    on: [push, pull_request]\n    run: ./bin/lint.sh\n  test:\n    on: [push, pull_request]\n    needs: lint\n    run: ./bin/test.sh\n  release:\n    on: [tag]\n    needs: test\n    run: ./bin/release.sh\n  docs:\n    on: [tag]\n    run: ./bin/docs.sh\n",
         "bin/lint.sh": sh_mod(["lint"], 551, 2), "bin/test.sh": sh_mod(["test"], 552, 2), "bin/release.sh": sh_mod(["rel"], 553, 2), "bin/docs.sh": sh_mod(["doc"], 554, 2)}
    make("code-33555", sub="explain", task_type="explain_readonly", desc="Read a CI pipeline: what runs on a tag push",
         files=f, turns=[{"p": "Looking at .ci/pipeline.yml: if I push a tag, which jobs run, and in what order do the dependent ones go? Don't edit the file.",
                          "inc": ["release", "docs"]}],
         truth="ans = 'release'\nassert 'on: [tag]' in files['.ci/pipeline.yml']\n", readonly=True, decoy="lint", policy=P_RO, ref_calls=2,
         trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read pipeline.", "release (after test) and docs on tag."))


@reg
def c56():
    f = {"limiter/bucket.js": "// token bucket: refills 2 tokens per second, holds at most 5\nconst CAP = 5;\nconst RATE = 2;\n\nexport function makeBucket() {\n  return { tokens: CAP, last: 0 };\n}\n\nexport function allow(b, nowSec) {\n  b.tokens = Math.min(CAP, b.tokens + (nowSec - b.last) * RATE);\n  b.last = nowSec;\n  if (b.tokens >= 1) {\n    b.tokens -= 1;\n    return true;\n  }\n  return false;\n}\n",
         "limiter/use.js": "import { makeBucket, allow } from './bucket.js';\n\nexport const b = makeBucket();\nexport const ok = (t) => allow(b, t);\n", "limiter/util.js": js_mod(["slot", "tick"], 561, 3)}
    make("code-33556", sub="explain", task_type="explain_readonly", desc="Token bucket: after a burst of 7 requests at t=0 how many pass",
         files=f, turns=[{"p": "limiter/bucket.js 是在做什么？如果在第 0 秒连续发 7 个请求，会放行几个？只解释，别改文件。", "inc": ["5"]},
                         {"p": "那再等 1 秒（第 1 秒）连发 4 个，放行几个？", "inc": ["2"]}],
         truth="tokens, ok = 5, 0\nfor _ in range(7):\n    if tokens >= 1:\n        tokens -= 1\n        ok += 1\nfirst = ok\ntokens = min(5, tokens + 2)\nok = 0\nfor _ in range(4):\n    if tokens >= 1:\n        tokens -= 1\n        ok += 1\nassert first == 5 and ok == 2, (first, ok)\nans = str(first)\n",
         readonly=True, decoy="7", policy=P_RO, ref_calls=3, trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read bucket.js; simulate.", "5 pass; next second 2 refilled tokens -> 2."))


@reg
def c57():
    f = {"text/dedupe.py": "def dedupe_sorted(xs):\n    \"\"\"Unique values, ascending.\"\"\"\n    seen = set()\n    for x in xs:\n        seen.add(x)\n    return sorted(seen)\n",
         "text/count.py": "def tally(xs):\n    out = {}\n    for x in xs:\n        out[x] = out.get(x, 0) + 1\n    return out\n", "text/util.py": py_mod(["word", "line"], 571, None, 3),
         "tests/test_text.py": "# dedupe_sorted([3, 1, 2, 3]) -> [1, 2, 3]\n"}
    make("code-33557", sub="explain", task_type="explain_readonly", desc="dedupe_sorted vs tally explained, result for a list",
         files=f, turns=[{"p": "text/dedupe.py 里的 dedupe_sorted 是干什么的？传入 [5, 3, 5, 1, 3] 会得到什么？别改东西。", "inc": ["[1, 3, 5]"]},
                         {"p": "text/count.py 的 tally 对同一个列表又会返回什么？", "inc": ["5"], "any": ["2"]}],
         truth=pyexec("dedupe_sorted([5, 3, 5, 1, 3])", ["text/dedupe.py"], "[1, 3, 5]").replace("exec(files[p].replace('from ship.rates import *', ''), ns)", "exec(files[p], ns)"),
         readonly=True, decoy="[5, 3, 1]", policy=P_RO, ref_calls=3, trap="TR-READONLY", extra_traps=("TR-NEARNAME",),
         notes=N("TR-READONLY; TR-NEARNAME: tally vs dedupe.", "read both; trace.", "[1, 3, 5]; tally {5: 2, 3: 2, 1: 1}."))


@reg
def c58():
    f = {"strutil/pad.go": "package strutil\n\n// Pad right-pads s with '*' up to width w; longer strings are returned unchanged.\nfunc Pad(s string, w int) string {\n\tfor len(s) < w {\n\t\ts += \"*\"\n\t}\n\treturn s\n}\n\n// Trunc cuts s to at most n bytes.\nfunc Trunc(s string, n int) string {\n\tif len(s) <= n {\n\t\treturn s\n\t}\n\treturn s[:n]\n}\n",
         "strutil/doc.go": "package strutil\n", "cmd/demo/main.go": "package main\n\nfunc main() {}\n", "go.mod": "module example.com/s\n\ngo 1.22\n"}
    make("code-33558", sub="explain", task_type="explain_readonly", desc="Pad and Trunc results for given inputs",
         files=f, turns=[{"p": "What do Pad and Trunc in strutil/pad.go do? What does Pad(\"ab\", 5) return, and what does Trunc(\"abcdef\", 4) return? Just reading, no edits please.",
                          "inc": ["ab***", "abcd"]}],
         truth="s = 'ab'\nwhile len(s) < 5:\n    s += '*'\nans = s\nassert ans == 'ab***' and 'abcdef'[:4] == 'abcd'\n",
         readonly=True, decoy="ab", policy=P_RO, ref_calls=2, trap="TR-READONLY", extra_traps=("TR-NEARNAME",),
         notes=N("TR-READONLY.", "read pad.go.", "ab*** and abcd."))


@reg
def c59():
    f = {"tools/sync.sh": "#!/usr/bin/env bash\n# mirror SRC into DEST, then prune files that no longer exist in SRC\nSRC=\"$1\"; DEST=\"$2\"\nrsync -a --delete \"$SRC/\" \"$DEST/\"\nrsync_status=$?\nif [ \"$rsync_status\" -ne 0 ]; then\n  echo \"sync failed ($rsync_status)\" >&2\n  exit 2\nfi\necho \"synced\"\n",
         "tools/README.md": "sync.sh SRC DEST — destructive for DEST.\n", "tools/lib.sh": sh_mod(["mirror", "prune"], 591, 3), "Makefile": "sync:\n\tbash tools/sync.sh src backup\n"}
    make("code-33559", sub="explain", task_type="explain_readonly", desc="Explain a destructive sync script and its exit code on failure",
         files=f, turns=[{"p": "tools/sync.sh 是做什么的？它会不会删除目标目录里的文件？只读文件解释，不要运行也不要改。", "inc": [], "any": ["删除", "delete", "--delete", "清除", "移除", "remove", "prune"]},
                         {"p": "如果 rsync 本身失败了，脚本最后退出码是多少？", "inc": ["2"]}],
         truth="ans = '2'\nassert 'exit 2' in files['tools/sync.sh']\n", readonly=True, decoy="1", policy=P_RO, ref_calls=3,
         trap="TR-READONLY", extra_traps=("TR-DECOY",),
         notes=N("TR-READONLY.", "read sync.sh.", "--delete prunes DEST; failure exits 2."))
