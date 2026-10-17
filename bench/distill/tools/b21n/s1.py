"""b21n sub 1: locate_definition 33501-33512."""
import random

from common import make, L, lineno, P_SEARCH, P_BASH, P_LINES, P_READ, P_SRL
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def loc_truth(pat, line):
    return ("import re\nhits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match(%r, l)]\n"
            "assert len(hits) == 1, hits\nans = hits[0][0]\nassert hits[0][1] == %d\n" % (pat, line))


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


def fill(r, names, template, n):
    return [template % (r.choice(names) + "_%d" % i, r.randint(2, 99)) for i in range(n)]


@reg
def c01():
    r = random.Random(1)
    lim = ["# upload limits for the media service", "", "import os", ""]
    lim += fill(r, ["AVATAR_MAX_PX", "THUMB_QUALITY", "CHUNK_KB", "ALBUM_CAP"], "%s = %d", 9)
    lim += ["", "MAX_UPLOAD_BYTES = 52428800", "MAX_UPLOAD_BYTES_ANON = 5242880", ""]
    lim += fill(r, ["RETRY_BASE", "QUEUE_SLOTS"], "%s = %d", 4)
    f = {"media/config/limits.py": L(*lim),
         "media/uploads.py": py_mod(["upload", "chunk"], 11, "from media.config.limits import MAX_UPLOAD_BYTES", 3) + "\n\ndef too_big(n):\n    return n > MAX_UPLOAD_BYTES\n",
         "media/api.py": py_mod(["route", "token"], 12, None, 3),
         "tests/test_limits.py": "# sanity: MAX_UPLOAD_BYTES = 1024 is only used in the fake config below\nFAKE = {'MAX_UPLOAD_BYTES': 1024}\n\n\ndef test_fake():\n    assert FAKE['MAX_UPLOAD_BYTES'] == 1024\n",
         "media/config/legacy.py": "MAX_UPLOAD_BYTES_LEGACY = 10485760\n"}
    ln = lineno(f, "media/config/limits.py", "MAX_UPLOAD_BYTES = ")
    make("code-33501", sub="locate", task_type="locate_definition", desc="Locate the MAX_UPLOAD_BYTES definition among similar names and a test mention",
         files=f, turns=[{"p": "项目里的 MAX_UPLOAD_BYTES 是在哪个文件里定义的？第几行？值是多少？注意别和名字相近的常量搞混。",
                          "inc": ["media/config/limits.py", str(ln), "52428800"]}],
         truth=loc_truth(r"^MAX_UPLOAD_BYTES\s*=", ln), decoy="media/config/legacy.py", trap="TR-NEARNAME",
         extra_traps=("TR-DECOY",), policy=P_SEARCH, ref_calls=3,
         refs=[("grep -rn 'MAX_UPLOAD_BYTES ' media | head", "limits.py:%d" % ln)],
         notes=N("TR-NEARNAME: MAX_UPLOAD_BYTES_ANON and _LEGACY; TR-DECOY: test comment and import.", "grep MAX_UPLOAD_BYTES; pick the assignment line.", "Only limits.py has `MAX_UPLOAD_BYTES =`; line %d." % ln))


