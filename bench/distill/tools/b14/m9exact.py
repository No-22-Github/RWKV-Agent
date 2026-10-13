"""b14 M9g: precise-match commands, ids 10067-10090.

The bashprobe miss was commands that run but match too much: substring grep
where a whole word was meant, regex metacharacters in a literal, an unanchored
pattern, an extension glob that also catches .log.gz or ~$ lock files. Each
case has a decoy that only the loose command picks up, and the answer is one
count. Tree cases (file counts by extension) hold 150-320 files in nested
folders, so listing them by hand is not an option; line cases reuse aggcore.
"""
from random import Random

from aggcore import Q, agg_case
from common import case, lines, verify_src

BUILDERS = []


def tree_case(cid, *, root, readme, gen, turns, desc, family, loose, loose_note, task_type="count_by_type", seed):
    """turns: (rule, prompt, cmd, reply) with rule a Python expression over p
    (the file path). loose is the rule a sloppy glob would apply."""
    for attempt in range(500):
        rng = Random(seed * 31 + attempt)
        files = gen(rng)
        paths = sorted(files)
        vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule, *_ in turns]
        dec = sum(1 for p in paths if eval(loose, {"p": p}))
        if len(set(vals)) == len(vals) and dec != vals[-1] and min(vals) >= 6 and 150 <= len(paths) <= 340:
            break
    else:
        raise SystemExit(cid + ": no seed")
    readme_path = root + "/" + readme[0]
    files[readme_path] = lines(readme[1:])
    rules = [t[0] for t in turns]
    body = '''
README = %r
RULES = %r
assert case["files"][README].startswith(%r)
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
''' % (readme_path, rules, readme[1])
    notes = "## Traps\n- TR-DECOY: %s gives %d; the README's rule gives %d.\n" % (loose_note, dec, vals[-1])
    notes += "- %d files in nested folders under %s/, so counting by listing is not practical.\n" % (len(paths), root)
    notes += "\n## Reference solution\n"
    for i, (rule, prompt, cmd, reply) in enumerate(turns, 1):
        notes += "%s bash: `%s` -> %d\n" % ("Turn %d:" % i if len(turns) > 1 else "1.", cmd, vals[i - 1])
    notes += "Final answer: %s\n" % turns[-1][3].format(v=vals[-1])
    notes += "\n## Why the answer is unique\nThe README fixes which names count; matching by that rule over the whole tree gives one number.\n"
    tl = [{"prompt": prompt, "expect": {"output_contains": [str(v)], "output_contains_token": True, "max_output_chars": 600}}
          for (rule, prompt, cmd, reply), v in zip(turns, vals)]
    from common import REFS
    path = case(cid, sub="M9g", spec={"kind": "bash_aggregate", "needs": [readme_path]}, desc=desc, task_type=task_type,
                family=family, ref_calls=len(turns), files=files, turns=tl, verify=verify_src(files, body), notes=notes,
                traps=["TR-DECOY"], decoys={"TR-DECOY": str(dec)}, axes=("OBS", "CON"))
    REFS[cid] = (files, [t[2] for t in turns], [str(v) for v in vals])
    return path


def spread(rng, dirs, names, exts, n):
    out = {}
    while len(out) < n:
        d = rng.choice(dirs)
        name = "%s%s" % (rng.choice(names), rng.randint(1, 999))
        ext = rng.choices([e for e, _ in exts], [w for _, w in exts])[0]
        out["%s/%s%s" % (d, name, ext)] = "%s\n" % ext.strip(".")[:6]
    return out


def reg(fn):
    BUILDERS.append(fn)
    return fn


# ------------------------------------------------------------------ extension / name counts


@reg
def fs_10067():
    dirs = ["var/log/app", "var/log/app/archive", "var/log/nginx", "var/log/worker", "var/log/worker/2026-09", "var/spool", "var/tmp"]
    return tree_case(
        "fs-10067", root="var", seed=10067,
        readme=["README.md", "# var layout", "Live logs end in .log. Rotated logs are compressed to .log.gz or kept as .log.1, .log.2;",
                "those are history, not live logs. *.log.lock files are writer locks."],
        gen=lambda rng: spread(rng, dirs, ["api", "auth", "cron", "access", "error", "queue"],
                               [(".log", 6), (".log.gz", 5), (".log.1", 2), (".log.lock", 1), (".txt", 1), (".json", 1)], rng.randint(180, 260)),
        turns=[('p.endswith(".log")', "How many live log files are there under var/, subfolders included?",
                "find var -type f -name '*.log' | wc -l", "There are {v} live .log files under var/ (rotated .log.gz/.log.N and .lock files excluded).")],
        loose='".log" in p', loose_note="matching '*.log*' (rotations and locks too)",
        desc="Counts live .log files in a nested tree full of rotated and lock look-alikes", family="fam-fs-b14-livelogs-01")


