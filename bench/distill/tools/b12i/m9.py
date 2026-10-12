"""M9 (bash) batch b12i of v1.41: ids 9221-9240, all M9e (bash offered but not the right action).

9221-9230: one named file holds the answer, bash is forbidden, a .bak/.old/.example/other-environment copy is the decoy.
9231-9236: the user asks for a command and says not to run it (tools [] + require_active_no_call).
9237-9240: two turns; turn 1 is a no-bash read of one named file, turn 2 a bounded bash aggregation over several txt files."""
import json
from random import Random

from common import lines
from common import write_case as _write_case

REFS = {}
_SPEC = {}
READ_TOOLS = ("read_file", "read_lines", "search_text")
LINES_GUARD = 'case = json.load(open("case.json"))\n'


def write_case(cid, *, files, verify, **kw):
    """Adds a per-file line-count guard so deleting any fixture line breaks verify."""
    guard = "LINES = %r\nfor _p, _n in LINES.items():\n    assert len(case[\"files\"][_p].splitlines()) == _n, _p\n" % {p: len(t.splitlines()) for p, t in files.items()}
    verify = verify.replace(LINES_GUARD, LINES_GUARD + guard, 1)
    return _write_case(cid, files=files, verify=verify, **kw)


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


def thousands(value):
    whole, _, frac = str(value).partition(".")
    grouped = f"{int(whole):,}" + ("." + frac if frac else "")
    return [str(value)] if grouped == str(value) else [str(value), grouped]


# ------------------------------------------------------------------ 9221-9230 single named file, bash forbidden


def read_case(cid, *, topic, desc, files, checks, prompt, want, decoy, task_type, answer, alts, token=False, scen_tags=("OBS",)):
    """checks: (path, line index, exact line) assertions pinned in verify.py; want: acceptable answer literals."""
    verify = '''
import json
case = json.load(open("case.json"))
for path, idx, row in %s:
    assert case["files"][path].splitlines()[idx] == row, (path, idx)
print(json.dumps(%s, ensure_ascii=False))
''' % (json.dumps(checks, ensure_ascii=False), json.dumps({"expected_number": int(want[0])} if token else {"expected_contains_any": want}, ensure_ascii=False))
    notes = f"""## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value ({decoy}).

## Reference solution
1. read_file on the named file.
Final answer: {answer}

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
""" + phrasings(*alts)
    _SPEC[cid] = dict(kind="bash_avoided", sub="M9e", via=READ_TOOLS)
    expect = {"output_contains_any": want, "forbidden_tools": ["bash"], "max_output_chars": 600}
    if token:
        expect = {"output_contains": want, "output_contains_token": True, "forbidden_tools": ["bash"], "max_output_chars": 600}
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12i-{topic}-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": decoy}, axes=list(scen_tags), files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": expect}])


def cfg_9221():
    files = {"service/settings.toml": lines(["[server]", 'host = "0.0.0.0"', "port = 8443", "", "[cache]", "ttl_seconds = 300"]),
             "service/settings.toml.bak": lines(["[server]", 'host = "0.0.0.0"', "port = 8080", "", "[cache]", "ttl_seconds = 60"])}
    return read_case(
        "cfg-9221", topic="tomlport", desc="Single-file port lookup in a toml settings file with a .bak decoy while bash is offered but forbidden",
        files=files, checks=[["service/settings.toml", 2, "port = 8443"], ["service/settings.toml.bak", 2, "port = 8080"]],
        prompt="What port does the server listen on according to service/settings.toml?", want=["8443"], decoy="8080",
        task_type="read_effective", answer="The server listens on port 8443 (service/settings.toml; the .bak copy says 8080).", token=True,
        alts=["Which port is configured under [server] in service/settings.toml?", "Check service/settings.toml and tell me the listening port.",
              "service/settings.toml: what is `port` set to?", "What's the server port in the toml settings file?", "Tell me the port from service/settings.toml."])


def doc_9222():
    files = {"值班/联系方式.md": lines(["# 值班联系方式", "", "- 应用值班：010-5550-3302", "- 数据库值班：010-5550-1427", "- 网络值班：010-5550-7781"]),
             "值班/联系方式-旧.md": lines(["# 值班联系方式（2025 年，已作废）", "", "- 应用值班：010-5550-3302", "- 数据库值班：010-5550-0961", "- 网络值班：010-5550-7781"])}
    return read_case(
        "doc-9222", topic="oncallphone", desc="Single-file on-call phone lookup with an outdated copy while bash is offered but forbidden",
        files=files, checks=[["值班/联系方式.md", 3, "- 数据库值班：010-5550-1427"], ["值班/联系方式-旧.md", 3, "- 数据库值班：010-5550-0961"]],
        prompt="值班/联系方式.md 里数据库值班的电话是多少？", want=["010-5550-1427", "5550-1427"], decoy="010-5550-0961",
        task_type="policy_lookup", answer="数据库值班电话是 010-5550-1427（旧版文档里的 0961 已作废）。", scen_tags=("OBS", "CHN"),
        alts=["数据库值班打哪个电话？看 值班/联系方式.md。", "按 值班/联系方式.md，DBA 值班电话是什么？", "帮我查一下数据库值班的号码，文件是 值班/联系方式.md。",
              "联系方式文档里数据库值班那一行的电话是多少？", "值班/联系方式.md 记录的数据库值班号码是？"])