@reg
def c02():
    r = random.Random(2)
    rows = ["// shared knobs for the playlist worker", "", "export const defaults = {", "  shuffle: true,", "  crossfadeMs: 1200,", "};", ""]
    rows += ["export const LABEL_%d = 'plist-%d';" % (i, r.randint(10, 99)) for i in range(8)]
    rows += ["", "export const FADE_STEP_MS = 40;", "export const FADE_STEP_MS_FAST = 15;", ""]
    rows += ["export const SLOT_%d = %d;" % (i, r.randint(2, 40)) for i in range(5)]
    f = {"src/settings.js": L(*rows),
         "src/player.js": "import { FADE_STEP_MS } from './settings.js';\n\n// FADE_STEP_MS = 40 comes from settings\nexport function fadeOut(el) {\n  el.volume -= FADE_STEP_MS / 1000;\n}\n" + js_mod(["track", "queue"], 21, 2),
         "src/queue.js": js_mod(["song", "list"], 22, 3),
         "docs/notes.md": "# notes\nThe fade step (FADE_STEP_MS) is tuned in settings.js.\n",
         "src/legacy-settings.js": "export const FADE_STEP_MS = 100; // old value, file is no longer imported\n"}
    ln = lineno(f, "src/settings.js", "export const FADE_STEP_MS = ")
    # legacy file defines the same name: tell the user which file the player imports
    make("code-33502", sub="locate", task_type="locate_definition", desc="Which of two files defining FADE_STEP_MS the player actually imports",
         files=f, turns=[{"p": "player.js 用到的 FADE_STEP_MS 是从哪个文件来的？告诉我文件和它所在的行号。（项目里不止一个地方写了这个名字。）",
                          "inc": ["src/settings.js", str(ln)]},
                         {"p": "那 FADE_STEP_MS_FAST 呢？它在同一个文件的第几行？", "inc": [str(ln + 1)]}],
         truth=("import re\nm = re.search(r\"from '\\./([\\w-]+\\.js)'\", files['src/player.js'])\nans = 'src/' + m.group(1)\nassert files[ans].split(chr(10))[%d].startswith('export const FADE_STEP_MS = ')\n" % (ln - 1)),
         decoy="src/legacy-settings.js", trap="TR-MULTISRC", extra_traps=("TR-NEARNAME",), policy=P_SEARCH, ref_calls=5,
         refs=[("grep -n 'FADE_STEP_MS' src/*.js", "settings.js:%d" % ln)],
         notes=N("TR-MULTISRC: legacy-settings.js defines the same name but is not imported; TR-NEARNAME: _FAST.", "read player.js import; grep in settings.js; turn 2 is the next line.", "settings.js line %d; FAST is line %d." % (ln, ln + 1)))


@reg
def c03():
    r = random.Random(3)
    rows = ["package limits", "", "import \"time\"", "", "// Defaults for the sync daemon.", "const ("]
    rows += ["\tBatchSize%d = %d" % (i, r.randint(10, 500)) for i in range(7)]
    rows += ["\tSyncInterval = 45 * time.Second", "\tSyncIntervalJitter = 5 * time.Second", ")", ""]
    f = {"internal/limits/limits.go": L(*rows),
         "internal/sync/run.go": "package sync\n\nimport \"example.com/hub/internal/limits\"\n\n// SyncInterval is read once at start.\nfunc Tick() int64 {\n\treturn int64(limits.SyncInterval)\n}\n",
         "internal/sync/util.go": go_mod("sync", ["peer", "blob"], 31),
         "cmd/hubd/main.go": "package main\n\nfunc main() {\n\t// SyncInterval = 45s by default\n}\n",
         "config/hubd.yaml": yaml_conf(["peer", "blob", "ring"], 32, 4)}
    ln = lineno(f, "internal/limits/limits.go", "SyncInterval = ")
    make("code-33503", sub="locate", task_type="locate_definition", desc="Go const block: SyncInterval vs SyncIntervalJitter",
         files=f, turns=[{"p": "Which file defines SyncInterval in this Go repo, and on which line? Don't give me the SyncIntervalJitter line.",
                          "inc": ["internal/limits/limits.go", str(ln)]}],
         truth=loc_truth(r"^\tSyncInterval\s*=", ln), decoy=str(ln + 1), trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_BASH, ref_calls=3, refs=[("grep -rn 'SyncInterval =' internal", "limits.go:%d" % ln)],
         notes=N("TR-NEARNAME: SyncIntervalJitter right below; TR-DECOY: comments in run.go/main.go.", "grep SyncInterval; choose the const line.", "line %d in limits.go." % ln))


