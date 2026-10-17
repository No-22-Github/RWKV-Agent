"""b21n sub 2: find_callers 33513-33524."""
import random

from common import make, L, lineno, P_SEARCH, P_BASH, P_LINES, P_READ, P_SRL, P_RWL, P_SRW
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


def callers_truth(name, want):
    return ("import re\nname = %r\ndef strip(l):\n    return re.sub(r\"(\\\"[^\\\"]*\\\"|'[^']*')\", '', l)\n"
            "out = []\nfor p, t in sorted(files.items()):\n    for l in t.split(chr(10)):\n        s = l.strip()\n"
            "        if s.startswith(('#', '//', '*', '/*')) or re.match(r'(def|func|function|export function|async function) ', s):\n            continue\n"
            "        if re.search(r'\\b' + name + r'\\(', strip(l)) and not re.match(r'(const|var|let) ', s) or re.search(r'\\b' + name + r'\\(', strip(l)) and 'return' in s:\n"
            "            out.append(p); break\nassert sorted(out) == %r, out\nans = out[0]\n" % (name, sorted(want), ))


def callers_truth(name, want):
    """callers = files with a call `name(` that is not a def line, a comment line or inside a string."""
    return ("import re\nname = %r\nout = []\nfor p, t in sorted(files.items()):\n    for l in t.split(chr(10)):\n"
            "        s = l.strip()\n        if s.startswith(('#', '//', '*', '/*')) or re.match(r'(export )?(async )?(def|func|function) ', s):\n            continue\n"
            "        s = re.sub(r\"(\\\"[^\\\"]*\\\"|'[^']*')\", '', s)\n        if re.search(r'\\b' + name + r'\\(', s):\n            out.append(p)\n            break\n"
            "assert sorted(out) == %r, out\nans = %r\n" % (name, sorted(want), want[0]))


@reg
def c13():
    f = {"billing/tax.py": "RATES = {'eu': 0.2, 'us': 0.07}\n\n\ndef apply_vat(amount, region):\n    return amount * (1 + RATES[region])\n\n\ndef apply_vat_inclusive(amount, region):\n    return amount\n",
         "billing/invoice.py": py_mod(["line", "total"], 131, "from billing.tax import apply_vat", 2) + "\n\ndef total(amount, region):\n    return apply_vat(amount, region)\n",
         "billing/refund.py": "from billing.tax import apply_vat\n\n\ndef refund(amount, region):\n    # apply_vat() is not applied twice on refunds\n    return -apply_vat(amount, region)\n",
         "billing/quote.py": py_mod(["quote", "item"], 132, None, 3) + "\n\ndef quote(amount, region):\n    # TODO: call apply_vat(amount, region) once the rates table is final\n    return amount\n",
         "billing/report.py": "from billing.tax import apply_vat_inclusive\n\n\ndef report(a, r):\n    return apply_vat_inclusive(a, r)\n",
         "tests/test_tax.py": "def test_doc():\n    assert 'apply_vat(100, \"eu\")' == 'apply_vat(100, \"eu\")'\n"}
    want = ["billing/invoice.py", "billing/refund.py"]
    make("code-33513", sub="callers", task_type="find_callers", desc="Callers of apply_vat; a comment, a string and a longer name are not calls",
         files=f, turns=[{"p": "哪些文件真正调用了 apply_vat？只要实际的调用，注释、字符串里提到的和名字更长的 apply_vat_inclusive 都不算。只回答文件路径，一行一个。",
                          "inc": want, "exc": ["billing/quote.py", "billing/report.py", "tests/test_tax.py"]}],
         truth=callers_truth("apply_vat", want), decoy="billing/quote.py", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SEARCH, ref_calls=4, refs=[("grep -rn 'apply_vat(' billing", "invoice.py")],
         notes=N("TR-NEARNAME: apply_vat_inclusive; TR-DECOY: comment/string.", "grep apply_vat(; filter.", "invoice.py and refund.py only."))


