"""b21a sub 3 (consistent multi-file changes), cases 31033-31045."""
from common import L, make, RW, RL, RB, RLW, RA

B = []


def reg(f):
    B.append(f)
    return f


def multi(cid, sub_files, ops, turns, policy, desc, trap, steps, unique, task_type="bulk_edit", traps=("TR-DECOY",)):
    make(cid, sub="multi", task_type=task_type, desc=desc, files=sub_files, turns=turns, ops=ops, policy=policy, traps=traps,
         notes_ref={"traps": [trap], "steps": steps, "unique": unique}, ref_calls=6)


@reg
def m1():
    f = {"ops/prod.env": L("SERVICE_PORT=8080", "HEALTH_URL=http://localhost:8080/health"), "ops/k8s-svc.yaml": L("kind: Service", "spec:", "  ports:", "  - port: 8080", "    targetPort: 8080"),
         "ops/readme.txt": L("服务默认端口 8080，健康检查走 /health。", "监控脚本在 ops/probe.sh。"), "ops/probe.sh": L("#!/bin/sh", "curl -fs http://localhost:8080/health || exit 1"),
         "ops/archive-old.env": L("SERVICE_PORT=8080")}
    ops = [[("sub", "ops/prod.env", "SERVICE_PORT=8080", "SERVICE_PORT=9090"), ("sub", "ops/prod.env", "localhost:8080", "localhost:9090"),
            ("sub", "ops/k8s-svc.yaml", "  - port: 8080\n    targetPort: 8080\n", "  - port: 9090\n    targetPort: 9090\n"), ("sub", "ops/readme.txt", "默认端口 8080", "默认端口 9090"),
            ("sub", "ops/probe.sh", "localhost:8080", "localhost:9090")]]
    multi("cfg-31033", f, ops, [("服务端口从 8080 改成 9090，ops 目录下 prod.env、k8s-svc.yaml、readme.txt、probe.sh 里用到的都要一起改。archive-old.env 是旧档，别碰。改完告诉我每个文件改了几处。", ["9090", "archive-old.env"], None)], None,
          "Changes a port across four files and leaves an archive file", "TR-DECOY: archive-old.env also holds 8080 and must stay; prod.env has two occurrences.",
          ["grep 8080 across ops", "edit each of the four files", "grep again to confirm only archive-old.env keeps 8080"], "Four files change, archive stays.", task_type="edit_value")


@reg
def m2():
    f = {"app/config.yaml": L("api_base: https://api.v1.nimbus.example/v1", "timeout: 10"), "app/client.js": L("const BASE = 'https://api.v1.nimbus.example/v1';", "export const get = (p) => fetch(BASE + p);"),
         "docs/api.md": L("# API", "", "基础地址：https://api.v1.nimbus.example/v1", "示例：GET https://api.v1.nimbus.example/v1/users")}
    ops = [[("sub", "app/config.yaml", "api.v1.nimbus.example/v1", "api.v2.nimbus.example/v2"), ("sub", "app/client.js", "api.v1.nimbus.example/v1", "api.v2.nimbus.example/v2"),
            ("sub", "docs/api.md", "基础地址：https://api.v1.nimbus.example/v1", "基础地址：https://api.v2.nimbus.example/v2"), ("sub", "docs/api.md", "GET https://api.v1.nimbus.example/v1/users", "GET https://api.v2.nimbus.example/v2/users")]]
    multi("doc-31034", f, ops, [("The API moved from https://api.v1.nimbus.example/v1 to https://api.v2.nimbus.example/v2. Update every place that mentions the old address in config.yaml, client.js and docs/api.md, then check nothing still says v1. Tell me how many places you changed.", ["v2", "4"], None)],
          RB, "Updates an API base URL in config, code and docs", "TR-DECOY: the doc mentions it twice.", ["grep -rn v1", "sed or edit", "grep again"], "Four occurrences become v2.", task_type="write_structured")


