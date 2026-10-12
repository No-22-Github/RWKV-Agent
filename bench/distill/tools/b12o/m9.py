"""M9 (bash) negative / zero-call batch b12o of v1.41: ids 9361-9380.

M9e only: 8 reply-only how-to-command cases (tools [], no call), 6 single named-file lookups with bash
forbidden, 6 named-file lookups where bash is allowed but one read is the right action. Every lookup file
has an in-file look-alike and/or an outdated sibling copy."""
import json

from common import lines
from common import write_case as _write_case

REFS = {}
_SPEC = {}
READ = ("read_file", "read_lines", "search_text")


def write_case(cid, *, files, verify, **kw):
    """Adds a per-file line-count guard so deleting any fixture line breaks verify."""
    if "LINES = " not in verify:
        guard = "LINES = %r\nfor _p, _n in LINES.items():\n    assert len(case[\"files\"][_p].splitlines()) == _n, _p\n" % {p: len(t.splitlines()) for p, t in files.items()}
        verify = verify.replace('case = json.load(open("case.json"))\n', 'case = json.load(open("case.json"))\n' + guard, 1)
    return _write_case(cid, files=files, verify=verify, **kw)


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


# ------------------------------------------------------------------ how-to-command, reply only


def howto(cid, *, topic, desc, files, prompt, contains, answer, alts, ref=None):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"] == %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (json.dumps(files, ensure_ascii=False), json.dumps(contains, ensure_ascii=False))
    notes = f"""## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or listing/reading the files first, breaks the request.

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
The user said not to run anything; any tool call violates the request. The reply must contain the command (one of {contains}).
""" + phrasings(*alts)
    if ref:
        REFS[cid] = (files, [ref[0]], has(*ref[1]))
    _SPEC[cid] = dict(kind="zero_call", sub="M9e")
    return write_case(
        cid, desc=desc, task_type="snippet_in_reply", family=f"fam-nt-b12o-{topic}-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": None}, axes=["DEC"], files=files, verify=verify, notes=notes,
        case_expect={"files": {p: {"unchanged": True} for p in files}},
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 700}}])


def nt_9361():
    files = {"项目/src/main.py": "print('hi')\n", "项目/docs/README.md": "# 项目说明\n", "项目/notes/todo.txt": "整理目录\n"}
    return howto(
        "nt-9361", topic="emptydirs", desc="Asks for a find command listing empty directories without running it while bash is offered",
        files=files, prompt="项目 目录里有一堆建完没放东西的空文件夹，帮我写一条命令把它们的路径列出来。先别运行，我想自己看一眼再执行。",
        contains=["-empty"], answer="`find 项目 -type d -empty`，提醒用户自己执行。",
        alts=["写一条命令列出 项目 目录下所有空文件夹，只要路径，不要执行。",
              "怎么用命令找出 项目 里的空目录？写出来就行，我自己跑。",
              "给我一条能把 项目 目录中没有任何内容的文件夹列出来的命令，先别运行。",
              "我想清理 项目 里的空目录，先给我列出它们的命令，别帮我执行。",
              "请只告诉我命令：列出 项目 下的空目录。不用运行。"])


def nt_9362():
    files = {"src/a.c": "// SPDX-License-Identifier: MIT\nint a(void){return 1;}\n", "src/b.c": "int b(void){return 2;}\n", "src/util/c.c": "// SPDX-License-Identifier: MIT\nint c(void){return 3;}\n"}
    return howto(
        "nt-9362", topic="spdxmissing", desc="Asks for a grep command listing files that lack a license header without running it while bash is offered",
        files=files, prompt="Which files under src are missing an SPDX-License-Identifier header? Give me a grep command that prints just those file names. Please don't run it, I'm going to paste it into my CI script.",
        contains=["-L", "--files-without-match"], answer="`grep -rL 'SPDX-License-Identifier' src`, noting that -L lists files with no match.",
        alts=["Write me a grep one-liner that lists the files in src without an SPDX-License-Identifier line. Don't execute it.",
              "I need a command (not run) that prints every file under src that doesn't contain SPDX-License-Identifier.",
              "How would I use grep to list source files in src lacking the SPDX header? Just the command, I'll run it myself.",
              "Give me the grep invocation for 'files under src with no SPDX-License-Identifier'. No running anything, please.",
              "For my CI check: a command that outputs the names of files in src that have no SPDX-License-Identifier. Only write it, don't run it."],
        ref=("grep -rL SPDX-License-Identifier src", ["src/b.c"]))