@reg
def c14():
    f = {"lib/clock.js": "export function nowIso() {\n  return new Date().toISOString();\n}\n\nexport function nowEpoch() {\n  return Date.now();\n}\n",
         "lib/logger.js": "import { nowIso } from './clock.js';\n\nexport function log(msg) {\n  console.log(`${nowIso()} ${msg}`);\n}\n",
         "lib/audit.js": "import { nowIso } from './clock.js';\n\nexport const stamp = () => ({ at: nowIso() });\n",
         "lib/cache.js": "import { nowEpoch } from './clock.js';\n\nexport function fresh(entry) {\n  return nowEpoch() - entry.t < 5000;\n}\n",
         "lib/docs.js": "// nowIso() returns UTC\nexport const HELP = 'call nowIso() for a timestamp';\n",
         "test/clock.test.js": "import { nowIso } from '../lib/clock.js';\nconsole.assert(nowIso().endsWith('Z'));\n"}
    want = ["lib/logger.js", "lib/audit.js"]
    make("code-33514", sub="callers", task_type="find_callers", desc="Callers of nowIso excluding the test; then migrate the callers",
         files=f, ops=[("sub", "lib/logger.js", "nowIso", "nowUtc") if False else ("sub", "lib/logger.js", "import { nowIso } from './clock.js';", "import { nowUtc } from './clock.js';"),
                       ("sub", "lib/logger.js", "${nowIso()}", "${nowUtc()}"),
                       ("sub", "lib/audit.js", "import { nowIso } from './clock.js';", "import { nowUtc } from './clock.js';"),
                       ("sub", "lib/audit.js", "at: nowIso()", "at: nowUtc()"),
                       ("sub", "lib/clock.js", "export function nowIso() {", "export function nowUtc() {")],
         turns=[{"p": "Which library files call nowIso()? Leave the test out; I only care about lib/ code that really calls it.", "inc": want},
                {"p": "Rename nowIso to nowUtc: the definition and the two callers you found. Don't touch cache.js, docs.js or the test file.", "inc": ["nowUtc"]}],
         truth="ans = 'x'\n", decoy="lib/docs.js", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SRL, ref_calls=8, refs=[("grep -rn 'nowIso(' lib", "logger.js")],
         notes=N("TR-NEARNAME: nowEpoch; TR-DECOY: docs.js and the test.", "grep nowIso(; rename in 3 files.", "logger.js and audit.js call it; the test and docs stay as they were."))


@reg
def c15():
    f = {"internal/auth/token.go": "package auth\n\nfunc ParseToken(raw string) (string, error) {\n\treturn raw, nil\n}\n\nfunc ParseTokenLoose(raw string) string {\n\treturn raw\n}\n",
         "internal/http/middleware.go": "package http\n\nimport \"example.com/gw/internal/auth\"\n\nfunc Guard(h string) error {\n\t_, err := auth.ParseToken(h)\n\treturn err\n}\n",
         "internal/ws/upgrade.go": "package ws\n\nimport \"example.com/gw/internal/auth\"\n\nfunc Upgrade(q string) bool {\n\tt, err := auth.ParseToken(q)\n\treturn err == nil && t != \"\"\n}\n",
         "internal/cli/debug.go": "package cli\n\nimport \"example.com/gw/internal/auth\"\n\n// debug uses auth.ParseToken(x) only in the docs below\nfunc Debug(x string) string {\n\treturn auth.ParseTokenLoose(x)\n}\n",
         "internal/auth/token_test.go": "package auth\n\nimport \"testing\"\n\nfunc TestParse(t *testing.T) {\n\t_, _ = ParseToken(\"x\")\n}\n",
         "cmd/gw/main.go": "package main\n\nfunc main() {}\n"}
    want = ["internal/http/middleware.go", "internal/ws/upgrade.go", "internal/auth/token_test.go"]
    make("code-33515", sub="callers", task_type="find_callers", desc="Go callers of ParseToken including the test file",
         files=f, turns=[{"p": "ParseToken 在哪些文件里被调用？测试文件也要算，ParseTokenLoose 不算。只写文件路径，一行一个。",
                          "inc": want, "exc": ["internal/cli/debug.go"]}],
         truth=callers_truth("ParseToken", want), decoy="internal/cli/debug.go", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_BASH, ref_calls=4, refs=[("grep -rn 'ParseToken(' .", "middleware.go")],
         notes=N("TR-NEARNAME: ParseTokenLoose; comment mention in debug.go.", "grep ParseToken(.", "three files incl. test."))