def cfg_9223():
    files = {"config/prod.env": lines(["APP_ENV=production", "DB_HOST=db-prod-02.internal", "DB_PORT=5432", "CACHE_URL=redis://cache-prod:6379"]),
             "config/prod.env.bak": lines(["APP_ENV=production", "DB_HOST=db-prod-01.internal", "DB_PORT=5432", "CACHE_URL=redis://cache-prod:6379"])}
    return read_case(
        "cfg-9223", topic="envdbhost", desc="Single-file DB_HOST lookup in an env file with a .bak decoy while bash is offered but forbidden",
        files=files, checks=[["config/prod.env", 1, "DB_HOST=db-prod-02.internal"], ["config/prod.env.bak", 1, "DB_HOST=db-prod-01.internal"]],
        prompt="config/prod.env 里 DB_HOST 设的是哪台主机？", want=["db-prod-02.internal", "db-prod-02"], decoy="db-prod-01.internal",
        task_type="read_effective", answer="DB_HOST 是 db-prod-02.internal（.bak 备份里是 db-prod-01，不是当前值）。", scen_tags=("OBS", "CHN"),
        alts=["生产环境数据库主机是哪个？config/prod.env 里写着。", "config/prod.env 的 DB_HOST 是什么？", "看一下 config/prod.env，数据库连的是哪台机器？",
              "prod.env 里配置的 DB_HOST 值是多少？", "告诉我 config/prod.env 里数据库主机名。"])


def doc_9224():
    files = {"README.md": lines(["# Pinecone Toolkit", "", "## Requirements", "", "- Python 3.11 or newer", "- 2 GB of free disk space", "", "## Install", "", "Run `pip install pinecone-toolkit`."]),
             "README.md.bak": lines(["# Pinecone Toolkit", "", "## Requirements", "", "- Python 3.8 or newer", "- 1 GB of free disk space", "", "## Install", "", "Run `pip install pinecone-toolkit`."])}
    return read_case(
        "doc-9224", topic="minpython", desc="Single-file minimum-Python-version lookup in a README with a .bak decoy while bash is offered but forbidden",
        files=files, checks=[["README.md", 4, "- Python 3.11 or newer"], ["README.md.bak", 4, "- Python 3.8 or newer"]],
        prompt="What is the minimum Python version listed in README.md?", want=["3.11"], decoy="3.8",
        task_type="policy_lookup", answer="Python 3.11 or newer (README.md.bak still says 3.8).",
        alts=["Which Python version does README.md require?", "README.md lists a Python requirement. What is it?", "How new does Python need to be, per README.md?",
              "Check README.md: minimum supported Python?", "What Python do I need according to the README?"])


def doc_9225():
    files = {"运维/备份策略.txt": lines(["备份策略（2026 年 10 月起执行）", "全量备份：每周日 02:00，保留 4 份", "增量备份：每天 02:00，保留 14 份", "异地副本：每月 1 日，保留 6 份"]),
             "运维/备份策略.txt.bak": lines(["备份策略（2025 年版）", "全量备份：每周日 02:00，保留 2 份", "增量备份：每天 02:00，保留 7 份", "异地副本：每月 1 日，保留 3 份"])}
    return read_case(
        "doc-9225", topic="backupkeep", desc="Single-file backup retention lookup with a .bak decoy while bash is offered but forbidden",
        files=files, checks=[["运维/备份策略.txt", 2, "增量备份：每天 02:00，保留 14 份"], ["运维/备份策略.txt.bak", 2, "增量备份：每天 02:00，保留 7 份"]],
        prompt="按 运维/备份策略.txt，每天的增量备份要保留几份？", want=["14", "十四"], decoy="7",
        task_type="policy_lookup", answer="增量备份保留 14 份（.bak 里 7 份是 2025 年旧版）。", scen_tags=("OBS", "CHN"),
        alts=["运维/备份策略.txt 规定增量备份保留多少份？", "日增量备份留几份？看 运维/备份策略.txt。", "备份策略里每天的增量备份保留份数是多少？",
              "查一下 运维/备份策略.txt：增量备份保留几份？", "增量备份的保留数量是多少，以 运维/备份策略.txt 为准。"])