def nt_9363():
    files = {"config/server.ini": lines(["setting_%02d=value_%02d" % (i, i) for i in range(1, 26)])}
    return howto(
        "nt-9363", topic="sedrange", desc="Asks for a sed command printing a line range without running it while bash is offered",
        files=files, prompt="我想只看 config/server.ini 的第 10 到 20 行，用 sed 写一条命令。别帮我跑，写出来我自己执行。",
        contains=["10,20p"], answer="`sed -n '10,20p' config/server.ini`，并说明 -n 抑制默认输出。",
        alts=["用 sed 怎么只打印 config/server.ini 的第 10 到第 20 行？只给命令，不要执行。",
              "写一条 sed 命令，输出 config/server.ini 第 10-20 行，我自己跑。",
              "config/server.ini 我只关心 10 到 20 行，给我 sed 命令，先别运行。",
              "请给出用 sed 截取 config/server.ini 第 10 行到第 20 行的命令，不用执行。",
              "sed 怎么截取文件的第 10 至 20 行？以 config/server.ini 为例，写出命令就行。"],
        ref=("sed -n '10,20p' config/server.ini", ["setting_10", "setting_20"]))


def nt_9364():
    files = {"logs/access.log": lines(['10.0.0.1 - - [12/Oct/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 512',
                                       '10.0.0.2 - - [12/Oct/2026:10:00:02 +0000] "GET /old-page HTTP/1.1" 404 128',
                                       '10.0.0.3 - - [12/Oct/2026:10:00:03 +0000] "GET /api/v1/items HTTP/1.1" 200 2048',
                                       '10.0.0.2 - - [12/Oct/2026:10:00:04 +0000] "GET /missing.png HTTP/1.1" 404 128'])}
    return howto(
        "nt-9364", topic="awk404", desc="Asks for an awk command printing paths of 404 lines without running it while bash is offered",
        files=files, prompt="My web server log is at logs/access.log and the HTTP status is field 9. Write an awk command that prints the requested path (field 7) only for lines whose status is 404. I'll run it myself, so don't execute anything.",
        contains=["$9"], answer="`awk '$9 == 404 {print $7}' logs/access.log`.",
        alts=["Give me an awk one-liner for logs/access.log that outputs field 7 where field 9 equals 404. Do not run it.",
              "What awk command lists the paths (column 7) of requests that returned 404 in logs/access.log? Just write it out.",
              "I want the 404 request paths from logs/access.log (status is column 9, path column 7). Command only, no execution.",
              "Write the awk filter that prints $7 when $9 is 404 for logs/access.log; I'll run it on my side.",
              "Need an awk command: from logs/access.log, show the path of every 404 response. Don't run anything."],
        ref=("awk '$9==404 {print $7}' logs/access.log", ["/old-page", "/missing.png"]))


def nt_9365():
    files = {"备份/说明.txt": lines(["backup-2026-10.tar.gz 由夜间任务生成。", "内容：conf/ 与 data/ 两个顶层目录。"])}
    return howto(
        "nt-9365", topic="tarextractdir", desc="Asks for a tar command extracting one directory from an archive without running it while bash is offered",
        files=files, prompt="backup-2026-10.tar.gz 里有 conf/ 和 data/ 两个目录，我只想把 conf/ 解压到 /tmp/restore。写一条 tar 命令，先不要运行，我确认路径后自己执行。",
        contains=["xzf", "zxf", "xvzf", "zxvf", "tar -x", "tar x", "--extract"], answer="`mkdir -p /tmp/restore && tar -xzf backup-2026-10.tar.gz -C /tmp/restore conf/`。",
        alts=["怎么只从 backup-2026-10.tar.gz 里解出 conf/ 目录到 /tmp/restore？写 tar 命令，别执行。",
              "给我一条 tar 命令：把 backup-2026-10.tar.gz 中的 conf/ 解压到 /tmp/restore，不要运行。",
              "tar 能不能只解压压缩包里的 conf/？命令写出来，目标目录 /tmp/restore，我自己跑。",
              "我只要备份包 backup-2026-10.tar.gz 里的 conf 目录，解压到 /tmp/restore，请给命令但不要执行。",
              "请写出局部解压的 tar 命令：来源 backup-2026-10.tar.gz，只取 conf/，放到 /tmp/restore；只写不跑。"])