@reg
def c16():
    f = {"bin/lib/common.sh": "#!/usr/bin/env bash\nnotify_slack() {\n  echo \"slack: $1\"\n}\n\nnotify_mail() {\n  echo \"mail: $1\"\n}\n",
         "bin/nightly.sh": "#!/usr/bin/env bash\nsource bin/lib/common.sh\nnotify_slack \"nightly done\"\n",
         "bin/deploy.sh": "#!/usr/bin/env bash\nsource bin/lib/common.sh\n# notify_slack is noisy at night\nnotify_mail \"deploy start\"\n",
         "bin/cleanup.sh": "#!/usr/bin/env bash\nsource bin/lib/common.sh\nif [ -n \"$X\" ]; then notify_slack \"cleanup $X\"; fi\n",
         "ci/pipeline.yml": "stages:\n  - build\n  - notify  # runs notify_slack via bin/nightly.sh\n",
         "README.md": "Use notify_slack for chat, notify_mail for email.\n"}
    want = ["bin/nightly.sh", "bin/cleanup.sh"]
    make("code-33516", sub="callers", task_type="find_callers", desc="Shell callers of notify_slack vs notify_mail",
         files=f, turns=[{"p": "哪些脚本在调用 notify_slack？不算定义它的文件，也不算只在注释或文档里提到的。只写路径，一行一个。",
                          "inc": want, "exc": ["bin/deploy.sh", "ci/pipeline.yml", "README.md"]}],
         truth=("out = [p for p, t in sorted(files.items()) if p.startswith('bin/') and p != 'bin/lib/common.sh' and any(l.strip().startswith('notify_slack ') or 'then notify_slack ' in l for l in t.split(chr(10)))]\nassert out == %r, out\nans = %r\n" % (sorted(want), want[0])),
         decoy="bin/deploy.sh", trap="TR-NEARNAME", extra_traps=("TR-DECOY",), policy=P_BASH, ref_calls=4,
         refs=[("grep -rn 'notify_slack' bin", "cleanup.sh")],
         notes=N("TR-NEARNAME: notify_mail; comment in deploy.sh.", "grep notify_slack.", "nightly.sh and cleanup.sh."))


@reg
def c17():
    f = {"src/format/money.ts": "export function fmtMoney(cents: number): string {\n  return (cents / 100).toFixed(2);\n}\n",
         "src/views/cart.ts": "import { fmtMoney } from '../format/money';\n\nexport const cartLine = (c: number) => `Total ${fmtMoney(c)}`;\n",
         "src/views/receipt.ts": "import { fmtMoney } from '../format/money';\n\nexport function receipt(c: number, tip: number) {\n  return [fmtMoney(c), fmtMoney(tip)].join(' + ');\n}\n",
         "src/views/header.ts": "export const title = 'fmtMoney(c) is documented in money.ts';\n",
         "src/views/admin.ts": "import * as money from '../format/money';\n// money.fmtMoney(x) used to be called here\nexport const noop = () => 0;\n",
         "src/index.ts": "export * from './views/cart';\n"}
    want = ["src/views/cart.ts", "src/views/receipt.ts"]
    make("code-33517", sub="callers", task_type="find_callers", desc="TS callers of fmtMoney, one file calls it twice",
         files=f, turns=[{"p": "Which files actually call fmtMoney? A mention in a string or a comment is not a call. Paths only, one per line.",
                          "inc": want, "exc": ["src/views/header.ts", "src/views/admin.ts"]}],
         truth=callers_truth("fmtMoney", want), decoy="src/views/header.ts", policy=P_SEARCH, ref_calls=3,
         refs=[("grep -rn 'fmtMoney(' src", "receipt.ts")],
         notes=N("TR-DECOY: string and comment mentions.", "grep fmtMoney(.", "cart.ts and receipt.ts."))