def cfg_9226():
    files = {"部署/deploy.toml": lines(["[rollout]", "max_surge = 25", "timeout_seconds = 900", "", "[health]", "interval_seconds = 15"]),
             "部署/deploy.toml.orig": lines(["[rollout]", "max_surge = 10", "timeout_seconds = 600", "", "[health]", "interval_seconds = 30"])}
    return read_case(
        "cfg-9226", topic="rollouttimeout", desc="Single-file rollout timeout lookup in a toml file with an .orig decoy while bash is offered but forbidden",
        files=files, checks=[["部署/deploy.toml", 2, "timeout_seconds = 900"], ["部署/deploy.toml.orig", 2, "timeout_seconds = 600"]],
        prompt="部署/deploy.toml 的 [rollout] 里 timeout_seconds 是多少？", want=["900"], decoy="600",
        task_type="read_effective", answer="rollout 的 timeout_seconds 是 900（deploy.toml.orig 里的 600 是旧值）。", scen_tags=("OBS", "CHN"),
        alts=["发布超时时间是多少秒？看 部署/deploy.toml 的 rollout 段。", "deploy.toml 里 rollout 超时设成了几秒？", "部署/deploy.toml：rollout 的超时秒数？",
              "帮我看看 部署/deploy.toml，发布的 timeout_seconds 是多少。", "rollout 段的 timeout_seconds 当前值是什么？"])


def doc_9227():
    files = {"docs/NEWS.md": lines(["# News", "", "## 5.2.0 (2026-09-30)", "", "- Faster cold start.", "", "## 5.1.4 (2026-09-02)", "", "- Fixes a crash on empty input."]),
             "docs/NEWS-archive.md": lines(["# News archive", "", "## 4.9.3 (2025-11-18)", "", "- Security fixes.", "", "## 4.9.2 (2025-10-21)", "", "- Minor fixes."])}
    return read_case(
        "doc-9227", topic="latestrelease", desc="Single-file latest-release lookup in a changelog with an archive decoy while bash is offered but forbidden",
        files=files, checks=[["docs/NEWS.md", 2, "## 5.2.0 (2026-09-30)"], ["docs/NEWS-archive.md", 2, "## 4.9.3 (2025-11-18)"]],
        prompt="What is the newest release listed in docs/NEWS.md?", want=["5.2.0"], decoy="4.9.3",
        task_type="policy_lookup", answer="The newest release is 5.2.0 (2026-09-30); the archive file only holds older 4.9.x entries.",
        alts=["Which version is at the top of docs/NEWS.md?", "docs/NEWS.md: what's the latest release number?", "Tell me the current release from the NEWS file in docs.",
              "What version did the most recent entry in docs/NEWS.md ship?", "Latest version according to docs/NEWS.md?"])


def cfg_9228():
    files = {"门店/价目表.txt": lines(["# 价目表（2026 年 10 月）", "美式 18 元", "拿铁 26 元", "卡布奇诺 28 元", "手冲 38 元"]),
             "门店/价目表-去年.txt": lines(["# 价目表（2025 年 10 月）", "美式 15 元", "拿铁 22 元", "卡布奇诺 24 元", "手冲 32 元"])}
    return read_case(
        "cfg-9228", topic="lattecost", desc="Single-file item price lookup with a last-year price list decoy while bash is offered but forbidden",
        files=files, checks=[["门店/价目表.txt", 2, "拿铁 26 元"], ["门店/价目表-去年.txt", 2, "拿铁 22 元"]],
        prompt="门店/价目表.txt 上拿铁现在卖多少钱？", want=["26"], decoy="22",
        task_type="read_effective", answer="拿铁 26 元（去年的价目表里是 22 元）。", scen_tags=("OBS", "CHN"),
        alts=["拿铁多少钱一杯？看 门店/价目表.txt。", "价目表.txt 里拿铁的价格是多少？", "现在一杯拿铁的售价是？以 门店/价目表.txt 为准。",
              "帮我查一下门店价目表里拿铁的价格。", "门店/价目表.txt 中拿铁标价多少元？"])


def cfg_9229():
    files = {"env/prod.env": lines(["APP_ENV=production", "SMTP_HOST=smtp.mail.internal", "SMTP_PORT=465", "SMTP_TLS=on"]),
             "env/staging.env": lines(["APP_ENV=staging", "SMTP_HOST=smtp.mail.internal", "SMTP_PORT=2525", "SMTP_TLS=off"])}
    return read_case(
        "cfg-9229", topic="smtpport", desc="Single-file SMTP port lookup in the production env file while the staging env file is the decoy and bash is forbidden",
        files=files, checks=[["env/prod.env", 2, "SMTP_PORT=465"], ["env/staging.env", 2, "SMTP_PORT=2525"]],
        prompt="env/prod.env 里 SMTP_PORT 是多少？", want=["465"], decoy="2525",
        task_type="read_effective", answer="生产环境的 SMTP_PORT 是 465（staging 用的是 2525）。", scen_tags=("OBS", "CHN"),
        alts=["生产环境发邮件用哪个端口？看 env/prod.env。", "env/prod.env 配的 SMTP 端口号是多少？", "prod.env 里的 SMTP_PORT 值是？",
              "告诉我 env/prod.env 里 SMTP_PORT 的值。", "线上邮件服务器端口是多少，以 env/prod.env 为准？"])