@reg
def fs_10068():
    dirs = ["相册/2026/春游", "相册/2026/春游/.thumbs", "相册/2026/毕业", "相册/2026/毕业/.thumbs", "相册/2025/年会", "相册/2025/年会/.thumbs", "相册/杂项"]
    return tree_case(
        "fs-10068", root="相册", seed=10068,
        readme=["说明.txt", "相册整理规则", "照片算 .jpg 和 .jpeg，扩展名大小写都有（.JPG 也是照片）。",
                ".thumbs 目录是缩略图缓存，不算照片；.jpg.bak 是备份，也不算。"],
        gen=lambda rng: spread(rng, dirs, ["IMG_", "DSC", "合影", "风景"],
                               [(".jpg", 5), (".JPG", 3), (".jpeg", 2), (".JPEG", 1), (".jpg.bak", 1), (".png", 2), (".mov", 1)], rng.randint(200, 300)),
        turns=[('p.lower().endswith((".jpg", ".jpeg")) and "/.thumbs/" not in p', "相册里一共有多少张照片？按说明里的规则数。",
                "find 相册 -type f \\( -iname '*.jpg' -o -iname '*.jpeg' \\) -not -path '*/.thumbs/*' | wc -l",
                "按说明的口径一共 {v} 张照片（.jpg/.jpeg 不分大小写，缩略图和 .bak 不算）。")],
        loose='p.endswith(".jpg")', loose_note="a case-sensitive '*.jpg' glob (misses .JPG/.jpeg, counts thumbnails)",
        desc="Counts photos by extension case-insensitively while skipping a thumbnail cache and backups", family="fam-fs-b14-photocount-01")


@reg
def fs_10069():
    dirs = ["dist/releases", "dist/releases/old", "dist/nightly", "dist/nightly/2026-09", "dist/src"]
    return tree_case(
        "fs-10069", root="dist", seed=10069,
        readme=["NOTES.md", "# dist/", "Release tarballs are .tar.gz or .tgz (same format, two spellings).",
                "Bare .gz files are compressed changelogs and checksums, not tarballs."],
        gen=lambda rng: spread(rng, dirs, ["ledgerd-", "agent-", "cli-"],
                               [(".tar.gz", 5), (".tgz", 3), (".gz", 3), (".tar.gz.sha256", 2), (".zip", 1)], rng.randint(160, 230)),
        turns=[('p.endswith((".tar.gz", ".tgz"))', "I need the number of .tar.gz/.tgz archives we ship from dist/, nested folders included. What is it?",
                "find dist -type f \\( -name '*.tar.gz' -o -name '*.tgz' \\) | wc -l", "{v} tarballs (.tar.gz plus .tgz; plain .gz and .sha256 files excluded).")],
        loose='p.endswith(".gz")', loose_note="globbing '*.gz' (bare .gz files counted, .tgz missed)",
        desc="Counts tarballs under two extensions while bare .gz files share the suffix", family="fam-fs-b14-tarballs-01")


@reg
def fs_10070():
    dirs = ["文档/产品", "文档/产品/需求", "文档/技术", "文档/技术/设计", "文档/运营", "文档/归档"]

    def gen(rng):
        files = spread(rng, dirs, ["方案", "周报", "复盘", "接口"], [(".md", 6), (".md.bak", 2), (".markdown", 1), (".docx", 2), (".txt", 1)], rng.randint(170, 250))
        for d in dirs:
            files[d + "/README.md"] = "目录说明\n"
        return files
    return tree_case(
        "fs-10070", root="文档", seed=10070,
        readme=["统计口径.md", "# 文档统计口径", "正文文档只算 .md 结尾的文件；每个目录的 README.md 是目录说明，不算正文。",
                ".md.bak 是编辑器备份，也不算。"],
        gen=gen,
        turns=[('p.endswith(".md") and not p.endswith("/README.md") and not p.endswith("统计口径.md")', "文档 目录下有多少篇正文文档？",
                "find 文档 -type f -name '*.md' ! -name 'README.md' ! -name '统计口径.md' | wc -l",
                "正文文档共 {v} 篇（不含各目录 README.md 和 .md.bak）。")],
        loose='p.endswith(".md") and not p.endswith("统计口径.md")', loose_note="counting every *.md including the folder READMEs",
        desc="Counts markdown documents while excluding per-folder README files and editor backups", family="fam-fs-b14-mddocs-01")