@reg
def c18():
    f = {"core/slugify.py": "import re\n\n\ndef slugify(text):\n    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')\n",
         "core/posts.py": "from core.slugify import slugify\n\n\ndef post_url(title):\n    return '/p/' + slugify(title)\n",
         "core/tags.py": "from core.slugify import slugify\n\n\ndef tag_key(name):\n    return 'tag:' + slugify(name)\n",
         "core/export.py": py_mod(["row", "col"], 181, None, 3),
         "scripts/migrate.py": "# slugify(old_title) was used here before the rewrite\nprint('done')\n",
         "tests/test_slug.py": "from core.slugify import slugify\n\n\ndef test_basic():\n    assert slugify('A b') == 'a-b'\n"}
    want = ["core/posts.py", "core/tags.py"]
    ops = [("sub", "core/posts.py", "from core.slugify import slugify", "from core.slugify import slugify as make_slug"),
           ("sub", "core/posts.py", "'/p/' + slugify(title)", "'/p/' + make_slug(title)"),
           ("sub", "core/tags.py", "from core.slugify import slugify", "from core.slugify import slugify as make_slug"),
           ("sub", "core/tags.py", "'tag:' + slugify(name)", "'tag:' + make_slug(name)")]
    make("code-33518", sub="callers", task_type="find_callers", desc="Find slugify callers in core then alias them; tests and scripts stay",
         files=f, ops=ops,
         turns=[{"p": "core 目录下哪些文件在调用 slugify？测试和 scripts 里的先不管。", "inc": want},
                {"p": "把这两个调用方改成 `from core.slugify import slugify as make_slug` 的写法，调用处也用 make_slug。测试文件别动。", "inc": ["make_slug"]}],
         truth="ans = 'x'\n", decoy="scripts/migrate.py", policy=P_SRL, ref_calls=8,
         refs=[("grep -rn 'slugify(' core", "posts.py")],
         notes=N("TR-DECOY: scripts comment, tests.", "grep slugify( in core; edit 2 files x 2 lines.", "posts.py and tags.py; tests/scripts unchanged."))


@reg
def c19():
    f = {"app/validators.py": "def check_zip(code):\n    return len(code) == 5 and code.isdigit()\n\n\ndef check_zip_plus4(code):\n    return len(code) == 10\n",
         "app/forms/signup.py": "from app.validators import check_zip\n\n\ndef signup(data):\n    if not check_zip(data['zip']):\n        raise ValueError('zip')\n",
         "app/forms/shipping.py": "from app.validators import check_zip, check_zip_plus4\n\n\ndef ship(data):\n    return check_zip(data['zip']) or check_zip_plus4(data['zip'])\n",
         "app/forms/profile.py": "from app.validators import check_zip_plus4\n\n\ndef profile(d):\n    return check_zip_plus4(d['zip'])\n",
         "app/forms/help.py": "HELP = \"We run check_zip(code) on every address form\"\n",
         "app/forms/old.py": "# def check_zip(code): moved to validators in 2024\n"}
    want = ["app/forms/signup.py", "app/forms/shipping.py"]
    make("code-33519", sub="callers", task_type="find_callers", desc="check_zip vs check_zip_plus4 callers",
         files=f, turns=[{"p": "check_zip 被哪些文件调用了？check_zip_plus4 是另一个函数，不算；字符串和注释里的也不算。只列文件路径，一行一个。",
                          "inc": want, "exc": ["app/forms/profile.py", "app/forms/help.py", "app/forms/old.py"]}],
         truth=callers_truth("check_zip", want), decoy="app/forms/profile.py", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SEARCH, ref_calls=4, refs=[("grep -rn 'check_zip(' app", "signup.py")],
         notes=N("TR-NEARNAME: check_zip_plus4.", "grep check_zip(.", "signup.py, shipping.py."))