def doc_9230():
    files = {"ops/oncall.md": lines(["# On-call rota", "", "Week of 2026-10-12", "", "- Primary: Priya Nair", "- Secondary: Marcus Lee", "", "Escalation: page the engineering manager after 30 minutes."]),
             "ops/oncall.md.bak": lines(["# On-call rota", "", "Week of 2026-10-05", "", "- Primary: Tom Becker", "- Secondary: Aiko Tanaka", "", "Escalation: page the engineering manager after 30 minutes."])}
    return read_case(
        "doc-9230", topic="oncallprimary", desc="Single-file primary on-call lookup with a last-week .bak decoy while bash is offered but forbidden",
        files=files, checks=[["ops/oncall.md", 4, "- Primary: Priya Nair"], ["ops/oncall.md.bak", 4, "- Primary: Tom Becker"]],
        prompt="Who is the primary on-call this week according to ops/oncall.md?", want=["Priya"], decoy="Tom Becker",
        task_type="policy_lookup", answer="Priya Nair is primary on-call (the .bak file is last week's rota with Tom Becker).",
        alts=["ops/oncall.md: who holds the primary pager?", "Who's on call as primary right now? The rota is ops/oncall.md.", "Check ops/oncall.md and name the primary on-call person.",
              "Tell me the primary on-call engineer from ops/oncall.md.", "Whose name is on the Primary line in ops/oncall.md?"])


# ------------------------------------------------------------------ 9231-9236 command asked for, not to be run


def snippet_case(cid, *, topic, desc, files, prompt, contains, answer, alts):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"] == %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (json.dumps(files, ensure_ascii=False), json.dumps(contains, ensure_ascii=False))
    notes = f"""## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or even listing the directory, breaks the request.

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
The user said not to execute; any tool call violates the request.
""" + phrasings(*alts)
    _SPEC[cid] = dict(kind="zero_call", sub="M9e")
    return write_case(
        cid, desc=desc, task_type="snippet_in_reply", family=f"fam-nt-b12i-{topic}-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": None}, axes=["DEC"], files=files, verify=verify, notes=notes,
        case_expect={"files": {p: {"unchanged": True} for p in files}},
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 700}}])


def nt_9231():
    files = {"素材/封面.psd": "placeholder 1\n", "素材/视频/开场.mov": "placeholder 2\n", "素材/音频/配乐.wav": "placeholder 3\n"}
    return snippet_case(
        "nt-9231", topic="bigfiles", desc="Asks for a find command listing files over 10 MB without running it while bash is offered",
        files=files, prompt="用 find 帮我写一条命令，列出 素材 目录下所有大于 10MB 的文件。先别跑，我看过再自己执行。",
        contains=["-size +10M", "-size +10240k", "-size +10485760c", "-size +10"], answer="`find 素材 -type f -size +10M`，提醒用户自己执行。",
        alts=["给我一条 find 命令，找出 素材 里超过 10MB 的文件，不要执行。", "素材 目录中体积大于 10M 的文件怎么用 find 列出来？写命令就行，我自己跑。",
              "我想用 find 筛出 素材 下大于 10MB 的文件，把命令写给我，别替我运行。", "请写出 find 命令：在 素材 下查找大于 10MB 的文件。只要命令，不要执行。",
              "帮我拼个 find 命令找 素材 目录里 10MB 以上的文件，先不要运行。"])


def nt_9232():
    files = {"data/sales.tsv": lines(["date\tregion\tamount", "2026-10-01\teast\t120", "2026-10-01\twest\t95", "2026-10-02\teast\t210"])}
    return snippet_case(
        "nt-9232", topic="awksum", desc="Asks for an awk command summing a tsv column without running it while bash is offered",
        files=files, prompt="Give me an awk command that sums the third column of data/sales.tsv and skips the header line. Don't run it; I'll paste it into my own terminal.",
        contains=["awk"], answer="`awk -F'\\t' 'NR>1 {s+=$3} END {print s}' data/sales.tsv`, not executed.",
        alts=["Write an awk one-liner to total column 3 of data/sales.tsv, ignoring the first line. Do not execute anything.",
              "How would I add up the amount column in data/sales.tsv with awk? Just show me the command, I'll run it myself.",
              "I need an awk command (not run by you) that sums the 3rd field of data/sales.tsv except the header.",
              "Show the awk command for the sum of the third tab-separated column in data/sales.tsv, header skipped. No running it, please.",
              "Draft an awk snippet that totals the amount column of data/sales.tsv. I'll execute it later."])