@reg
def c04():
    r = random.Random(4)
    rows = ["#!/usr/bin/env bash", "# deploy helper", "set -euo pipefail", ""]
    rows += ["export ZONE_%s=%s" % (z, r.choice(["a", "b", "c"])) for z in ["EU", "US", "AP", "SA"]]
    rows += ["", "BACKUP_KEEP_DAYS=14", "BACKUP_KEEP_COUNT=30", ""]
    f = {"scripts/env.sh": L(*rows),
         "scripts/backup.sh": sh_mod(["dump", "ship"], 41) + "\n# retention: BACKUP_KEEP_DAYS (see env.sh)\nfind /var/bk -mtime +\"$BACKUP_KEEP_DAYS\" -delete\n",
         "scripts/restore.sh": sh_mod(["fetch", "unpack"], 42, 2),
         "ops/crontab.yml": yaml_conf(["nightly", "weekly"], 43, 3) + "# BACKUP_KEEP_DAYS is set in env.sh, not here\n",
         "README.md": "# ops\nSet BACKUP_KEEP_DAYS before the nightly run.\n"}
    ln = lineno(f, "scripts/env.sh", "BACKUP_KEEP_DAYS=")
    make("code-33504", sub="locate", task_type="locate_definition", desc="Shell variable BACKUP_KEEP_DAYS assignment line",
         files=f, turns=[{"p": "备份脚本保留几天的备份？这个值 BACKUP_KEEP_DAYS 是在哪个文件的第几行设置的？",
                          "inc": ["scripts/env.sh", str(ln), "14"]}],
         truth=loc_truth(r"^BACKUP_KEEP_DAYS=", ln), decoy="scripts/backup.sh", policy=P_SEARCH, ref_calls=3,
         refs=[("grep -rn '^BACKUP_KEEP_DAYS=' .", "env.sh:%d" % ln)],
         notes=N("TR-DECOY: other files mention the name.", "grep ^BACKUP_KEEP_DAYS=.", "env.sh line %d, value 14." % ln))


@reg
def c05():
    r = random.Random(5)
    rows = ["// request guards", "import { Request } from './types';", ""]
    rows += ["export function guard%s(req: Request): boolean {\n  return !!req.%s;\n}\n" % (n.capitalize(), n) for n in ["user", "org", "scope"]]
    rows += ["export function isRateLimited(req: Request): boolean {", "  return req.hits > 100;", "}", ""]
    rows += ["export function isRateLimitedBurst(req: Request): boolean {", "  return req.burst > 20;", "}", ""]
    f = {"src/guards.ts": L(*rows),
         "src/types.ts": "export interface Request {\n  user?: string;\n  org?: string;\n  scope?: string;\n  hits: number;\n  burst: number;\n}\n",
         "src/server.ts": "import { isRateLimited } from './guards';\n\n// isRateLimited decides on 429\nexport function handle(req: any) {\n  if (isRateLimited(req)) return 429;\n  return 200;\n}\n",
         "src/util.ts": js_mod(["row", "col"], 51, 3, ts=True),
         "test/guards.test.ts": "// describe('isRateLimited', ...) — pending\nexport {};\n"}
    ln = lineno(f, "src/guards.ts", "export function isRateLimited(")
    make("code-33505", sub="locate", task_type="locate_definition", desc="TS function isRateLimited vs isRateLimitedBurst",
         files=f, turns=[{"p": "函数 isRateLimited 的定义在哪个文件、第几行？（isRateLimitedBurst 是另一个函数，别搞混。）",
                          "inc": ["src/guards.ts", str(ln)]},
                         {"p": "它判断限流的阈值是多少？", "inc": ["100"]}],
         truth=loc_truth(r"^export function isRateLimited\(", ln), decoy=str(ln + 4), trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SEARCH, ref_calls=4, refs=[("grep -rn 'function isRateLimited(' src", "guards.ts:%d" % ln)],
         notes=N("TR-NEARNAME: isRateLimitedBurst.", "grep; read the 2-line body for the threshold.", "guards.ts line %d; threshold 100." % ln))


@reg
def c06():
    r = random.Random(6)
    rows = ["\"\"\"Retry helpers for the exporter.\"\"\"", "import time", ""]
    rows += ["BACKOFF_%d = %d" % (i, r.randint(1, 30)) for i in range(11)]
    rows += ["", "class RetryPolicy:", "    attempts = 3", "", "    def wait(self, n):", "        return 2 ** n", ""]
    rows += ["", "class RetryPolicyStrict(RetryPolicy):", "    attempts = 1", ""]
    f = {"exporter/retry.py": L(*rows),
         "exporter/run.py": "from exporter.retry import RetryPolicy\n\n# RetryPolicy is shared with the importer\ndef go():\n    return RetryPolicy().wait(2)\n",
         "exporter/csvout.py": py_mod(["col", "row"], 61, None, 4),
         "importer/retry.py": "class RetryPolicyImporter:\n    attempts = 5\n",
         "tests/test_retry.py": "# class RetryPolicy: see exporter/retry.py\n"}
    ln = lineno(f, "exporter/retry.py", "class RetryPolicy:")
    make("code-33506", sub="locate", task_type="locate_definition", desc="Python class RetryPolicy vs subclass and importer variant",
         files=f, turns=[{"p": "Where is the class RetryPolicy defined (file and line number)? The exporter uses it.",
                          "inc": ["exporter/retry.py", str(ln)]},
                         {"p": "And how many attempts does it allow by default?", "inc": ["3"]}],
         truth=loc_truth(r"^class RetryPolicy:", ln), decoy="importer/retry.py", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_BASH, ref_calls=4, refs=[("grep -rn 'class RetryPolicy:' .", "retry.py:%d" % ln)],
         notes=N("TR-NEARNAME: RetryPolicyStrict, RetryPolicyImporter.", "grep class RetryPolicy:.", "exporter/retry.py line %d; attempts 3." % ln))