def nt_9366():
    files = {"README.txt": "Photo mirror notes: originals live in ~/photos, the backup disk mounts at /mnt/backup.\n"}
    return howto(
        "nt-9366", topic="mirrorsync", desc="Asks for a mirroring command with a dry-run option without running it while bash is offered",
        files=files, prompt="I keep my photos in ~/photos and want to mirror them to /mnt/backup/photos, copying only what changed. Give me the command with a dry run so I can preview what it would do. Don't run it, I'll do that after reading it.",
        contains=["rsync"], answer="`rsync -av --dry-run ~/photos/ /mnt/backup/photos/`, then rerun without --dry-run.",
        alts=["What command mirrors ~/photos to /mnt/backup/photos copying only changed files, with a preview mode? Only write it, don't run it.",
              "Show me an incremental sync from ~/photos to /mnt/backup/photos, including a dry-run flag. No execution.",
              "I want to back up ~/photos to /mnt/backup/photos and only transfer differences. Write the command with a preview option; I'll run it.",
              "Command please (not executed): sync ~/photos into /mnt/backup/photos, updating only what changed, with a dry run first.",
              "Give me a sync command for ~/photos -> /mnt/backup/photos that skips unchanged files and can preview first. Just the command."])


def nt_9367():
    files = {"名单/报名表.txt": lines(["王芳", "李强", "张敏", "王芳", "赵磊", "李强", "王芳", "孙悦"])}
    return howto(
        "nt-9367", topic="dupnames", desc="Asks for a sort and uniq command listing repeated names without running it while bash is offered",
        files=files, prompt="名单/报名表.txt 里有人重复报名了。写一条命令，只列出重复出现的姓名，每个姓名只出现一次。别执行，我先放进脚本里。",
        contains=["uniq -d", "uniq -D", "awk"], answer="`sort 名单/报名表.txt | uniq -d`。",
        alts=["用命令把 名单/报名表.txt 里出现不止一次的姓名找出来，每个只显示一次。只写命令，不要跑。",
              "写一条命令，列出 名单/报名表.txt 中重复的名字（去重后显示）。先不要执行。",
              "怎么找 名单/报名表.txt 里重复报名的人？给出命令，我自己执行。",
              "给我一个 sort 加 uniq 的组合命令，输出 名单/报名表.txt 中重复的姓名。不要运行。",
              "报名表里有重复姓名，请写出只显示这些重复姓名的命令，不用运行它。"],
        ref=("sort 名单/报名表.txt | uniq -d", ["王芳", "李强"]))


def nt_9368():
    files = {"docs/guide.md": "# Guide\n\nline\n", "docs/api/ref.md": "# Ref\n", "docs/notes final.md": "# Notes\n"}
    return howto(
        "nt-9368", topic="xargswc", desc="Asks for a find and xargs pipeline counting lines of markdown files without running it while bash is offered",
        files=files, prompt="Give me a pipeline using find and xargs that prints the line count of every .md file under docs, with a total at the end. Some file names contain spaces, so make it safe. Don't run it, I'm only after the command.",
        contains=["xargs"], answer="`find docs -name '*.md' -print0 | xargs -0 wc -l`.",
        alts=["Write a find | xargs command that shows line counts for all .md files in docs and handles spaces in names. Don't execute it.",
              "How do I count lines in every markdown file under docs using xargs, safely for names with spaces? Command only.",
              "I need a find piped to xargs wc -l for the .md files under docs, space-safe. Just give it to me, no running.",
              "Compose a null-delimited find/xargs line-count command for docs/*.md (recursive). I'll run it myself.",
              "Command, not output: line counts of every .md under docs via xargs, robust to spaces in file names."],
        ref=("find docs -name '*.md' | xargs wc -l", ["guide.md"]))


# ------------------------------------------------------------------ named-file lookups