@reg
def c20():
    f = {"src/bus.js": "const subs = [];\nexports.emit = function emit(ev) {\n  subs.forEach((s) => s(ev));\n};\nexports.on = function on(fn) {\n  subs.push(fn);\n};\n",
         "src/jobs/mail.js": "const bus = require('../bus');\n\nmodule.exports = function sendMail(job) {\n  bus.emit({ type: 'mail', job });\n};\n",
         "src/jobs/sms.js": "const { emit } = require('../bus');\n\nmodule.exports = function sendSms(job) {\n  emit({ type: 'sms', job });\n};\n",
         "src/jobs/push.js": "const bus = require('../bus');\n\nmodule.exports = function push(job) {\n  bus.on(() => 1);\n};\n",
         "src/main.js": "// emit() is called from the job modules, not from here\nrequire('./jobs/mail');\n",
         "package.json": "{\"name\": \"notifier\", \"scripts\": {\"emit\": \"node src/main.js\"}}\n"}
    want = ["src/jobs/mail.js", "src/jobs/sms.js"]
    ops = [("sub", "src/jobs/mail.js", "bus.emit({ type: 'mail', job });", "bus.emit({ type: 'mail', job, at: Date.now() });"),
           ("sub", "src/jobs/sms.js", "emit({ type: 'sms', job });", "emit({ type: 'sms', job, at: Date.now() });")]
    make("code-33520", sub="callers", task_type="find_callers", desc="emit callers (bus.emit and destructured emit), then add an at field",
         files=f, ops=ops,
         turns=[{"p": "src 里哪些文件调用了 emit（不管是 bus.emit 还是解构出来的 emit）？定义它的文件不算。", "inc": want},
                {"p": "在这些调用传的对象里都加一个字段 at: Date.now()，别的文件不要动。", "inc": ["at"]}],
         truth="ans = 'x'\n", decoy="src/main.js", policy=P_SRL, ref_calls=8,
         refs=[("grep -rn 'emit(' src", "mail.js")],
         notes=N("TR-DECOY: comment in main.js, package.json script key.", "grep emit(; edit two calls.", "mail.js and sms.js changed."))


@reg
def c21():
    f = {"pkg/retry/retry.go": "package retry\n\nfunc Do(n int, fn func() error) error {\n\tvar err error\n\tfor i := 0; i < n; i++ {\n\t\tif err = fn(); err == nil {\n\t\t\treturn nil\n\t\t}\n\t}\n\treturn err\n}\n",
         "pkg/db/conn.go": "package db\n\nimport \"example.com/svc/pkg/retry\"\n\nfunc Open() error {\n\treturn retry.Do(3, func() error { return nil })\n}\n",
         "pkg/mq/consumer.go": "package mq\n\nimport \"example.com/svc/pkg/retry\"\n\nfunc Run() error {\n\treturn retry.Do(5, func() error { return nil })\n}\n",
         "pkg/api/handler.go": "package api\n\n// retry.Do(n, fn) is intentionally not used in handlers\nfunc Handle() {}\n",
         "pkg/api/docs.go": "package api\n\nconst Doc = \"wrap flaky calls in retry.Do(3, fn)\"\n"}
    want = ["pkg/db/conn.go", "pkg/mq/consumer.go"]
    make("code-33521", sub="callers", task_type="find_callers", desc="Go retry.Do callers; comment and string mentions",
         files=f, turns=[{"p": "Who calls retry.Do in this service? List the files only, one per line. Mentions inside comments or string constants are not calls.",
                          "inc": want, "exc": ["pkg/api/handler.go", "pkg/api/docs.go"]}],
         truth=callers_truth("retry\\.Do", want), decoy="pkg/api/docs.go", policy=P_BASH, ref_calls=3,
         refs=[("grep -rn 'retry.Do(' pkg", "conn.go")],
         notes=N("TR-DECOY: comment and string.", "grep retry.Do(.", "db/conn.go, mq/consumer.go."))


@reg
def c22():
    f = {"lib/paths.sh": "#!/usr/bin/env bash\nwork_dir() {\n  echo \"${HOME}/.cache/tool\"\n}\n\nwork_dir_tmp() {\n  echo \"/tmp/tool\"\n}\n",
         "bin/start.sh": "#!/usr/bin/env bash\nsource lib/paths.sh\nmkdir -p \"$(work_dir)\"\n",
         "bin/stop.sh": "#!/usr/bin/env bash\nsource lib/paths.sh\nrm -f \"$(work_dir)/pid\"\n",
         "bin/tmpclean.sh": "#!/usr/bin/env bash\nsource lib/paths.sh\nrm -rf \"$(work_dir_tmp)\"\n",
         "docs/usage.md": "Run `bin/start.sh`; it calls $(work_dir) first.\n"}
    want = ["bin/start.sh", "bin/stop.sh"]
    ops = [("sub", "bin/start.sh", "$(work_dir)", "$(work_dir)/run"), ("sub", "bin/stop.sh", "$(work_dir)/pid", "$(work_dir)/run/pid")]
    make("code-33522", sub="callers", task_type="find_callers", desc="work_dir callers (not work_dir_tmp); move pid under run/",
         files=f, ops=ops,
         turns=[{"p": "哪些 bin 脚本调用了 work_dir？work_dir_tmp 不算。", "inc": want},
                {"p": "这两个脚本以后统一用 work_dir 下面的 run 子目录：start.sh 创建 run，stop.sh 删 run/pid。按这个改，别动 tmpclean.sh。", "inc": ["run"]}],
         truth="ans = 'x'\n", decoy="bin/tmpclean.sh", trap="TR-NEARNAME", extra_traps=("TR-DECOY",), policy=P_SRL, ref_calls=8,
         refs=[("grep -rn 'work_dir)' bin", "start.sh")],
         notes=N("TR-NEARNAME: work_dir_tmp.", "grep; two edits.", "start.sh and stop.sh change."))