@reg
def m3():
    f = {"src/utils/date_fmt.py": L("def fmt_date(d):", "    return d.strftime('%Y-%m-%d')"), "src/report.py": L("from utils.date_fmt import fmt_date", "", "def title(d):", "    return 'Report ' + fmt_date(d)"),
         "src/export.py": L("from utils.date_fmt import fmt_date", "", "def row(d, v):", "    return [fmt_date(d), v]"), "tests/test_date.py": L("from utils.date_fmt import fmt_date", "", "def test_fmt(d):", "    assert fmt_date(d)")}
    ops = [[("sub", "src/utils/date_fmt.py", "def fmt_date(d):", "def format_date(d):"), ("sub", "src/report.py", "import fmt_date", "import format_date"), ("sub", "src/report.py", "' + fmt_date(d)", "' + format_date(d)"),
            ("sub", "src/export.py", "import fmt_date", "import format_date"), ("sub", "src/export.py", "[fmt_date(d), v]", "[format_date(d), v]"), ("sub", "tests/test_date.py", "import fmt_date", "import format_date"), ("sub", "tests/test_date.py", "assert fmt_date(d)", "assert format_date(d)")]]
    multi("code-31035", f, ops, [("把函数 fmt_date 改名为 format_date，定义和 src、tests 里所有引用都要跟着改，不然会 import 失败。改完检查一遍没有遗漏，告诉我一共改了几个文件。", ["format_date", "4"], None)], None,
          "Renames a function and updates imports and calls in four files", "TR-DECOY: import line and call line are separate edits in each file.", ["grep -rn fmt_date", "edit 4 files", "grep again"], "No fmt_date remains.", task_type="fix_edge_case")


@reg
def m4():
    f = {"site/nav.md": L("- [首页](index.md)", "- [定价](pricing.md)", "- [关于](about-us.md)"), "site/index.md": L("# 首页", "欢迎。了解我们请看[关于](about-us.md)。"),
         "site/footer.md": L("© Lumen", "[关于我们](about-us.md) | [联系](contact.md)"), "site/about-us.md": L("# 关于我们", "我们是 Lumen。")}
    ops = [[("sub", "site/nav.md", "(about-us.md)", "(about.md)"), ("sub", "site/index.md", "(about-us.md)", "(about.md)"), ("sub", "site/footer.md", "(about-us.md)", "(about.md)")]]
    multi("fs-31036", f, ops, [("site/about-us.md 这个页面的文件名要简化成 site/about.md。我没法重命名文件，你只需要把其他页面里指向它的链接都改成 about.md，页面内容本身先不动。改完告诉我改了哪几个文件。", ["nav.md", "index.md", "footer.md"], None)], RW,
          "Updates links to a renamed page in three files without touching the page", "TR-DECOY: about-us.md itself must stay unchanged.", ["grep about-us.md", "edit three link lines", "grep again"], "Three files change, about-us.md unchanged.")


@reg
def m5():
    f = {"charts/values-dev.yaml": L("image:", "  tag: 3.4.1", "replicas: 1"), "charts/values-staging.yaml": L("image:", "  tag: 3.4.1", "replicas: 2"),
         "charts/values-prod.yaml": L("image:", "  tag: 3.3.9", "replicas: 6"), "charts/NOTES.txt": L("prod 暂时留在 3.3.9，等灰度结束再升。", "dev 和 staging 跟随最新版本。")}
    ops = [[("sub", "charts/values-dev.yaml", "tag: 3.4.1", "tag: 3.5.0"), ("sub", "charts/values-staging.yaml", "tag: 3.4.1", "tag: 3.5.0")]]
    multi("cfg-31037", f, ops, [("镜像升到 3.5.0：按 charts/NOTES.txt 的说明，该升的环境都升，不该升的不要动。告诉我你升了哪几个环境。", ["dev", "staging", "3.5.0"], None)], None,
          "Bumps image tags in the environments a notes file allows", "TR-READONLY: prod is held back by NOTES.txt; excluded file stays.", ["read NOTES.txt", "edit dev and staging", "grep tag"], "dev and staging 3.5.0; prod unchanged.", traps=("TR-READONLY",), task_type="edit_value")


@reg
def m6():
    f = {"i18n/en.json": L("{", '  "app.name": "Orbit",', '  "app.tagline": "Plan together"', "}"), "i18n/zh.json": L("{", '  "app.name": "Orbit",', '  "app.tagline": "一起规划"', "}"),
         "i18n/ja.json": L("{", '  "app.name": "Orbit",', '  "app.tagline": "一緒に計画"', "}"), "i18n/_README.md": L("所有语言文件的 app.name 必须一致。")}
    ops = [[("sub", "i18n/en.json", '"Orbit"', '"Orbit Pro"'), ("sub", "i18n/zh.json", '"app.name": "Orbit"', '"app.name": "Orbit Pro"'), ("sub", "i18n/ja.json", '"app.name": "Orbit"', '"app.name": "Orbit Pro"')]]
    multi("cfg-31038", f, ops, [("产品改名为 Orbit Pro，i18n 下每种语言文件里的应用名都要改，要求见 i18n/_README.md。口号文案不动。改完告诉我改了几个文件。", ["3", "Orbit Pro"], None)], RL,
          "Renames the product in three language files per a readme requirement", "TR-DECOY: only app.name, not tagline.", ["read README", "edit three files", "grep app.name"], "All three have Orbit Pro.", task_type="edit_value")