@reg
def fs_10071():
    svcs = ["services/%s" % s for s in ["billing", "search", "auth", "notify", "media", "report", "gateway", "export", "audit", "geo",
                                         "billing/worker", "search/indexer", "media/transcode", "report/pdf"]]

    def gen(rng):
        files = {}
        for d in svcs:
            for name in rng.sample([".env", ".env.example", ".env.local", "env.sample", ".envrc", "config.yaml", "Dockerfile", "main.go", "go.mod"], rng.randint(4, 8)):
                files["%s/%s" % (d, name)] = "x=1\n"
            for i in range(rng.randint(6, 14)):
                files["%s/pkg/f%d.go" % (d, i)] = "package pkg\n"
        return files
    return tree_case(
        "fs-10071", root="services", seed=10071,
        readme=["SECRETS.md", "# Secrets", "Real secrets live only in files named exactly .env.",
                ".env.example, .env.local, .envrc and env.sample are templates or tooling, not secrets."],
        gen=gen,
        turns=[('p.rsplit("/", 1)[-1] == ".env"', "How many real secret files are checked in under services/?",
                "find services -type f -name .env | wc -l", "{v} files named exactly .env (templates and .envrc excluded).")],
        loose='p.rsplit("/", 1)[-1].startswith(".env")', loose_note="matching '.env*'",
        desc="Counts files named exactly .env across services while templates share the prefix", family="fam-fs-b14-envfiles-01")


@reg
def fs_10072():
    dirs = ["数据/销售", "数据/销售/区域", "数据/库存", "数据/财务", "数据/财务/月报", "数据/临时"]
    return tree_case(
        "fs-10072", root="数据", seed=10072,
        readme=["说明.md", "# 数据目录", "表格导出统一是 .csv；.csv.tmp 是导出中途的临时文件，.tsv 是旧系统格式，都不算 CSV。"],
        gen=lambda rng: {**{p: "a,b\n" for p in spread(rng, dirs, ["销售_2025_", "销售_2026_", "库存_2026_", "月报_2025_", "汇总_"],
                                                        [(".csv", 6), (".csv.tmp", 2), (".tsv", 2), (".xlsx", 1)], rng.randint(170, 240))}},
        turns=[('p.endswith(".csv")', "数据 目录下一共有多少个 CSV 文件？", "find 数据 -type f -name '*.csv' | wc -l", "{v} 个。"),
               ('p.endswith(".csv") and "2025" in p.rsplit("/", 1)[-1]', "其中文件名里带 2025 的有几个？",
                "find 数据 -type f -name '*2025*.csv' | wc -l", "文件名带 2025 的 CSV 有 {v} 个。")],
        loose='".csv" in p and "2025" in p.rsplit("/", 1)[-1]', loose_note="matching '*.csv*' (temp files counted)",
        desc="Two turns: counts CSV exports in a tree with temp-file look-alikes, then those from one year", family="fam-fs-b14-csvyear-01")


@reg
def fs_10073():
    dirs = ["src/app", "src/app/api", "src/app/tests", "src/lib", "src/lib/tests", "src/tools", "src/tests"]

    def gen(rng):
        out = {}
        while len(out) < rng.randint(170, 240):
            d = rng.choice(dirs)
            stem = rng.choice(["test_", "", "", "conftest", "helpers_"]) + rng.choice(["orders", "users", "cache", "auth", "export"]) + str(rng.randint(1, 99))
            ext = rng.choices([".py", ".pyc", ".pyi", ".txt"], [8, 2, 1, 1])[0]
            out["%s/%s%s" % (d, stem, ext)] = "pass\n"
        return out
    return tree_case(
        "fs-10073", root="src", seed=10073,
        readme=["CONTRIBUTING.md", "# Layout", "Source modules are .py files outside any tests/ folder.",
                "Test modules are test_*.py files; .pyc and .pyi files are build or stub artefacts."],
        gen=gen,
        turns=[('p.endswith(".py") and "/tests/" not in p', "How many source modules are there in src/, not counting anything inside tests folders?",
                "find src -type f -name '*.py' -not -path '*/tests/*' | wc -l", "{v}."),
               ('p.endswith(".py") and p.rsplit("/", 1)[-1].startswith("test_")', "And how many test modules (test_*.py) in total?",
                "find src -type f -name 'test_*.py' | wc -l", "{v} test modules.")],
        loose='"test_" in p', loose_note="matching 'test_*' (.pyc and .txt counted)",
        desc="Two turns: counts Python modules outside tests folders, then test modules by name pattern", family="fam-fs-b14-pymodules-01")