@reg
def c07():
    f = {"deploy/staging.yaml": "name: staging\nreplicas: 2\nregion: eu-west\nresources:\n  cpu: 500m\n  memory: 512Mi\nautoscale:\n  min: 2\n  max: 6\n  timeout_seconds: 30\nprobes:\n  readiness:\n    path: /ready\n    timeout_seconds: 5\n  liveness:\n    path: /live\n    timeout_seconds: 10\nlabels:\n  tier: web\n",
         "deploy/prod.yaml": "name: prod\nreplicas: 6\nregion: eu-west\nresources:\n  cpu: 2000m\n  memory: 2Gi\nautoscale:\n  min: 6\n  max: 24\n  timeout_seconds: 60\nprobes:\n  readiness:\n    path: /ready\n    timeout_seconds: 8\n  liveness:\n    path: /live\n    timeout_seconds: 15\n",
         "deploy/README.md": "# deploy\nprod.yaml: liveness timeout_seconds is 15; staging is shorter.\n",
         "scripts/render.sh": sh_mod(["tpl", "diff"], 71, 2),
         "scripts/check.py": py_mod(["probe", "pod"], 72, None, 3)}
    ln = lineno(f, "deploy/prod.yaml", "timeout_seconds", 3)
    make("code-33507", sub="locate", task_type="locate_definition", desc="YAML key repeated: liveness timeout line in prod.yaml",
         files=f, turns=[{"p": "prod 环境的 liveness 探针超时是在 deploy 目录哪个文件的第几行？值是多少？staging 的不用管。",
                          "inc": ["deploy/prod.yaml", str(ln), "15"]}],
         truth=("lines = files['deploy/prod.yaml'].split(chr(10))\nidx = [i for i, l in enumerate(lines, 1) if 'timeout_seconds' in l]\nans = 'deploy/prod.yaml'\nassert idx[2] == %d and lines[idx[2]-1].strip() == 'timeout_seconds: 15'\n" % ln),
         decoy="deploy/staging.yaml", policy=P_LINES, ref_calls=3, refs=[("grep -n timeout_seconds deploy/prod.yaml", "%d:" % ln)],
         notes=N("TR-DECOY: timeout_seconds appears three times in prod.yaml and in staging.", "grep -n; pick the one under liveness.", "prod.yaml line %d value 15." % ln))


@reg
def c08():
    r = random.Random(8)
    rows = ["// text helpers for the importer", ""]
    rows += ["const %s_PAD = %d;" % (n, r.randint(2, 50)) for n in ["LEFT", "RIGHT", "TOP", "GAP"]]
    rows += ["", "// EMAIL_RE = /^\\S+@\\S+$/ (the old loose one, removed in v2)", "const EMAIL_RE = /^[\\w.+-]+@[\\w-]+\\.[\\w.]+$/;", "const EMAIL_RE_LOOSE = /@/;", ""]
    rows += ["module.exports = { EMAIL_RE };"]
    f = {"lib/patterns.js": L(*rows), "lib/validate.js": "const { EMAIL_RE } = require('./patterns');\n\nfunction ok(s) {\n  return EMAIL_RE.test(s);\n}\nmodule.exports = { ok };\n",
         "lib/format.js": js_mod(["cell", "row"], 81, 3), "test/validate.test.js": "// EMAIL_RE is defined in patterns.js\n", "bin/import.js": "const { ok } = require('../lib/validate');\n"}
    ln = lineno(f, "lib/patterns.js", "const EMAIL_RE = ")
    make("code-33508", sub="locate", task_type="locate_definition", desc="Regex constant EMAIL_RE with a commented older version",
         files=f, turns=[{"p": "邮箱校验用的正则 EMAIL_RE 真正生效的定义在哪个文件第几行？文件里还有一行注释写了旧版本，别选那个。",
                          "inc": ["lib/patterns.js", str(ln)]}],
         truth=loc_truth(r"^const EMAIL_RE\s*=", ln), decoy=str(ln - 1), trap="TR-DECOY", extra_traps=(), policy=P_SEARCH, ref_calls=3,
         refs=[("grep -n 'const EMAIL_RE =' lib/patterns.js", "%d:" % ln)],
         notes=N("TR-DECOY: comment holds an old assignment; EMAIL_RE_LOOSE.", "grep EMAIL_RE; pick the const line.", "patterns.js line %d." % ln))