@reg
def c23():
    f = {"web/api.ts": "export async function fetchUser(id: string) {\n  return { id };\n}\n\nexport async function fetchUsers() {\n  return [];\n}\n",
         "web/pages/profile.ts": "import { fetchUser } from '../api';\n\nexport async function load(id: string) {\n  return await fetchUser(id);\n}\n",
         "web/pages/team.ts": "import { fetchUsers } from '../api';\n\nexport const team = () => fetchUsers();\n",
         "web/pages/admin.ts": "import { fetchUser } from '../api';\n\nexport async function audit(ids: string[]) {\n  return Promise.all(ids.map((i) => fetchUser(i)));\n}\n",
         "web/pages/about.ts": "export const note = \"data comes from fetchUser(id)\";\n"}
    want = ["web/pages/profile.ts", "web/pages/admin.ts"]
    make("code-33523", sub="callers", task_type="find_callers", desc="fetchUser vs fetchUsers callers",
         files=f, turns=[{"p": "fetchUser（单数）被哪些页面文件调用？fetchUsers 不算。回答文件路径就行。",
                          "inc": want, "exc": ["web/pages/team.ts", "web/pages/about.ts"]},
                         {"p": "那 fetchUsers（复数）呢？", "inc": ["web/pages/team.ts"]}],
         truth=callers_truth("fetchUser", want), decoy="web/pages/team.ts", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SEARCH, ref_calls=5, refs=[("grep -rn 'fetchUser(' web", "profile.ts")],
         notes=N("TR-NEARNAME: fetchUsers (turn 2 asks for it).", "grep fetchUser(; turn 2 grep fetchUsers(.", "profile.ts, admin.ts; then team.ts."))


@reg
def c24():
    f = {"svc/units.py": "def to_kg(lb):\n    return lb * 0.4536\n\n\ndef to_lb(kg):\n    return kg / 0.4536\n",
         "svc/ship.py": py_mod(["box", "pallet"], 241, "from svc.units import to_kg", 2) + "\n\ndef weight(lb):\n    return round(to_kg(lb), 1)\n",
         "svc/label.py": "from svc.units import to_kg, to_lb\n\n\ndef label(lb):\n    return str(to_kg(lb)) + ' kg / ' + str(lb) + ' lb'\n",
         "svc/audit.py": "from svc.units import to_lb\n\n\ndef back(kg):\n    return to_lb(kg)\n",
         "CHANGELOG.md": "- 1.2: to_kg(lb) now rounds to 1 decimal in ship.py\n"}
    want = ["svc/ship.py", "svc/label.py"]
    ops = [("sub", "svc/label.py", "str(to_kg(lb))", "str(round(to_kg(lb), 1))")]
    make("code-33524", sub="callers", task_type="find_callers", desc="to_kg callers; the one that does not round gets fixed",
         files=f, ops=ops,
         turns=[{"p": "Which files call to_kg? Don't count the changelog line or to_lb.", "inc": want},
                {"p": "ship.py already rounds the result to 1 decimal. Make the other caller round the same way (round(..., 1) around the to_kg call) and leave everything else alone.", "inc": ["label.py"]}],
         truth="ans = 'x'\n", decoy="svc/audit.py", trap="TR-NEARNAME", extra_traps=("TR-DECOY",), policy=P_SRL, ref_calls=7,
         refs=[("grep -rn 'to_kg(' svc", "ship.py")],
         notes=N("TR-NEARNAME: to_lb.", "grep to_kg(; patch label.py.", "ship.py, label.py; label.py gets round()."))