@reg
def fs_10074():
    dirs = ["报表/2026", "报表/2026/季度", "报表/2025", "报表/共享", "报表/共享/草稿"]

    def gen(rng):
        out = {}
        while len(out) < rng.randint(160, 230):
            d = rng.choice(dirs)
            name = rng.choice(["销售", "成本", "人力", "预算"]) + str(rng.randint(1, 300))
            kind = rng.choices(["x", "lock", "old", "csv"], [6, 2, 1, 1])[0]
            name = {"x": name + ".xlsx", "lock": "~$" + name + ".xlsx", "old": name + ".xls", "csv": name + ".csv"}[kind]
            out["%s/%s" % (d, name)] = "PK\n"
        return out
    return tree_case(
        "fs-10074", root="报表", seed=10074,
        readme=["说明.md", "# 报表目录", "正式报表是 .xlsx 文件。", "以 ~$ 开头的是 Excel 打开时留下的锁文件，不是报表；.xls 是老格式，已停用，不算。"],
        gen=gen,
        turns=[('p.endswith(".xlsx") and not p.rsplit("/", 1)[-1].startswith("~$")', "报表 目录里一共有多少份正式报表？",
                "find 报表 -type f -name '*.xlsx' ! -name '~$*' | wc -l", "正式报表 {v} 份（~$ 锁文件和 .xls 不算）。")],
        loose='p.endswith(".xlsx")', loose_note="globbing '*.xlsx' (lock files counted)",
        desc="Counts spreadsheet reports while excluding Excel lock files that share the extension", family="fam-fs-b14-xlsxlock-01")


# ------------------------------------------------------------------ whole word / literal / anchored / exact id

LINE = {"fmt": "re", "pattern": r"(?P<line>.*)", "template": "{line}", "header": False}


def line_world(root, files, rows, gen, readme_name, readme, task_type="count_events", unique="The README defines the match; one pattern gives one count."):
    w = dict(LINE, root=root, files=files, rows=rows, gen=lambda rng, fi, i: {"line": gen(rng, fi, i)},
             readme_name=readme_name, readme=readme, task_type=task_type, unique=unique, needs_readme=True)
    w["cols"] = None
    return w


def ts(rng, fi):
    return "2026-09-%02dT%02d:%02d:%02dZ" % (fi + 10, rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59))


W_TIMEOUT = line_world(
    "logs/gateway", ["gw-2026-09-%02d.log" % d for d in range(10, 16)], (330, 380),
    lambda rng, fi, i: "%s %s %s" % (ts(rng, fi), rng.choice(["INFO", "WARN", "ERROR"]), rng.choice([
        "upstream timeout after 3000ms", "request timeouts climbing", "set timeout_ms=2500", "readtimeout raised by client lib",
        "retry scheduled", "upstream ok", "connection reset by peer", "timeout waiting for lock", "pool size 32", "cache hit ratio 0.93"])),
    "README.md", ["# Gateway logs", "", "Free-text messages. A timeout event is a line containing the word timeout on its own;",
                  "timeouts (a rate summary), timeout_ms (config echo) and readtimeout (client lib) are not timeout events."])

W_USERTAB = line_world(
    "慢查询", ["db%d-slow.log" % i for i in range(1, 7)], (300, 360),
    lambda rng, fi, i: "# %s %dms %s" % (ts(rng, fi), rng.randint(200, 9000), rng.choice([
        "SELECT * FROM user WHERE id = ?", "SELECT name FROM users WHERE org = ?", "UPDATE user_profile SET bio = ?",
        "DELETE FROM user WHERE last_login < ?", "SELECT count(*) FROM orders", "INSERT INTO user_audit VALUES (?)",
        "SELECT u.id FROM user u JOIN orders o ON o.uid = u.id", "SELECT * FROM superuser_grants"])),
    "说明.md", ["# 慢查询日志", "", "每行一条慢 SQL。表名 user 和 users、user_profile、user_audit、superuser_grants 是不同的表。"])