def lookup(cid, *, topic, desc, task_type, files, path, needles, prompt, answers, decoy, ref, alts, forbid, why, axes, answer_text, scenario_note=""):
    """needles: substrings that must stay in `path` (answer line) and the decoy lines in other files."""
    verify = '''
import json
case = json.load(open("case.json"))
NEEDLES = %s
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (json.dumps(needles, ensure_ascii=False), json.dumps(answers, ensure_ascii=False))
    notes = f"""## Traps
- TR-DECOY: {scenario_note}

## Reference solution
1. read_file {path}
Final answer: {answer_text}

## Why the answer is unique
The user names {path}; only its live line holds the answer. {why}
Why bash is not the tool here: one named file and one fact, read_file is the direct read.{" The turn forbids bash." if forbid else " Bash is offered, but a shell call would be wasted effort."}
""" + phrasings(*alts)
    REFS[cid] = (files, [ref], has(*answers[:1]))
    _SPEC[cid] = dict(kind="bash_avoided", sub="M9e", via=READ)
    expect = {"output_contains_any": answers, "max_output_chars": 600}
    if forbid:
        expect["forbidden_tools"] = ["bash"]
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12o-{topic}-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": decoy}, axes=axes, files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": expect}])


def cfg_9369():
    files = {"deploy/limits.toml": lines(["# 各组件内存与 CPU 上限", "[api]", "memory_mb = 1024", "cpu_cores = 2", "", "[worker]", "memory_mb = 768", "cpu_cores = 1", "", "[worker-canary]", "memory_mb = 512", "cpu_cores = 1"]),
             "deploy/limits.toml.old": lines(["[api]", "memory_mb = 512", "", "[worker]", "memory_mb = 256"])}
    return lookup(
        "cfg-9369", topic="workermem", desc="Reads one memory limit from a toml file with a look-alike section and an outdated copy, bash forbidden", task_type="read_effective",
        files=files, path="deploy/limits.toml", needles=[["deploy/limits.toml", "[worker]\nmemory_mb = 768"], ["deploy/limits.toml", "[worker-canary]\nmemory_mb = 512"], ["deploy/limits.toml.old", "memory_mb = 256"]],
        prompt="deploy/limits.toml 里 [worker] 段的 memory_mb 是多少？", answers=["768"], decoy="512",
        ref="grep -A1 '^\\[worker\\]' deploy/limits.toml", alts=["看一下 deploy/limits.toml，worker 的内存上限（MB）设的是多少？", "deploy/limits.toml 中 worker 组件的 memory_mb 写的几？", "按 deploy/limits.toml，[worker] 能用多少 MB 内存？", "worker 的内存配额是多少？以 deploy/limits.toml 为准。", "帮我查 deploy/limits.toml：[worker] 段 memory_mb。"],
        forbid=True, why="[worker-canary] shares the key (512) and limits.toml.old is stale (256).", axes=["OBS", "CHN"], answer_text="[worker] 段的 memory_mb 是 768（canary 段是 512，不是 worker 本身）。",
        scenario_note="the [worker-canary] section has the same key with 512; limits.toml.old says 256.")


def cfg_9370():
    cur = ["image:", "  repository: registry.local/web", '  tag: "1.8.2"', "resources:", "  requests:", "    cpu: 250m", "    memory: 256Mi", "  limits:", "    cpu: 500m", "    memory: 512Mi"]
    old = ["resources:", "  requests:", "    cpu: 100m", "  limits:", "    cpu: 1000m"]
    files = {"charts/web/values.yaml": lines(cur), "charts/web/values.yaml.orig": lines(old)}
    return lookup(
        "cfg-9370", topic="cpulimit", desc="Reads a CPU limit from a values yaml with a requests look-alike and an .orig copy, bash forbidden", task_type="read_effective",
        files=files, path="charts/web/values.yaml", needles=[["charts/web/values.yaml", "  limits:\n    cpu: 500m"], ["charts/web/values.yaml", "  requests:\n    cpu: 250m"], ["charts/web/values.yaml.orig", "cpu: 1000m"]],
        prompt="charts/web/values.yaml 里 CPU 的 limit 设成多少？", answers=["500m"], decoy="250m",
        ref="grep -A2 'limits:' charts/web/values.yaml", alts=["charts/web/values.yaml 的 resources.limits.cpu 是多少？", "web 这个 chart 的 CPU 上限（limits）写的是什么？看 charts/web/values.yaml。", "values.yaml（charts/web 下）里 limits 的 cpu 值是多少？", "请查 charts/web/values.yaml：容器 CPU limit 是？", "charts/web/values.yaml 给 CPU 限制了多少？"],
        forbid=True, why="requests.cpu is 250m and values.yaml.orig says 1000m.", axes=["OBS", "CHN"], answer_text="CPU limit 是 500m（requests 是 250m；.orig 里的 1000m 是旧值）。",
        scenario_note="requests.cpu 250m sits next to limits.cpu 500m; values.yaml.orig says 1000m.")


def cfg_9371():
    files = {"config/prod.env": lines(["APP_ENV=production", "# CACHE_TTL_SECONDS=60", "CACHE_TTL_SECONDS=300", "SESSION_TTL_SECONDS=3600", "LOG_FORMAT=json"]),
             "config/prod.env.example": lines(["APP_ENV=production", "CACHE_TTL_SECONDS=120", "SESSION_TTL_SECONDS=1800"])}
    return lookup(
        "cfg-9371", topic="cachettl", desc="Reads a cache TTL from an env file with a commented-out line and an example copy, bash forbidden", task_type="read_effective",
        files=files, path="config/prod.env", needles=[["config/prod.env", "\nCACHE_TTL_SECONDS=300\n"], ["config/prod.env", "# CACHE_TTL_SECONDS=60"], ["config/prod.env.example", "CACHE_TTL_SECONDS=120"]],
        prompt="What cache TTL, in seconds, does config/prod.env actually set?", answers=["300"], decoy="60",
        ref="grep CACHE_TTL config/prod.env", alts=["In config/prod.env, what is CACHE_TTL_SECONDS set to?", "How long (seconds) is the cache kept according to config/prod.env?", "Check config/prod.env for the effective cache TTL.", "What value of CACHE_TTL_SECONDS is live in config/prod.env?", "config/prod.env: what's the cache time-to-live in seconds?"],
        forbid=True, why="A commented-out 60 and the .example file's 120 are not live.", axes=["OBS"], answer_text="300 seconds (the commented 60 and the example file's 120 are not in effect).",
        scenario_note="a commented-out CACHE_TTL_SECONDS=60 line in the same file and 120 in prod.env.example.")


def cfg_9372():
    files = {"conf/backup.ini": lines(["[schedule]", "hour = 3", "", "[retention]", "keep_days = 14", "", "[retention_cold]", "keep_days = 90"]),
             "conf/backup.ini.bak": lines(["[schedule]", "hour = 1", "", "[retention]", "keep_days = 7"])}
    return lookup(
        "cfg-9372", topic="keepdays", desc="Reads a retention value from an ini file with a sibling section and a .bak copy, bash forbidden", task_type="read_effective",
        files=files, path="conf/backup.ini", needles=[["conf/backup.ini", "[retention]\nkeep_days = 14"], ["conf/backup.ini", "[retention_cold]\nkeep_days = 90"], ["conf/backup.ini.bak", "keep_days = 7"]],
        prompt="conf/backup.ini 里 [retention] 这一段，备份保留多少天？", answers=["14"], decoy="90",
        ref="grep -A1 '^\\[retention\\]' conf/backup.ini", alts=["看 conf/backup.ini：普通备份保留几天（[retention] 段的 keep_days）？", "conf/backup.ini 的 [retention] keep_days 是多少？", "按 conf/backup.ini，备份默认保留多少天？", "帮我读一下 conf/backup.ini，[retention] 里写的保留天数。", "conf/backup.ini 规定的保留期限是几天？看 [retention] 段。"],
        forbid=True, why="[retention_cold] has 90 and the .bak copy has 7.", axes=["OBS", "CHN"], answer_text="[retention] 段 keep_days 为 14 天（冷备份段是 90，.bak 里的 7 是旧值）。",
        scenario_note="[retention_cold] has keep_days = 90 and conf/backup.ini.bak says 7.")


def doc_9373():
    files = {"docs/报销规则.md": lines(["# 报销规则（2026 版）", "", "- 住宿：单晚上限 600 元", "- 交通：单笔上限 300 元", "- 餐饮：单笔上限 150 元", "- 招待费需事先审批。"]),
             "docs/报销规则-2025.md": lines(["# 报销规则（2025 版，已作废）", "", "- 住宿：单晚上限 500 元", "- 餐饮：单笔上限 100 元"])}
    return lookup(
        "doc-9373", topic="mealcap", desc="Reads one reimbursement cap from the current rules with other caps and an outdated copy, bash forbidden", task_type="policy_lookup",
        files=files, path="docs/报销规则.md", needles=[["docs/报销规则.md", "餐饮：单笔上限 150 元"], ["docs/报销规则.md", "住宿：单晚上限 600 元"], ["docs/报销规则-2025.md", "餐饮：单笔上限 100 元"]],
        prompt="docs/报销规则.md 规定单笔餐饮最多能报多少钱？", answers=["150"], decoy="100",
        ref="grep 餐饮 docs/报销规则.md", alts=["按 docs/报销规则.md，吃饭一次最多报销多少？", "餐饮报销的单笔上限是多少？看 docs/报销规则.md。", "docs/报销规则.md 里餐饮一笔能报多少元？", "我这次的餐饮发票最多能报多少，以 docs/报销规则.md 为准？", "报销规则里餐饮的单笔限额是多少？"],
        forbid=True, why="The 2025 file is void (100); other categories carry other numbers.", axes=["OBS", "CHN"], answer_text="单笔餐饮上限 150 元（2025 版的 100 元已作废）。",
        scenario_note="docs/报销规则-2025.md says 100 for meals.")


def doc_9374():
    files = {"CONTRIBUTING.md": lines(["# Contributing", "", "## Branch names", "", "- features: feature/<ticket>", "- bug fixes: patch/<ticket>", "- documentation: docs/<topic>", "", "## Commit messages", "", "Use the imperative mood."]),
             "CONTRIBUTING.old.md": lines(["# Contributing (superseded)", "", "- features: feature/<ticket>", "- bug fixes: bugfix/<ticket>"])}
    return lookup(
        "doc-9374", topic="branchprefix", desc="Reads a branch-name prefix from the current contributing guide with an outdated copy, bash forbidden", task_type="policy_lookup",
        files=files, path="CONTRIBUTING.md", needles=[["CONTRIBUTING.md", "bug fixes: patch/<ticket>"], ["CONTRIBUTING.md", "features: feature/<ticket>"], ["CONTRIBUTING.old.md", "bugfix/<ticket>"]],
        prompt="Per CONTRIBUTING.md, what prefix should a bug-fix branch name start with?", answers=["patch/"], decoy="bugfix/",
        ref="grep 'bug fixes' CONTRIBUTING.md", alts=["What does CONTRIBUTING.md say a bug-fix branch should be named?", "In CONTRIBUTING.md, which branch prefix is used for bug fixes?", "How do I name a branch for a bug fix? CONTRIBUTING.md has the rule.", "CONTRIBUTING.md: bug-fix branches start with what?", "Check CONTRIBUTING.md for the bug-fix branch naming prefix."],
        forbid=True, why="CONTRIBUTING.old.md is superseded (bugfix/).", axes=["OBS"], answer_text="Bug-fix branches start with patch/ (the superseded guide used bugfix/).",
        scenario_note="CONTRIBUTING.old.md still says bugfix/<ticket>.")


# bash allowed, one read is clearly right


def doc_9375():
    files = {"notes/纪要-1008.md": lines(["# 10 月 8 日项目例会纪要", "", "出席：周岚、陈默、吴越、郑涛", "", "## 待办", "- 数据迁移：周岚负责，10 月 20 日前完成", "- 迁移回滚演练：陈默负责，10 月 25 日前完成", "- 监控告警梳理：吴越负责，10 月 30 日前完成"]),
             "notes/纪要-1001.md": lines(["# 10 月 1 日项目例会纪要", "", "## 待办", "- 数据迁移：吴越负责（下次例会已调整）", "- 监控告警梳理：郑涛负责"])}
    return lookup(
        "doc-9375", topic="migowner", desc="Finds an owner in a named meeting note that lists other owners and an older note; bash allowed but one read suffices", task_type="extract_items",
        files=files, path="notes/纪要-1008.md", needles=[["notes/纪要-1008.md", "数据迁移：周岚负责"], ["notes/纪要-1008.md", "迁移回滚演练：陈默负责"], ["notes/纪要-1001.md", "数据迁移：吴越负责"]],
        prompt="notes/纪要-1008.md 里，数据迁移这项待办由谁负责？", answers=["周岚"], decoy="吴越",
        ref="grep 数据迁移 notes/纪要-1008.md", alts=["10 月 8 日的纪要（notes/纪要-1008.md）里数据迁移谁负责？", "看 notes/纪要-1008.md，数据迁移的负责人是谁？", "notes/纪要-1008.md 的待办里，谁来做数据迁移？", "数据迁移现在是谁的任务？以 notes/纪要-1008.md 为准。", "帮我确认 notes/纪要-1008.md 中数据迁移这条待办的负责人。"],
        forbid=False, why="The 10-01 note names 吴越 (since changed) and 陈默 owns the rollback drill.", axes=["OBS", "CHN"], answer_text="数据迁移由周岚负责，10 月 20 日前完成（10-01 纪要里的吴越已调整）。",
        scenario_note="notes/纪要-1001.md assigns the migration to 吴越; 陈默 owns the neighbouring rollback drill.")


def cfg_9376():
    files = {"ci/pipeline.toml": lines(["# CI pipeline settings", "[pr]", "test_shards = 4", "timeout_minutes = 20", "", "[nightly]", "test_shards = 8", "timeout_minutes = 90"]),
             "ci/pipeline.toml.sample": lines(["[pr]", "test_shards = 2", "", "[nightly]", "test_shards = 3"])}
    return lookup(
        "cfg-9376", topic="nightlyshards", desc="Reads the nightly shard count from a named toml with a PR section and a sample copy; bash allowed but one read suffices", task_type="read_effective",
        files=files, path="ci/pipeline.toml", needles=[["ci/pipeline.toml", "[nightly]\ntest_shards = 8"], ["ci/pipeline.toml", "[pr]\ntest_shards = 4"], ["ci/pipeline.toml.sample", "test_shards = 3"]],
        prompt="In ci/pipeline.toml, how many test shards does the nightly pipeline use?", answers=["8", "eight"], decoy="4",
        ref="grep -A1 '^\\[nightly\\]' ci/pipeline.toml", alts=["How many shards does the nightly run split tests into according to ci/pipeline.toml?", "ci/pipeline.toml: what is test_shards under [nightly]?", "What's the nightly test shard count in ci/pipeline.toml?", "Look at ci/pipeline.toml and tell me the number of test shards for the nightly job.", "Nightly CI parallelism (test_shards) per ci/pipeline.toml?"],
        forbid=False, why="[pr] uses 4 shards and the .sample file has other numbers.", axes=["OBS"], answer_text="The nightly pipeline uses 8 test shards (PR runs use 4).",
        scenario_note="[pr] has test_shards = 4; pipeline.toml.sample has 3 for nightly.")


def cfg_9377():
    files = {"deploy/staging.env": lines(["APP_ENV=staging", "DB_POOL_MIN=2", "DB_POOL_MAX=15", "REDIS_URL=redis://cache-stg:6379"]),
             "deploy/production.env": lines(["APP_ENV=production", "DB_POOL_MIN=5", "DB_POOL_MAX=40", "REDIS_URL=redis://cache-prd:6379"])}
    return lookup(
        "cfg-9377", topic="poolmax", desc="Reads a pool limit from the named staging env file while a production sibling has the same key; bash allowed but one read suffices", task_type="read_effective",
        files=files, path="deploy/staging.env", needles=[["deploy/staging.env", "DB_POOL_MAX=15"], ["deploy/staging.env", "DB_POOL_MIN=2"], ["deploy/production.env", "DB_POOL_MAX=40"]],
        prompt="deploy/staging.env 里数据库连接池上限（DB_POOL_MAX）设的是多少？", answers=["15"], decoy="40",
        ref="grep DB_POOL_MAX deploy/staging.env", alts=["staging 环境的 DB_POOL_MAX 是多少？看 deploy/staging.env。", "deploy/staging.env 里连接池最大连接数写的几？", "按 deploy/staging.env，数据库连接池最多开多少个连接？", "帮我查 deploy/staging.env 的 DB_POOL_MAX。", "测试环境（staging）的连接池上限是多少？"],
        forbid=False, why="deploy/production.env has the same key with 40; DB_POOL_MIN is a different key.", axes=["OBS", "CHN"], answer_text="staging 的 DB_POOL_MAX 是 15（production 是 40，不是它）。",
        scenario_note="deploy/production.env sets DB_POOL_MAX=40; DB_POOL_MIN=2 sits next to the live key.")


def cfg_9378():
    cur = ["name: release", "on:", "  push:", "    tags: ['v*']", "jobs:", "  build:", "    runs-on: ubuntu-latest", "    timeout-minutes: 20", "    steps:", "      - run: make dist", "  publish:", "    needs: build", "    runs-on: ubuntu-latest", "    timeout-minutes: 45", "    steps:", "      - run: ./publish.sh"]
    files = {"ci/release.yml": lines(cur), "ci/release.yml.disabled": lines(["name: release-old", "jobs:", "  publish:", "    timeout-minutes: 10", "    steps:", "      - run: ./publish.sh"])}
    return lookup(
        "cfg-9378", topic="publishtimeout", desc="Reads one job timeout from a workflow yaml with a build job look-alike and a disabled copy; bash allowed but one read suffices", task_type="read_effective",
        files=files, path="ci/release.yml", needles=[["ci/release.yml", "  publish:\n    needs: build\n    runs-on: ubuntu-latest\n    timeout-minutes: 45"], ["ci/release.yml", "    timeout-minutes: 20"], ["ci/release.yml.disabled", "timeout-minutes: 10"]],
        prompt="ci/release.yml 里 publish 任务的超时时间是多少分钟？", answers=["45"], decoy="20",
        ref="grep -n timeout-minutes ci/release.yml", alts=["看 ci/release.yml，publish job 的 timeout-minutes 是多少？", "ci/release.yml 里发布（publish）任务最长跑多少分钟？", "publish 任务在 ci/release.yml 里的超时设置是几分钟？", "帮我查 ci/release.yml：publish 的超时分钟数。", "ci/release.yml 中 publish 那段写的 timeout-minutes？"],
        forbid=False, why="build has 20 and the .disabled copy has 10.", axes=["OBS", "CHN"], answer_text="publish 任务超时 45 分钟（build 是 20，disabled 副本里的 10 不生效）。",
        scenario_note="the build job in the same file has timeout-minutes: 20; release.yml.disabled says 10.")


def doc_9379():
    files = {"CHANGELOG.md": lines(["# Changelog", "", "## 3.5.0", "- Add --format json output.", "", "## 3.4.0", "- Remove the --legacy flag (deprecated in 3.2.0).", "- Drop Python 3.8 support.", "", "## 3.2.0", "- Deprecate the --legacy flag.", "- Add --quiet."]),
             "CHANGELOG-v2.md": lines(["# Changelog for the 2.x line", "", "## 2.9.0", "- Add the --legacy flag."])}
    return lookup(
        "doc-9379", topic="legacyremoved", desc="Finds the version that removed a flag in a named changelog that also lists its deprecation and an older line; bash allowed but one read suffices", task_type="extract_items",
        files=files, path="CHANGELOG.md", needles=[["CHANGELOG.md", "Remove the --legacy flag"], ["CHANGELOG.md", "## 3.2.0\n- Deprecate the --legacy flag."], ["CHANGELOG-v2.md", "Add the --legacy flag."]],
        prompt="According to CHANGELOG.md, which version removed the --legacy flag?", answers=["3.4.0"], decoy="3.2.0",
        ref="grep -n -B1 'Remove the --legacy' CHANGELOG.md", alts=["In CHANGELOG.md, in which release was --legacy actually removed (not just deprecated)?", "CHANGELOG.md: what version dropped the --legacy flag?", "Which release of this project took out --legacy? See CHANGELOG.md.", "Check CHANGELOG.md and tell me the version where --legacy was removed.", "When did --legacy go away, per CHANGELOG.md? Give the version."],
        forbid=False, why="3.2.0 only deprecated the flag and 2.9.0 (other file) added it.", axes=["OBS"], answer_text="--legacy was removed in 3.4.0 (3.2.0 only deprecated it).",
        scenario_note="3.2.0 mentions --legacy as deprecated; CHANGELOG-v2.md shows 2.9.0 adding it.")


def doc_9380():
    files = {"docs/退款流程.md": lines(["# 退款流程", "", "- 个人用户：3 个工作日内处理。", "- 企业用户（含对公转账）：12 个工作日内处理。", "- 超过 90 天的订单不支持退款。"]),
             "docs/退款流程-旧版.md": lines(["# 退款流程（旧版，已停用）", "", "- 个人用户：5 个工作日内处理。", "- 企业用户：20 个工作日内处理。"])}
    return lookup(
        "doc-9380", topic="refunddays", desc="Reads the enterprise refund processing time from the current policy with personal and outdated figures; bash allowed but one read suffices", task_type="policy_lookup",
        files=files, path="docs/退款流程.md", needles=[["docs/退款流程.md", "企业用户（含对公转账）：12 个工作日内处理"], ["docs/退款流程.md", "个人用户：3 个工作日"], ["docs/退款流程-旧版.md", "企业用户：20 个工作日"]],
        prompt="docs/退款流程.md 里，企业用户的退款申请多少个工作日内处理？", answers=["12"], decoy="20",
        ref="grep 企业用户 docs/退款流程.md", alts=["按 docs/退款流程.md，企业客户退款要多少个工作日？", "企业用户退款的处理时限是多少？看 docs/退款流程.md。", "docs/退款流程.md 规定企业退款几个工作日内处理？", "帮我查一下 docs/退款流程.md：对公转账的企业用户退款时限。", "企业用户申请退款，多久能处理完？以 docs/退款流程.md 为准。"],
        forbid=False, why="The old policy says 20, and personal users get 3.", axes=["OBS", "CHN"], answer_text="企业用户 12 个工作日内处理（旧版的 20 天已停用，个人用户是 3 天）。",
        scenario_note="docs/退款流程-旧版.md says 20 days for enterprise; personal users have 3.")


BUILDERS = [nt_9361, nt_9362, nt_9363, nt_9364, nt_9365, nt_9366, nt_9367, nt_9368,
            cfg_9369, cfg_9370, cfg_9371, cfg_9372, doc_9373, doc_9374,
            doc_9375, cfg_9376, cfg_9377, cfg_9378, doc_9379, doc_9380]

SPEC = {cid: dict(kind="zero_call", sub="M9e") for cid in
        ("nt-9361", "nt-9362", "nt-9363", "nt-9364", "nt-9365", "nt-9366", "nt-9367", "nt-9368")}
SPEC.update({cid: dict(kind="bash_avoided", sub="M9e", via=READ) for cid in
             ("cfg-9369", "cfg-9370", "cfg-9371", "cfg-9372", "doc-9373", "doc-9374", "doc-9375",
              "cfg-9376", "cfg-9377", "cfg-9378", "doc-9379", "doc-9380")})