@reg
def c09():
    r = random.Random(9)
    rows = ["package cache", "", "import \"errors\"", "", "var ErrMiss = errors.New(\"cache miss\")", ""]
    for n in ["Get", "Put", "Drop"]:
        rows += ["func (c *Cache) %s(k string) error {" % n, "\treturn nil", "}", ""]
    rows += ["// Evict removes the oldest entry.", "func (c *Cache) Evict() {", "\t// TODO: ring buffer", "}", "", "func (c *Cache) EvictAll() {", "}", ""]
    f = {"pkg/cache/cache.go": L(*rows), "pkg/cache/cache_test.go": "package cache\n\n// TestEvict covers Evict() and EvictAll()\nfunc TestEvict() {}\n",
         "pkg/store/store.go": go_mod("store", ["row", "key"], 91), "main.go": "package main\n\nfunc main() {}\n", "go.mod": "module example.com/kv\n\ngo 1.22\n"}
    ln = lineno(f, "pkg/cache/cache.go", "func (c *Cache) Evict()")
    make("code-33509", sub="locate", task_type="locate_definition", desc="Go method Evict vs EvictAll",
         files=f, turns=[{"p": "Cache 的 Evict 方法写在哪个文件？第几行？（EvictAll 是另一个方法。）",
                          "inc": ["pkg/cache/cache.go", str(ln)]},
                         {"p": "EvictAll 呢，是第几行？", "inc": [str(ln + 4)]}],
         truth=loc_truth(r"^func \(c \*Cache\) Evict\(\)", ln), decoy=str(ln + 4), trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SEARCH, ref_calls=4, refs=[("grep -n 'Evict' pkg/cache/cache.go", "%d:" % ln)],
         notes=N("TR-NEARNAME: EvictAll; TR-DECOY: comments/test.", "grep Evict; T2 next definition.", "cache.go line %d, EvictAll %d." % (ln, ln + 4)))


@reg
def c10():
    f = {"tools/lib.sh": "#!/usr/bin/env bash\n# helpers\n\nsay() {\n  printf '%s\\n' \"$*\"\n}\n\ndie() {\n  say \"fatal: $*\" >&2\n  exit 1\n}\n\nrequire_cmd() {\n  command -v \"$1\" >/dev/null || die \"missing $1\"\n}\n\nretry() {\n  local n=0\n  until \"$@\"; do\n    n=$((n+1)); [ \"$n\" -ge 3 ] && return 1\n    sleep 1\n  done\n}\n",
         "tools/release.sh": "#!/usr/bin/env bash\nsource tools/lib.sh\n# uses retry() from lib.sh\nrequire_cmd git\nretry git fetch\n",
         "tools/old/lib.sh": "retry() { \"$@\"; }\n", "tools/notes.txt": "retry() was copied to tools/old once; do not use that copy.\n",
         "Makefile": "release:\n\tbash tools/release.sh\n"}
    ln = lineno(f, "tools/lib.sh", "retry() {")
    make("code-33510", sub="locate", task_type="locate_definition", desc="Shell function retry defined twice, one is the live copy",
         files=f, turns=[{"p": "release.sh 调用的 retry 函数是在哪个文件的第几行定义的？仓库里有两个同名函数，要选实际被 source 进来的那个。",
                          "inc": ["tools/lib.sh", str(ln)]}],
         truth=("import re\nsrc = re.search(r'source (\\S+)', files['tools/release.sh']).group(1)\nlines = files[src].split(chr(10))\nidx = [i for i, l in enumerate(lines, 1) if l.startswith('retry()')]\nans = src\nassert idx == [%d]\n" % ln),
         decoy="tools/old/lib.sh", trap="TR-MULTISRC", extra_traps=("TR-DECOY",), policy=P_BASH, ref_calls=4,
         refs=[("grep -rn 'retry()' tools", "lib.sh:%d:" % ln)],
         notes=N("TR-MULTISRC: tools/old/lib.sh has another retry().", "read release.sh to see which lib is sourced; grep.", "tools/lib.sh line %d." % ln))