W_REDIS = line_world(
    "logs/cache", ["cache-%s.log" % h for h in ["a", "b", "c", "d", "e", "f"]], (320, 380),
    lambda rng, fi, i: "%s host=%s %s" % (ts(rng, fi), rng.choice(["redis-1", "redis-10", "redis-12", "redis-2", "redis-1-replica"]),
                                          rng.choice(["evicted keys", "slowlog entry", "connection refused", "failover started", "ok"])),
    "README.md", ["# Cache logs", "", "redis-1 is the primary; redis-10, redis-12 and redis-1-replica are other nodes."])

W_ORDERID = line_world(
    "订单日志", ["%s.log" % d for d in ["0910", "0911", "0912", "0913", "0914", "0915"]], (330, 380),
    lambda rng, fi, i: "%s 订单 %s %s" % (ts(rng, fi), rng.choice(["A1024", "A10245", "A1024B", "A2048", "XA1024", "A1025"]),
                                        rng.choice(["已创建", "已支付", "已发货", "催单", "已退款"])),
    "说明.md", ["# 订单日志", "", "订单号区分全称：A1024 和 A10245、A1024B、XA1024 都是不同的订单。"])

W_RETRY = line_world(
    "jobs/logs", ["runner-%d.log" % i for i in range(1, 7)], (320, 380),
    lambda rng, fi, i: "%s job=%s %s" % (ts(rng, fi), rng.choice(["sync", "export", "billing"]), rng.choice([
        "retry 1 of 3", "retrying in 5s", "retry_count=2", "no retry needed", "giving up after retries", "done", "queued"])),
    "README.md", ["# Runner logs", "", "A retry attempt is logged with the word retry on its own (\"retry 1 of 3\", \"no retry needed\" is not an attempt",
                  "but still contains the word). retrying, retries and retry_count are other messages."])

W_WARN = line_world(
    "logs/build", ["build-%03d.log" % i for i in range(301, 307)], (330, 380),
    lambda rng, fi, i: "%s %s" % (rng.choice(["[WARN]", "[INFO]", "[ERROR]", "WARN:", "[WARNING]", "[RAW]"]), rng.choice([
        "deprecated API used", "cache miss", "test passed", "unused import", "network flake", "artifact uploaded"])),
    "README.md", ["# Build logs", "", "Warnings are lines tagged exactly [WARN]. [WARNING] comes from a vendored tool and is tracked separately."])

W_METRIC = line_world(
    "metrics", ["dump-%02d.txt" % i for i in range(1, 7)], (330, 380),
    lambda rng, fi, i: "%s %s %d" % (ts(rng, fi), rng.choice(["api.v2.latency", "api_v2_latency", "api.v2.latency.p99", "apixv2xlatency", "db.pool.size"]), rng.randint(1, 900)),
    "README.md", ["# Metric dumps", "", "Metric names are dotted. api.v2.latency is the one on the SLO board;",
                  "api.v2.latency.p99 and the legacy api_v2_latency are different series."])

W_CHANGELOG = line_world(
    "changelog", ["v%d.md" % v for v in range(20, 26)], (300, 360),
    lambda rng, fi, i: rng.choice(["- fix: handle empty cart", "- fixup: typo in fix", "  - fix: nested note", "- feat: export to pdf",
                                   "- feat(api): bulk delete", "- chore: bump deps", "- docs: fix link", "- fix(ui): button overlap"]),
    "README.md", ["# Changelog layout", "", "One file per release. A top-level bug fix entry is a line starting with \"- fix\" (\"- fix:\" or \"- fix(scope):\").",
                  "Indented entries are notes under another entry; fixup and docs entries are not bug fixes."], task_type="count_markers")

W_SWITCH = line_world(
    "开关", ["%s.conf" % s for s in ["支付", "推送", "搜索", "风控", "会员", "广告"]], (300, 360),
    lambda rng, fi, i: rng.choice(["启用=是", "# 启用=是", "启用=否", "  启用=是", "预发启用=是", "名称=%s%d" % (rng.choice(["开关", "实验"]), rng.randint(1, 999))]),
    "说明.md", ["# 开关配置", "", "只有顶格写的「启用=是」才生效；# 开头是注释，前面有空格的是被缩进屏蔽的旧配置，「预发启用」只在预发环境生效。"],
    task_type="read_effective")