@reg
def m7():
    f = {"billing/rates.csv": L("plan,monthly,tax", "basic,49,0.06", "team,149,0.06", "pro,399,0.06"), "billing/invoice_template.txt": L("税率：6%", "金额含税。"),
         "billing/README.md": L("税率变动时，rates.csv 的 tax 列和 invoice_template.txt 的税率说明要同步。")}
    ops = [[("sub", "billing/rates.csv", "basic,49,0.06", "basic,49,0.08"), ("sub", "billing/rates.csv", "team,149,0.06", "team,149,0.08"), ("sub", "billing/rates.csv", "pro,399,0.06", "pro,399,0.08"), ("sub", "billing/invoice_template.txt", "税率：6%", "税率：8%")]]
    multi("tab-31039", f, ops, [("税率从 6% 调到 8%。按 billing/README.md 的要求把需要同步的地方都改了，改完核对一下，再告诉我每个文件改了几处。", ["8%", "0.08"], None)], None,
          "Raises a tax rate in a csv column and a template note", "TR-DECOY: README says which files must sync; three csv rows + template.", ["read README", "edit csv rows and template", "grep"], "csv 3 rows 0.08, template 8%.", task_type="write_summary")


@reg
def m8():
    f = {"scripts/backup.sh": L("#!/bin/sh", "DEST=/mnt/backup/old-nas", "rsync -a /data $DEST"), "scripts/restore.sh": L("#!/bin/sh", "SRC=/mnt/backup/old-nas", "rsync -a $SRC/data /data"),
         "docs/backup.md": L("备份目的地：/mnt/backup/old-nas", "恢复时从同一位置拷回。"), "scripts/legacy-copy.sh": L("#!/bin/sh", "cp -r /data /mnt/backup/old-nas  # 历史脚本，已停用")}
    ops = [[("sub", "scripts/backup.sh", "/mnt/backup/old-nas", "/mnt/backup/new-nas"), ("sub", "scripts/restore.sh", "/mnt/backup/old-nas", "/mnt/backup/new-nas"), ("sub", "docs/backup.md", "/mnt/backup/old-nas", "/mnt/backup/new-nas")]]
    multi("fs-31040", f, ops, [("Backups now go to /mnt/backup/new-nas instead of /mnt/backup/old-nas. Update backup.sh, restore.sh and docs/backup.md. legacy-copy.sh is deprecated and marked as such, leave it alone. Which files did you change?", ["new-nas", "backup.sh", "restore.sh"], ["legacy-copy.sh 已改"])], RB,
          "Changes a backup path in scripts and docs but not a deprecated script", "TR-DECOY: legacy-copy.sh shares the string and must stay.", ["grep -rn old-nas", "sed three files", "grep again"], "Three files change.")


@reg
def m9():
    f = {"web/index.html": L("<title>Maple Notes v1.9</title>", '<footer>Maple Notes 1.9</footer>'), "web/about.html": L("<p>当前版本：1.9</p>"), "VERSION": L("1.9.0"), "web/archive.html": L("<p>历史：1.8 已停止维护。</p>")}
    ops = [[("sub", "web/index.html", "v1.9</title>", "v2.0</title>"), ("sub", "web/index.html", "Notes 1.9<", "Notes 2.0<"), ("sub", "web/about.html", "当前版本：1.9", "当前版本：2.0"), ("sub", "VERSION", "1.9.0", "2.0.0")]]
    multi("code-31041", f, ops, [("发 2.0 了。VERSION 文件改成 2.0.0，网页 index.html 的标题和页脚、about.html 的当前版本都改成 2.0。archive.html 是历史页，不改。改完告诉我改动清单。", ["2.0.0", "2.0"], None)], None,
          "Bumps a version in a VERSION file and three places in pages", "TR-DECOY: archive.html mentions an older version, 1.8.", ["edit four places", "grep 1.9"], "Four edits, archive unchanged.", task_type="fix_edge_case")