@reg
def c11():
    r = random.Random(11)
    rows = ["\"\"\"Pricing constants.\"\"\"", ""]
    rows += ["%s = %d" % (n, r.randint(2, 90)) for n in ["BASE_FEE", "LATE_FEE", "MIN_ORDER", "SHIP_CAP", "COUPON_CAP", "TIER_STEP", "TAX_DIGITS"]]
    rows += ["", "FREE_SHIPPING_FROM = 80", "FREE_SHIPPING_FROM_PRIME = 40", ""]
    f = {"shop/pricing.py": L(*rows), "shop/cart.py": "from shop.pricing import FREE_SHIPPING_FROM\n\n\ndef shipping(total):\n    return 0 if total >= FREE_SHIPPING_FROM else 6\n",
         "shop/util.py": py_mod(["cart", "line"], 111, None, 3), "docs/pricing.md": "Free shipping starts at 80 (FREE_SHIPPING_FROM).\n"}
    ln = lineno(f, "shop/pricing.py", "FREE_SHIPPING_FROM = ")
    make("code-33511", sub="locate", task_type="locate_definition", desc="Locate then change a constant, siblings untouched",
         files=f, ops=[("sub", "shop/pricing.py", "FREE_SHIPPING_FROM = 80\n", "FREE_SHIPPING_FROM = 100\n")],
         turns=[{"p": "FREE_SHIPPING_FROM 在哪个文件第几行定义的？", "inc": ["shop/pricing.py", str(ln)]},
                {"p": "好，把它改成 100，其他同名前缀的常量别动，改完读一下确认。", "inc": ["100"]}],
         truth="ans = 'shop/pricing.py'\n", decoy="shop/cart.py", trap="TR-NEARNAME", extra_traps=("TR-DECOY",),
         policy=P_SRL, ref_calls=6, refs=[("grep -n 'FREE_SHIPPING_FROM = ' shop/pricing.py", "%d:" % ln)],
         notes=N("TR-NEARNAME: FREE_SHIPPING_FROM_PRIME.", "locate then edit that one line.", "pricing.py line %d; becomes 100." % ln))


@reg
def c12():
    rows = ["// order status codes", "export enum Status {", "  Draft = 0,", "  Paid = 1,", "  Shipped = 2,", "  Delivered = 3,", "  Cancelled = 9,", "}", "",
            "export enum RefundStatus {", "  None = 0,", "  Pending = 1,", "  Cancelled = 7,", "  Done = 8,", "}", ""]
    f = {"src/status.ts": L(*rows), "src/order.ts": "import { Status } from './status';\n\nexport function canCancel(s: Status) {\n  return s === Status.Draft || s === Status.Paid;\n}\n// Status.Cancelled is set by the admin tool\n",
         "src/refund.ts": "import { RefundStatus } from './status';\nexport const done = RefundStatus.Done;\n", "src/util.ts": js_mod(["order", "line"], 121, 3, ts=True),
         "README.md": "Status.Cancelled = 9\n"}
    ln = lineno(f, "src/status.ts", "Cancelled = 9")
    make("code-33512", sub="locate", task_type="locate_definition", desc="Enum member Cancelled exists in two enums",
         files=f, turns=[{"p": "The order Status enum has a Cancelled member. Which file and line is it on, and what number does it equal? There is another enum with the same member name, that one does not count.",
                          "inc": ["src/status.ts", str(ln), "9"]}],
         truth=("lines = files['src/status.ts'].split(chr(10))\nidx = [i for i, l in enumerate(lines, 1) if 'Cancelled = 9' in l]\nans = 'src/status.ts'\nassert idx == [%d]\n" % ln),
         decoy=str(ln + 6), trap="TR-NEARNAME", extra_traps=("TR-DECOY",), policy=P_SEARCH, ref_calls=3,
         refs=[("grep -n Cancelled src/status.ts", "%d:" % ln)],
         notes=N("TR-NEARNAME: RefundStatus.Cancelled = 7.", "grep Cancelled; choose under enum Status.", "status.ts line %d value 9." % ln))