W_USERID = dict(fmt="csv", root="订单/明细", files=["%02d.csv" % d for d in range(1, 9)], rows=(240, 300), cols=["订单号", "用户", "金额", "状态"],
                readme_name="说明.md", task_type="filter_count", needs_readme=True,
                readme=["# 订单明细", "", "用户字段是完整用户编号，u12 和 u120、u121、u12a 是不同用户。"],
                gen=lambda rng, fi, i: {"订单号": "D%02d%05d" % (fi, i), "用户": rng.choice(["u12", "u120", "u121", "u12a", "u7", "u33", "u45"]),
                                        "金额": "%.2f" % rng.uniform(5, 300), "状态": rng.choice(["已完成", "已完成", "已取消"])},
                unique="用户是精确字段，按整字段相等匹配只有一个结果。")

W_CAM = dict(fmt="kv", root="cams", files=["events-%02d.log" % d for d in range(1, 7)], rows=(330, 380), cols=["t", "cam", "event", "zone"],
             readme_name="README.md", task_type="count_events", needs_readme=True,
             readme=["# Camera events", "", "cam-3 is the loading-dock camera; cam-30, cam-31 and cam-3b are different cameras."],
             gen=lambda rng, fi, i: {"t": "D%02dT%02d%02d" % (fi + 1, rng.randint(0, 23), rng.randint(0, 59)), "cam": rng.choice(["cam-3", "cam-30", "cam-31", "cam-3b", "cam-7"]),
                                     "event": rng.choice(["motion", "motion", "offline", "tamper"]), "zone": rng.choice(["dock", "yard", "gate"])},
             unique="cam is an exact key=value field.")

W_SKU = dict(fmt="csv", root="sales/lines", files=["store-%d.csv" % s for s in range(1, 8)], rows=(250, 300), cols=["receipt", "product", "qty", "unit_price"],
             readme_name="README.md", task_type="aggregate", needs_readme=True,
             readme=["# Sales lines", "", "product codes are exact: P-77 is the house blend; P-770 and P-77X are other products."],
             gen=lambda rng, fi, i: {"receipt": "R%d-%05d" % (fi, i), "product": rng.choice(["P-77", "P-770", "P-77X", "P-12", "P-5"]),
                                     "qty": str(rng.randint(1, 9)), "unit_price": "%.2f" % rng.uniform(2, 40)},
             unique="product is an exact field.")

W_STORE = dict(fmt="csv", root="门店/客流", files=["第%d周.csv" % w for w in range(31, 37)], rows=(260, 310), cols=["日期", "门店", "时段", "人数"],
               readme_name="说明.md", task_type="aggregate", needs_readme=True,
               readme=["# 客流统计", "", "门店编号要整列匹配：S1 是旗舰店，S10、S11、S1A 是其他门店。"],
               gen=lambda rng, fi, i: {"日期": "2026-%02d-%02d" % (8 + (fi > 3), rng.randint(1, 28)), "门店": rng.choice(["S1", "S10", "S11", "S1A", "S2", "S3"]),
                                       "时段": rng.choice(["上午", "下午", "晚上"]), "人数": str(rng.randint(3, 99))},
               unique="门店是精确字段。")


def line_case(cid, world, queries, desc, family, seed, sub="M9g", axes=("OBS", "CON")):
    return agg_case(cid, world, queries, sub=sub, seed=seed, desc=desc, family=family, axes=axes)