def nt_9233():
    files = {"conf/site.conf": lines(["# main site", "server {", "    listen 80;", "", "    # static files", "    root /srv/www;", "}"])}
    return snippet_case(
        "nt-9233", topic="sedstrip", desc="Asks for a sed command stripping comment and blank lines without running it while bash is offered",
        files=files, prompt="我想把 conf/site.conf 里以 # 开头的注释行和空行都删掉，结果输出到屏幕就行，别改原文件。给我 sed 命令，不要执行，我想先过目。",
        contains=["sed"], answer="`sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' conf/site.conf`（不带 -i，不改原文件），不执行。",
        alts=["写一条 sed 命令，去掉 conf/site.conf 的注释行和空行，只在终端显示，不要改文件。先别运行。", "怎么用 sed 过滤掉 conf/site.conf 里 # 开头的行和空白行？给命令就行，我自己执行。",
              "给我一个 sed 命令：输出 conf/site.conf 去掉注释和空行后的内容。不用你跑。", "我要预览 conf/site.conf 去掉注释行、空行之后的样子，请写出 sed 命令，先不要执行。",
              "帮我写 sed 命令删除 conf/site.conf 中的注释与空行（不改原文件），只要命令，不要运行。"])


def nt_9234():
    files = {"reports/q3-summary.txt": "Third quarter revenue summary, final.\n", "reports/q4-summary.txt": "Fourth quarter revenue summary, final.\n", "reports/tmp/draft-notes.txt": "half-written outline, do not ship\n"}
    return snippet_case(
        "nt-9234", topic="tarexclude", desc="Asks for a tar command archiving a folder with an exclusion without running it while bash is offered",
        files=files, prompt="What tar command would pack the reports directory into reports.tar.gz while leaving out everything under reports/tmp? Just tell me, don't execute anything.",
        contains=["--exclude"], answer="`tar -czf reports.tar.gz --exclude='reports/tmp' reports`, not executed.",
        alts=["Write the tar command that compresses reports into reports.tar.gz but skips reports/tmp. Do not run it.", "I want a gzip tarball of the reports folder without the tmp subfolder. Give me the command; I'll run it.",
              "Show me how to create reports.tar.gz from reports, excluding reports/tmp. No execution please.", "Which tar invocation archives reports (minus reports/tmp) into a .tar.gz? Command only, nothing run.",
              "Draft a tar command for reports.tar.gz that leaves out reports/tmp; I will run it on my side."])


def nt_9235():
    files = {"data/a/x.bin": "x\n", "data/b/y.bin": "y\n", "data/c/z.bin": "z\n"}
    return snippet_case(
        "nt-9235", topic="dutop", desc="Asks for a du pipeline listing the largest subdirectories without running it while bash is offered",
        files=files, prompt="想看 data 目录下占空间最大的 5 个子目录，帮我写个命令（du 配 sort 和 head 之类的），不要执行，把命令给我就行。",
        contains=["sort -rh", "sort -hr", "sort -h", "sort -nr", "sort -rn", "sort -r"], answer="`du -sh data/*/ | sort -rh | head -5`，不执行。",
        alts=["给我一个命令，列出 data 里最占空间的前五个子目录。别运行，我自己跑。", "怎么用 du 找出 data 下体积最大的 5 个子目录？写出命令即可，不要执行。",
              "写个 du 加 sort 的命令，查看 data 目录里最大的五个子目录，先不执行。", "我想知道 data 下哪五个子目录最大，请只给出命令，不要替我运行。",
              "帮忙拼一条命令：按大小倒序显示 data 的前 5 个子目录，只写命令。"])


def nt_9236():
    files = {"notes/release-checklist.txt": lines(["Tag v2.0 shipped on 2026-08-30.", "Next: list what changed since the tag before writing the notes."])}
    return snippet_case(
        "nt-9236", topic="gitnames", desc="Asks for a git command listing files changed since a tag without running it while bash is offered",
        files=files, prompt="I need a git command that lists just the names of the files changed between the tag v2.0 and HEAD. I'm not in the repo right now, so don't run anything; just write the command.",
        contains=["--name-only", "--name-status"], answer="`git diff --name-only v2.0 HEAD`, not executed.",
        alts=["Which git command shows only file names changed from v2.0 to HEAD? Command only, no execution.", "Write git diff (or similar) listing the files that differ between tag v2.0 and HEAD, names only. Don't run it.",
              "Give me the command to see changed filenames since v2.0 in git. I'll run it later; you shouldn't.", "How do I list the files modified since the v2.0 tag with git? Just the command, please, nothing executed.",
              "Draft a git command: names of files changed between v2.0 and HEAD. Do not execute it."])


# ------------------------------------------------------------------ 9237-9240 two turns: no-bash read, then bash aggregate