@reg
def m10():
    f = {"team/roster.csv": L("name,email,role", "Ada,ada@orbit.example,lead", "Ben,ben@orbit.example,dev", "Cai,cai@orbit.example,dev"), "team/aliases.txt": L("ben@orbit.example -> eng-all@orbit.example", "cai@orbit.example -> eng-all@orbit.example"),
         "team/README.md": L("邮箱变更时，roster.csv 和 aliases.txt 都要同步，别的文件是自动生成的。")}
    ops = [[("sub", "team/roster.csv", "ben@orbit.example", "ben.w@orbit.example"), ("sub", "team/aliases.txt", "ben@orbit.example ->", "ben.w@orbit.example ->")]]
    multi("tab-31042", f, ops, [("Ben 的邮箱换成 ben.w@orbit.example 了，请按 team/README.md 把该改的文件都改好。别动其他人的。告诉我改了哪些行。", ["ben.w@orbit.example"], None)], None,
          "Changes one person's email in two files per a readme", "TR-DECOY: aliases map direction; only Ben's lines.", ["read README", "edit csv line", "edit alias line", "grep ben"], "Two files, one line each.", task_type="write_summary")


@reg
def m11():
    f = {"config/db.yaml": L("host: db-old.internal", "port: 5432"), "config/migrate.yaml": L("target: db-old.internal", "dry_run: false"), "config/replica-db.yaml": L("host: db-old.internal", "read_only: true"),
         "config/README.md": L("replica-* 文件由 DBA 管理，应用侧不要改。")}
    ops = [[("sub", "config/db.yaml", "db-old.internal", "db-new.internal"), ("sub", "config/migrate.yaml", "db-old.internal", "db-new.internal")]]
    multi("cfg-31043", f, ops, [("数据库搬到了 db-new.internal，把 config 下该改的配置里的 db-old.internal 换掉，注意看 README。改完告诉我改了哪些文件、哪些没改以及为什么。", ["db.yaml", "migrate.yaml", "replica"], None)], RL,
          "Moves a db host in app configs but not DBA-managed replica config", "TR-READONLY: replica-db.yaml is excluded by README.", ["read README", "edit db.yaml, migrate.yaml"], "Two files change; replica unchanged.", traps=("TR-READONLY",), task_type="edit_value")


@reg
def m12():
    f = {"locales/menu.txt": L("save=保存", "open=打开", "quit=退出"), "src/menu.py": L("ITEMS = ['save', 'open', 'quit']", "SHORTCUT = {'quit': 'Ctrl+Q'}"), "docs/menu.md": L("菜单项：save、open、quit。退出快捷键 Ctrl+Q。")}
    ops = [[("sub", "locales/menu.txt", "quit=退出", "exit=退出"), ("sub", "src/menu.py", "'quit']", "'exit']"), ("sub", "src/menu.py", "{'quit':", "{'exit':"), ("sub", "docs/menu.md", "open、quit。", "open、exit。")], [("sub", "docs/menu.md", "Ctrl+Q", "Ctrl+W")]]
    multi("code-31044", f, ops, [("菜单项的内部名 quit 统一改成 exit：locales/menu.txt 的键、src/menu.py 的列表和快捷键表、docs/menu.md 的说明都要改。显示文字“退出”和快捷键 Ctrl+Q 不变。改完检查没有漏。", ["exit"], None),
                                  ("再把 docs/menu.md 里写的退出快捷键改成 Ctrl+W，只改文档，代码里的 SHORTCUT 先不动。告诉我这句说明现在是什么。", ["Ctrl+W", "exit"], None)], None,
          "Renames an internal key across three files then edits the doc shortcut", "TR-DECOY: quit appears as key, list item, dict key and doc word; 退出 is display text.", ["grep quit", "edit 4 places", "turn2 edit doc"], "Final menu.md says exit and Ctrl+W.", task_type="fix_edge_case")


@reg
def m13():
    f = {"cron/jobs.txt": L("0 3 * * * /opt/bin/sync --tz Asia/Shanghai", "0 9 * * 1 /opt/bin/weekly --tz Asia/Shanghai"), "cron/report.conf": L("timezone = Asia/Shanghai", "hour = 9"),
         "cron/legacy.conf": L("timezone = Asia/Shanghai  # 旧系统，保持不变")}
    ops = [[("sub", "cron/jobs.txt", "sync --tz Asia/Shanghai", "sync --tz Asia/Singapore"), ("sub", "cron/jobs.txt", "weekly --tz Asia/Shanghai", "weekly --tz Asia/Singapore"), ("sub", "cron/report.conf", "Asia/Shanghai", "Asia/Singapore")]]
    multi("cfg-31045", f, ops, [("服务器迁到新加坡，cron/jobs.txt 里两个任务和 cron/report.conf 的时区从 Asia/Shanghai 改成 Asia/Singapore。legacy.conf 注明保持不变，不要动。改完告诉我一共改了几处。", ["3", "Asia/Singapore"], None)], None,
          "Changes a timezone in three places across two files and leaves legacy", "TR-DECOY: legacy.conf has the same string.", ["grep Asia/Shanghai", "edit three places"], "Three replacements.", task_type="edit_value")