PLAN = [
    ("log-10075", W_TIMEOUT, [Q("count", 're.search(r"\\btimeout\\b", r["line"])', "How many timeout events are in the gateway logs for the 10th to the 15th?",
      "cat logs/gateway/*.log | grep -cw timeout", "{v} timeout events (timeouts, timeout_ms and readtimeout lines excluded).",
      decoy={"pred": '"timeout" in r["line"]'}, decoy_note="a substring grep for timeout")],
     "Counts whole-word timeout events across six gateway logs where longer words contain it", "fam-log-b14-wordtimeout-01"),
    ("log-10076", W_USERTAB, [Q("count", 're.search(r"\\buser\\b", r["line"])', "慢查询日志里，涉及 user 这张表的慢 SQL 有多少条？",
      "cat 慢查询/*.log | grep -cw user", "涉及 user 表的慢 SQL 有 {v} 条（users、user_profile 等不算）。",
      decoy={"pred": '"user" in r["line"]'}, decoy_note="a substring grep for user")],
     "Counts slow queries touching one table by whole-word match while similar table names contain it", "fam-log-b14-wordusertab-01"),
    ("log-10077", W_REDIS, [Q("count", 're.search(r"host=redis-1 ", r["line"]) and "failover" not in r["line"]', "How many non-failover lines did the primary cache node log?",
      "cat logs/cache/*.log | awk '$2==\"host=redis-1\" && !/failover/' | wc -l", "{v} lines from redis-1 that are not failovers.",
      decoy={"pred": 're.search(r"host=redis-1(?![A-Za-z0-9_])", r["line"]) and "failover" not in r["line"]'}, decoy_note="grep -w host=redis-1, which also matches redis-1-replica (a hyphen is not a word character)")],
     "Counts lines from one cache host by whole-word match while other host names extend it", "fam-log-b14-wordredis-01"),
    ("log-10078", W_ORDERID, [Q("count", 're.search(r"(?<![A-Za-z0-9])A1024(?![A-Za-z0-9])", r["line"]) and "催单" in r["line"]',
      "订单 A1024 一共被催了几次单？六天的日志都看一下。", "cat 订单日志/*.log | grep -w A1024 | grep -c 催单", "A1024 被催单 {v} 次。",
      decoy={"pred": '"A1024" in r["line"] and "催单" in r["line"]'}, decoy_note="a substring grep for A1024")],
     "Counts reminder events for one order id where longer ids contain it", "fam-log-b14-wordorderid-01"),
    ("log-10079", W_RETRY, [Q("count", 're.search(r"\\bretry\\b", r["line"])', "How many lines across the runner logs contain the word retry on its own?",
      "cat jobs/logs/*.log | grep -cw retry", "{v}.", decoy={"pred": '"retry" in r["line"]'}, decoy_note="a substring grep"),
      Q("count", 're.search(r"\\bretry\\b", r["line"]) and "job=billing" in r["line"]', "Only for the billing job?",
        "cat jobs/logs/*.log | grep -w retry | grep -c 'job=billing'", "{v} of them are from the billing job.")],
     "Two turns: counts whole-word retry lines, then only for one job", "fam-log-b14-wordretry-01"),
    ("log-10080", W_ORDERID, [Q("count", 're.search(r"(?<![A-Za-z0-9])A2048(?![A-Za-z0-9])", r["line"])', "日志里订单 A2048 出现了多少次？",
      "cat 订单日志/*.log | grep -cw A2048", "{v} 次。"),
      Q("count", 're.search(r"(?<![A-Za-z0-9])A1024(?![A-Za-z0-9])", r["line"]) and "已退款" in r["line"]', "那 A1024 有几条已退款记录？注意别和别的订单号混了。",
        "cat 订单日志/*.log | grep -w A1024 | grep -c 已退款", "A1024 的已退款记录有 {v} 条。",
        decoy={"pred": '"A1024" in r["line"] and "已退款" in r["line"]'}, decoy_note="a substring grep for A1024")],
     "Two turns: counts one order id, then refund lines for a second id that longer ids contain", "fam-log-b14-wordorder2-01"),
    ("log-10081", W_WARN, [Q("count", '"[WARN]" in r["line"]', "How many warnings are in the six build logs?",
      "cat logs/build/*.log | grep -cF '[WARN]'", "{v} [WARN] lines.",
      decoy={"pred": 'any(c in r["line"] for c in "WARN")'}, decoy_note="an unescaped grep '[WARN]' (a character class)")],
     "Counts a bracketed tag where an unescaped pattern becomes a character class", "fam-log-b14-fixedwarn-01"),
    ("log-10082", W_METRIC, [Q("count", 'r["line"].split(" ")[1] == "api.v2.latency"', "How many samples of the SLO latency metric are in the dumps?",
      "cat metrics/*.txt | awk '$2==\"api.v2.latency\"' | wc -l", "{v} samples of api.v2.latency.",
      decoy={"pred": 're.search("api.v2.latency", r["line"])'}, decoy_note="an unescaped regex (dots match _ and x, .p99 included)")],
     "Counts one dotted metric name where regex dots and a longer series both over-match", "fam-log-b14-fixedmetric-01"),
    ("code-10083", W_CHANGELOG, [Q("count", 'r["line"].startswith("- fix:") or r["line"].startswith("- fix(")', "How many top-level bug fix entries are in the changelogs for v20 to v25?",
      "cat changelog/*.md | grep -cE '^- fix(:|\\()'", "{v} bug fix entries.",
      decoy={"pred": '"fix" in r["line"]'}, decoy_note="an unanchored grep fix")],
     "Counts anchored changelog entries while indented, fixup and docs lines also contain the word", "fam-code-b14-anchorfix-01"),
    ("cfg-10084", W_SWITCH, [Q("count", 'r["line"] == "启用=是"', "六个开关配置文件里，真正生效的「启用=是」一共有几行？",
      "cat 开关/*.conf | grep -c '^启用=是$'", "生效的有 {v} 行。",
      decoy={"pred": '"启用=是" in r["line"]'}, decoy_note="an unanchored grep")],
     "Counts effective switch lines where commented, indented and prefixed variants contain the same text", "fam-cfg-b14-anchorswitch-01"),
    ("code-10085", W_CHANGELOG, [Q("count", 'r["line"].startswith("- feat:") or r["line"].startswith("- feat(")', "How many top-level feature entries are there across the changelogs?",
      "cat changelog/*.md | grep -cE '^- feat(:|\\()'", "{v}."),
      Q("count", 'r["line"].startswith("- fix:") or r["line"].startswith("- fix(")', "And top-level bug fixes?",
        "cat changelog/*.md | grep -cE '^- fix(:|\\()'", "{v} bug fix entries.", decoy={"pred": '"fix" in r["line"]'}, decoy_note="an unanchored grep fix")],
     "Two turns: counts anchored feature entries, then anchored fix entries", "fam-code-b14-anchorfeat-01"),
    ("tab-10086", W_USERID, [Q("count", 'r["用户"]=="u12" and r["状态"]=="已完成"', "用户 u12 一共完成了多少笔订单？",
      "cat 订单/明细/*.csv | awk -F, '$2==\"u12\" && $4==\"已完成\"' | wc -l", "u12 完成了 {v} 笔订单。",
      decoy={"pred": 'r["用户"].startswith("u12") and r["状态"]=="已完成"'}, decoy_note="a substring grep for u12")],
     "Counts completed orders for one user id where longer ids start with it", "fam-tab-b14-exactuser-01"),
    ("log-10087", W_CAM, [Q("count", 'r["cam"]=="cam-3" and r["event"]=="offline"', "How often did the loading-dock camera go offline in these six days?",
      "cat cams/*.log | grep ' cam=cam-3 ' | grep -c 'event=offline'", "cam-3 went offline {v} times.",
      decoy={"pred": 'r["cam"].startswith("cam-3") and r["event"]=="offline"'}, decoy_note="a substring grep for cam-3")],
     "Counts offline events for one camera where other camera names extend its id", "fam-log-b14-exactcam-01"),
    ("tab-10088", W_SKU, [Q("sum", 'r["product"]=="P-77"', "How many units of the house blend did the seven stores sell?",
      "cat sales/lines/*.csv | awk -F, '$2==\"P-77\" {s+=$3} END {print s}'", "{v} units of P-77.", val='r["qty"]',
      decoy={"pred": 'r["product"].startswith("P-77")'}, decoy_note="prefix-matching P-770 and P-77X")],
     "Sums units for one product code where longer codes share the prefix", "fam-tab-b14-exactsku-01"),
    ("tab-10089", W_STORE, [Q("sum", 'r["门店"]=="S1"', "旗舰店这六周一共来了多少客流？",
      "cat 门店/客流/*.csv | awk -F, '$2==\"S1\" {s+=$4} END {print s}'", "{v} 人次。", val='r["人数"]',
      decoy={"pred": 'r["门店"].startswith("S1")'}, decoy_note="prefix-matching S10/S11/S1A"),
      Q("sum", 'r["门店"]=="S1" and r["时段"]=="晚上"', "其中晚上时段的有多少？",
        "cat 门店/客流/*.csv | awk -F, '$2==\"S1\" && $3==\"晚上\" {s+=$4} END {print s}'", "旗舰店晚上时段客流 {v} 人次。", val='r["人数"]')],
     "Two turns: sums visitors for one store code where others share the prefix, then one time slot", "fam-tab-b14-exactstore-01"),
    ("tab-10090", W_USERID, [Q("sumc", 'r["用户"]=="u12" and r["状态"]=="已取消"', "u12 取消的订单金额加起来是多少？",
      "cat 订单/明细/*.csv | awk -F, '$2==\"u12\" && $4==\"已取消\" {s+=$3} END {printf \"%.2f\\n\", s}'", "u12 已取消订单合计 {v} 元。", val='r["金额"]',
      decoy={"pred": 'r["用户"].startswith("u12") and r["状态"]=="已取消"'}, decoy_note="a substring grep for u12")],
     "Sums cancelled order amounts for one user id where longer ids start with it", "fam-tab-b14-exactusersum-01"),
]


def _mk(entry, seed):
    cid, world, queries, desc, family = entry

    def build():
        return line_case(cid, world, queries, desc, family, seed)
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(PLAN):
    BUILDERS.append(_mk(_e, 14200 + _i))