def two_turn(cid, *, desc, task_type, family, level, files, body, cmd, want, traps, decoys, trap_note, ref1, prompts, expects, alts, needs):
    verify = ('import json\ncase = json.load(open("case.json"))\n' + body.strip("\n") + "\n")
    notes = f"""## Traps
{trap_note}

## Reference solution
Turn 1: {ref1}
Turn 2:
1. bash: `{cmd}`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, the read tool is the direct read. Turn 2 spans several files, where one pipeline beats opening them one by one.
""" + phrasings(*alts)
    REFS[cid] = (files, [cmd], has(*want))
    _SPEC[cid] = dict(kind="bash_aggregate", sub="M9a", needs=needs)
    return write_case(
        cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=2, traps=traps, decoys=decoys, axes=["OBS", "CHN"],
        files=files, verify=verify, notes=notes, turns=[{"prompt": p, "expect": e} for p, e in zip(prompts, expects)])


def tab_9237():
    for seed in range(300):
        rng = Random(9237 + seed * 7919)
        cats = ["差旅", "差旅", "差旅补贴", "餐饮", "办公"]
        files, total, loose = {}, 0, 0
        for m in range(4, 10):
            rows = []
            for _ in range(rng.randint(70, 110)):
                c, v = rng.choice(cats), rng.randint(20, 900)
                rows.append(f"2026-{m:02d}-{rng.randint(1, 28):02d} {c} {v}")
                total += v * (c == "差旅")
                loose += v * c.startswith("差旅")
            files[f"报销/2026-{m:02d}.txt"] = lines(rows)
        files["报销/说明.md"] = lines(["# 报销说明", "", "每月一个 .txt 文件，每行三列：日期、类别、金额（元，整数），用空格分隔。", "类别按完整名称匹配，「差旅补贴」不是「差旅」。"])
        files["联系人.txt"] = lines(["# 财务部分机", "财务主管 8317", "出纳 8322", "审计 8340"])
        files["联系人-旧.txt"] = lines(["# 财务部分机（2025 年）", "财务主管 8105", "出纳 8122", "审计 8140"])
        if total >= 20000 and not any(str(total) in t for t in files.values()) and not any(str(loose) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["报销/说明.md"].startswith("# 报销说明")
assert case["files"]["联系人.txt"].splitlines()[1] == "财务主管 8317"
assert case["files"]["联系人-旧.txt"].splitlines()[1] == "财务主管 8105"
n = 0
for path, text in case["files"].items():
    if path.startswith("报销/2026-") and path.endswith(".txt"):
        for r in text.splitlines():
            d, c, v = r.split(" ")
            n += int(v) * (c == "差旅")
print(json.dumps({"expected_contains_any": ["8317"] + [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}))
'''
    cmd = """cat 报销/2026-*.txt | awk '$2=="差旅" {s+=$3} END{print s}'"""
    return two_turn(
        "tab-9237", desc="Two turns: the finance supervisor's extension from one named file, then the total 差旅 expense over six monthly txt files with a look-alike category",
        task_type="aggregate", family="fam-tab-b12i-travelsum-01", level="L3", files=files, body=body, cmd=cmd, want=[str(total)],
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": "8317", "TR-DECOY": str(loose)},
        trap_note="- TR-DECOY: 联系人-旧.txt has an old extension; 「差旅补贴」 shares the prefix with 差旅 and must not be summed. TR-MULTISRC: six monthly files, README in 报销/说明.md.",
        ref1="read_file 联系人.txt -> 财务主管 分机 8317.", needs=["报销/说明.md"],
        prompts=["联系人.txt 里财务主管的分机号是多少？", "报销目录里 4 到 9 月的文件，类别为差旅的金额一共多少元？统计口径见 报销/说明.md。"],
        expects=[{"output_contains_any": ["8317"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains_any": thousands(total), "max_output_chars": 600}],
        alts=["把六个月里差旅类的报销金额加起来", "报销/ 下各月文件中 差旅 的合计是多少", "4-9 月差旅报销总额（不含差旅补贴）", "各月报销文件里类别是差旅的钱一共多少", "What is the total of the 差旅 category across the monthly files in 报销?"])


def log_9238():
    for seed in range(300):
        rng = Random(9238 + seed * 7919)
        tags = ["TODO", "TODO", "TODO-later", "DONE", "NOTE", "NOTE"]
        files, count, loose = {}, 0, 0
        for w in range(1, 7):
            rows = []
            for _ in range(rng.randint(60, 90)):
                t = rng.choice(tags)
                rows.append(f"[{t}] item {rng.randint(100, 999)}")
                count += t == "TODO"
                loose += t.startswith("TODO")
            files[f"notes/week-{w}.txt"] = lines(rows)
        files["notes/README.md"] = lines(["# Notes", "", "One txt file per week. Every line starts with a bracketed tag: [TODO], [TODO-later], [DONE] or [NOTE].", "[TODO-later] is parked work and is not a TODO."])
        files["team/RULES.md"] = lines(["# Team rules", "", "- Merging requires 2 approvals.", "- Hotfixes need 1 approval from the on-call engineer."])
        files["team/RULES.md.bak"] = lines(["# Team rules", "", "- Merging requires 1 approval.", "- Hotfixes need no approval."])
        if count >= 100 and not any(str(count) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["notes/README.md"].startswith("# Notes")
assert case["files"]["team/RULES.md"].splitlines()[2] == "- Merging requires 2 approvals."
assert case["files"]["team/RULES.md.bak"].splitlines()[2] == "- Merging requires 1 approval."
n = 0
for path, text in case["files"].items():
    if path.startswith("notes/week-") and path.endswith(".txt"):
        for r in text.splitlines():
            assert r.startswith("["), r
            n += r.startswith("[TODO] ")
print(json.dumps({"expected_number": n}))
'''
    cmd = "cat notes/week-*.txt | grep -c '^\\[TODO\\] '"
    return two_turn(
        "log-9238", desc="Two turns: the merge approval count from one named rules file, then counting [TODO] lines over six weekly txt files with a look-alike parked tag",
        task_type="count_events", family="fam-log-b12i-todocount-01", level="L3", files=files, body=body, cmd=cmd, want=[str(count)],
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": "2", "TR-DECOY": str(loose)},
        trap_note="- TR-DECOY: team/RULES.md.bak has the old approval count; [TODO-later] lines start with the same word but are not TODO. TR-MULTISRC: six weekly files, README in notes/README.md.",
        ref1="read_file team/RULES.md -> merging requires 2 approvals.", needs=["notes/README.md"],
        prompts=["How many approvals does a pull request need according to team/RULES.md?", "Across the weekly files in notes, how many lines are [TODO] items? notes/README.md explains the tags."],
        expects=[{"output_contains_any": ["2", "two"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains": [str(count)], "output_contains_token": True, "max_output_chars": 600}],
        alts=["Count the [TODO] lines over all six notes files.", "How many open TODO entries do the weekly notes hold in total (parked ones excluded)?", "Total number of [TODO] tagged lines in notes/week-*.txt?",
              "Across weeks 1 to 6, how many items are tagged TODO and not TODO-later?", "统计 notes 下各周文件里标记为 [TODO] 的行数"])


def tab_9239():
    for seed in range(300):
        rng = Random(9239 + seed * 7919)
        states = ["已交", "已交", "已交", "缺交", "缺交已补", "请假"]
        files, miss, loose = {}, 0, 0
        for w in range(1, 7):
            rows = []
            for sid in range(2601, 2601 + rng.randint(55, 75)):
                s = rng.choice(states)
                rows.append(f"{sid} {rng.choice('赵钱孙李周吴郑王')}{rng.choice('明华强丽静磊敏')} {s}")
                miss += s == "缺交"
                loose += s.startswith("缺交")
            files[f"作业/第{w}周.txt"] = lines(rows)
        files["作业/说明.md"] = lines(["# 作业记录说明", "", "每周一个 .txt 文件，每行三列：学号、姓名、状态，用空格分隔。", "状态取值：已交、缺交、缺交已补、请假。只有「缺交」才算没交，「缺交已补」已经补交。"])
        files["课程表.md"] = lines(["# 课程表（本学期）", "", "周一 第一节：语文", "周二 第二节：英语", "周三 第二节：线性代数", "周四 第三节：物理"])
        files["课程表-上学期.md"] = lines(["# 课程表（上学期）", "", "周一 第一节：语文", "周二 第二节：英语", "周三 第二节：高等数学", "周四 第三节：化学"])
        if miss >= 80 and not any(str(miss) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["作业/说明.md"].startswith("# 作业记录说明")
assert case["files"]["课程表.md"].splitlines()[4] == "周三 第二节：线性代数"
assert case["files"]["课程表-上学期.md"].splitlines()[4] == "周三 第二节：高等数学"
n = 0
for path, text in case["files"].items():
    if path.startswith("作业/第") and path.endswith(".txt"):
        for r in text.splitlines():
            sid, name, s = r.split(" ")
            n += s == "缺交"
print(json.dumps({"expected_contains_any": ["线性代数"] + [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}, ensure_ascii=False))
'''
    cmd = """cat 作业/第*.txt | awk '$3=="缺交" {n++} END{print n}'"""
    return two_turn(
        "tab-9239", desc="Two turns: Wednesday's second class from one named timetable, then counting 缺交 records over six weekly txt files with a look-alike status",
        task_type="filter_count", family="fam-tab-b12i-missedwork-01", level="L3", files=files, body=body, cmd=cmd, want=[str(miss)],
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": "线性代数", "TR-DECOY": str(loose)},
        trap_note="- TR-DECOY: 课程表-上学期.md has last term's class; 「缺交已补」 starts with 缺交 but was handed in later. TR-MULTISRC: six weekly files, README in 作业/说明.md.",
        ref1="read_file 课程表.md -> 周三第二节 is 线性代数.", needs=["作业/说明.md"],
        prompts=["课程表.md 里周三第二节是什么课？", "作业目录里六周的记录，状态为缺交的一共有多少条？口径见 作业/说明.md。"],
        expects=[{"output_contains_any": ["线性代数"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains_any": thousands(miss), "max_output_chars": 600}],
        alts=["六周里没交作业的记录总共多少条", "作业/第*.txt 里状态是缺交的行数", "统计缺交（不含缺交已补）的记录总数", "这六周一共有多少次缺交", "How many 缺交 records are there across the six weekly files?"])


def log_9240():
    for seed in range(300):
        rng = Random(9240 + seed * 7919)
        plats = ["linux", "linux", "linux-arm", "macos", "windows"]
        files, total, loose = {}, 0, 0
        for m in range(5, 11):
            rows = []
            for _ in range(rng.randint(55, 80)):
                p, v = rng.choice(plats), rng.randint(5, 400)
                rows.append(f"{p} {v}")
                total += v * (p == "linux")
                loose += v * p.startswith("linux")
            files[f"stats/2026-{m:02d}.txt"] = lines(rows)
        files["stats/README.md"] = lines(["# Download stats", "", "One txt file per month. Each line is: platform, then the number of downloads in one batch, separated by a space.",
                                          "Platform names match exactly: linux-arm is a different platform from linux."])
        files["release/NEXT.md"] = lines(["# Next release", "", "codename: Harbor", "target: 2026-11-15"])
        files["release/NEXT.md.bak"] = lines(["# Next release", "", "codename: Lantern", "target: 2026-10-01"])
        if total >= 20000 and not any(str(total) in t for t in files.values()) and not any(str(loose) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["stats/README.md"].startswith("# Download stats")
assert case["files"]["release/NEXT.md"].splitlines()[2] == "codename: Harbor"
assert case["files"]["release/NEXT.md.bak"].splitlines()[2] == "codename: Lantern"
n = 0
for path, text in case["files"].items():
    if path.startswith("stats/2026-") and path.endswith(".txt"):
        for r in text.splitlines():
            p, v = r.split(" ")
            n += int(v) * (p == "linux")
print(json.dumps({"expected_contains_any": [str(n)] + (["{:,}".format(n)] if n >= 1000 else [])}))
'''
    cmd = """cat stats/2026-*.txt | awk '$1=="linux" {s+=$2} END{print s}'"""
    return two_turn(
        "log-9240", desc="Two turns: the next release codename from one named file, then summing linux downloads over six monthly txt files with a look-alike platform",
        task_type="count_events", family="fam-log-b12i-linuxdl-01", level="L3", files=files, body=body, cmd=cmd, want=[str(total)],
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": "Harbor", "TR-DECOY": str(loose)},
        trap_note="- TR-DECOY: release/NEXT.md.bak has the old codename; linux-arm lines share the prefix with linux and must not be summed. TR-MULTISRC: six monthly files, README in stats/README.md.",
        ref1="read_file release/NEXT.md -> codename Harbor.", needs=["stats/README.md"],
        prompts=["What is the codename in release/NEXT.md?", "Using the monthly files in stats, how many downloads were there in total for the linux platform? stats/README.md describes the format."],
        expects=[{"output_contains": ["Harbor"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains_any": thousands(total), "max_output_chars": 600}],
        alts=["Sum the linux downloads over May to October.", "Total downloads for exactly the linux platform across stats/2026-*.txt?", "How many linux downloads in all six months (linux-arm excluded)?",
              "Add up every linux line's download count from the monthly stats files.", "统计 stats 下六个月文件里 linux 平台的下载量合计"])


BUILDERS = [cfg_9221, doc_9222, cfg_9223, doc_9224, doc_9225, cfg_9226, doc_9227, cfg_9228, cfg_9229, doc_9230,
            nt_9231, nt_9232, nt_9233, nt_9234, nt_9235, nt_9236,
            tab_9237, log_9238, tab_9239, log_9240]

SPEC = {'cfg-9221': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'cfg-9223': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'cfg-9226': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'cfg-9228': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'cfg-9229': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'doc-9222': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'doc-9224': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'doc-9225': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'doc-9227': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'doc-9230': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
 'log-9238': {'kind': 'bash_aggregate', 'needs': ['notes/README.md'], 'sub': 'M9a'},
 'log-9240': {'kind': 'bash_aggregate', 'needs': ['stats/README.md'], 'sub': 'M9a'},
 'nt-9231': {'kind': 'zero_call', 'sub': 'M9e'},
 'nt-9232': {'kind': 'zero_call', 'sub': 'M9e'},
 'nt-9233': {'kind': 'zero_call', 'sub': 'M9e'},
 'nt-9234': {'kind': 'zero_call', 'sub': 'M9e'},
 'nt-9235': {'kind': 'zero_call', 'sub': 'M9e'},
 'nt-9236': {'kind': 'zero_call', 'sub': 'M9e'},
 'tab-9237': {'kind': 'bash_aggregate', 'needs': ['报销/说明.md'], 'sub': 'M9a'},
 'tab-9239': {'kind': 'bash_aggregate', 'needs': ['作业/说明.md'], 'sub': 'M9a'}}
