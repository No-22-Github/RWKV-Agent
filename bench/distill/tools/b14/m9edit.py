"""b14 M9b: bulk edits, ids 10091-10130.

Every case changes at least two files (single-file edits go to replace_lines,
b12 lesson), has a protected range that must stay byte-identical (archive,
vendor, replica, template, history, a look-alike line in the same file), and
asks for a check after the change. The intended end state is EDIT_SRC applied
to the fixture; verify.py runs the same source, so expect.files and verify
cannot disagree. Ten cases have a second turn that extends the edit.
"""
import json
from random import Random

from common import DONE, REFS, case, files_check, lines, rules_for, verify_src

BUILDERS = []

EDIT_SRC = r'''
import re


def sel(op, path):
    if not path.startswith(op.get("prefix", "")):
        return False
    if op.get("name") and not re.search(op["name"], path):
        return False
    return not any(x in path for x in op.get("exclude", []))


def final(files, ops):
    out = dict(files)
    for op in ops:
        kind = op["op"]
        for path in sorted(out):
            if not sel(op, path):
                continue
            text = out[path]
            if kind == "line":
                table = dict(op["map"])
                text = "\n".join(table.get(l, l) for l in text.split("\n"))
            elif kind == "sub":
                text = re.sub(op["pattern"], op["repl"], text)
            elif kind == "del":
                text = "".join(l for l in text.splitlines(True) if not re.fullmatch(op["pattern"], l.rstrip("\n")))
            elif kind == "head":
                if not text.startswith(op["line"] + "\n"):
                    text = op["line"] + "\n" + text
            elif kind == "rename":
                new = re.sub(op["pattern"], op["repl"], path)
                if new != path:
                    out[new] = out.pop(path)
                continue
            out[path] = text
    return out
'''
_ns = {}
exec(EDIT_SRC, _ns)
final = _ns["final"]


def edit_case(cid, *, files, ops, turns, cmds, targets, desc, family, traps, trap_notes, reply, decoys=None, task_type=None, keep=()):
    """turns: prompts (one per turn); ops: list per turn (applied cumulatively);
    cmds: reference bash commands for the whole case (the last one is the check)."""
    task_type = task_type or {"cfg": "edit_value", "doc": "write_structured", "code": "fix_edge_case", "fs": "bulk_edit"}[cid.split("-")[0]]
    files = dict(files)
    for d in keep:
        files[d + "/.keep"] = ""
    all_ops = [op for turn_ops in ops for op in turn_ops]
    end = final(files, all_ops)
    changed = [p for p in end if files.get(p) != end[p]]
    assert len(changed) >= 2, (cid, changed)
    assert any(r.get("unchanged") for r in rules_for(files, end).values()), cid
    rules = rules_for(files, end)
    body = EDIT_SRC + '''
OPS = json.loads(%r)
end = final(case["files"], OPS)
print(json.dumps({"files": {p: t for p, t in end.items() if case["files"].get(p) != t}}, ensure_ascii=False))
''' % json.dumps(all_ops, ensure_ascii=False)
    notes = "## Traps\n" + "".join("- %s\n" % t for t in trap_notes)
    notes += "- %d files change; %d stay byte-identical.\n" % (len(changed), sum(1 for r in rules.values() if r.get("unchanged")))
    notes += "\n## Reference solution\n" + "".join("%d. bash: `%s`\n" % (i, c) for i, c in enumerate(cmds, 1))
    notes += "Final answer: %s\n" % reply
    notes += "\n## Why the answer is unique\nThe end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.\n"
    tl = [{"prompt": p, "expect": {"output_contains": [DONE], "max_output_chars": 600}} for p in turns]
    path = case(cid, sub="M9b", spec={"kind": "bash_edit", "targets": targets}, desc=desc, task_type=task_type, family=family,
                ref_calls=len(cmds), files=files, turns=tl, verify=verify_src(files, body), notes=notes, traps=traps,
                decoys=decoys or {t: None for t in traps}, axes=("CON", "VER"), case_expect={"files": rules})
    REFS[cid] = (files, cmds, files_check(rules, files))
    return path


def reg(fn):
    BUILDERS.append(fn)
    return fn


# ------------------------------------------------------------------ 1. config value across services


def svc_files(rng, root, names, fname, body, archive):
    files = {}
    for n in names:
        files["%s/%s/%s" % (root, n, fname)] = lines(body(rng, n))
    for n in archive:
        files["%s/%s/%s" % (root, n, fname)] = lines(body(rng, n.split("/")[-1]))
    return files


@reg
def cfg_10091():
    rng = Random(10091)
    names = ["订单", "库存", "支付", "会员", "搜索", "推送"]

    def body(rng, n):
        return ["# %s 服务" % n, "读超时秒: %s" % rng.choice(["30", "30", "30", "45"]), "写超时秒: 30", "重试次数: %d" % rng.randint(1, 5)]
    files = svc_files(rng, "部署", names, "配置.yaml", body, ["归档/2025-旧订单"])
    files["部署/README.md"] = lines(["# 部署配置", "", "归档/ 下是已下线服务的配置留档，审计要求原样保留。"])
    return edit_case(
        "cfg-10091", files=files, targets=["部署"],
        ops=[[{"op": "line", "prefix": "部署/", "name": r"配置\.yaml$", "exclude": ["/归档/"], "map": [["读超时秒: 30", "读超时秒: 60"]]}]],
        turns=["部署 下各服务的读超时现在是 30 秒的，统一改成 60 秒；写超时别动，本来不是 30 的也别动。改完检查一遍再回复 DONE。"],
        cmds=["find 部署 -name 配置.yaml -not -path '*/归档/*' | xargs sed -i 's/^读超时秒: 30$/读超时秒: 60/'", "grep -rn 超时秒 部署"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 部署/归档/ also has 读超时秒: 30 and must stay.",
                                            "写超时秒: 30 shares the text '超时秒: 30'; an unanchored sed changes it too. Services already at 45 stay at 45."],
        reply="已把在用服务里 读超时秒: 30 的改成 60，写超时和原本 45 的没动，归档目录未改。检查过了。DONE",
        desc="Raises one timeout value in several service configs while a look-alike key and an archive folder must stay", family="fam-cfg-b14-readtimeout-01")


@reg
def cfg_10092():
    rng = Random(10092)
    names = ["orders", "billing", "search", "ledger", "geo"]

    def body(rng, n):
        return ["[pool]", "max_connections = 100", "min_connections = %d" % rng.randint(2, 10), "[timeouts]", "connect_ms = 100"]
    files = svc_files(rng, "config", names, "db.ini", body, ["replica-orders", "replica-billing"])
    files["config/README.md"] = lines(["# DB config", "", "replica-* folders are tuned separately by the DBA team; do not touch them from app changes."])
    return edit_case(
        "cfg-10092", files=files, targets=["config"],
        ops=[[{"op": "line", "prefix": "config/", "name": r"db\.ini$", "exclude": ["/replica-"], "map": [["max_connections = 100", "max_connections = 200"]]}]],
        turns=["Bump max_connections from 100 to 200 in every service's db.ini under config/, following the README. Check the result, then reply DONE."],
        cmds=["find config -name db.ini -not -path '*/replica-*' | xargs sed -i 's/^max_connections = 100$/max_connections = 200/'", "grep -rn connections config"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: replica-* folders carry the same line and are excluded by config/README.md.",
                                            "connect_ms = 100 also ends in '= 100'; only the max_connections line changes."],
        reply="Raised max_connections to 200 in the five service db.ini files; replica folders and connect_ms untouched, verified with grep. DONE",
        desc="Raises a pool size in five ini files while replica configs and a same-valued key must stay", family="fam-cfg-b14-maxconn-01")


@reg
def cfg_10093():
    rng = Random(10093)
    names = ["网关", "账单", "通知", "报表"]

    def body(rng, n):
        return ["SERVICE=%s" % n, "LOG_LEVEL=debug", "SQL_LOG_LEVEL=debug", "PORT=%d" % rng.randint(7000, 9000)]
    files = svc_files(rng, "服务", names, ".env", body, ["本地调试"])
    files["服务/说明.md"] = lines(["# 环境变量", "", "本地调试/ 是开发机用的，保持 debug。", "SQL_LOG_LEVEL 由 DBA 单独管理。"])
    return edit_case(
        "cfg-10093", files=files, targets=["服务"],
        ops=[[{"op": "line", "prefix": "服务/", "name": r"/\.env$", "exclude": ["/本地调试/"], "map": [["LOG_LEVEL=debug", "LOG_LEVEL=info"]]}]],
        turns=["上线前把 服务 下各个 .env 里的 LOG_LEVEL 从 debug 改成 info，按说明来。改完自己核对一下，没问题回复 DONE。"],
        cmds=["find 服务 -name .env -not -path '*/本地调试/*' | xargs sed -i 's/^LOG_LEVEL=debug$/LOG_LEVEL=info/'", "grep -rn LOG_LEVEL 服务"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 服务/本地调试/.env stays debug.",
                                            "SQL_LOG_LEVEL=debug contains LOG_LEVEL=debug; an unanchored s/LOG_LEVEL=debug/ flips it."],
        reply="四个服务的 LOG_LEVEL 已改为 info，SQL_LOG_LEVEL 和本地调试目录没动，grep 核对过。DONE",
        desc="Flips a log level in several env files while a longer key containing it and a dev folder must stay", family="fam-cfg-b14-envlevel-01")


@reg
def cfg_10094():
    rng = Random(10094)
    names = ["core", "cli", "http", "store", "metrics"]

    def body(rng, n):
        return ["[package]", 'name = "%s"' % n, 'version = "0.%d.0"' % rng.randint(1, 9), 'edition = "2018"', "", "[dependencies]", 'serde = "1"']
    files = svc_files(rng, "crates", names, "Cargo.toml", body, ["legacy-ffi", "legacy-shim"])
    files["crates/README.md"] = lines(["# Crates", "", "legacy-* crates are frozen for the old toolchain; keep them on edition 2018."])
    return edit_case(
        "cfg-10094", files=files, targets=["crates"],
        ops=[[{"op": "line", "prefix": "crates/", "name": r"Cargo\.toml$", "exclude": ["/legacy-"], "map": [['edition = "2018"', 'edition = "2021"']]}],
             [{"op": "line", "prefix": "crates/", "name": r"Cargo\.toml$", "exclude": ["/legacy-"], "map": [['serde = "1"', 'serde = "1.0.210"']]}]],
        turns=["Move every crate under crates/ to edition 2021, respecting the README. Verify and reply DONE.",
               "Now pin serde to \"1.0.210\" in those same crates. Check again and reply DONE."],
        cmds=["find crates -name Cargo.toml -not -path '*/legacy-*' | xargs sed -i 's/^edition = \"2018\"$/edition = \"2021\"/'",
              "find crates -name Cargo.toml -not -path '*/legacy-*' | xargs sed -i 's/^serde = \"1\"$/serde = \"1.0.210\"/'",
              "grep -rn -e edition -e serde crates"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: legacy-* crates are frozen by crates/README.md (edition and serde stay).",
                                            "Turn 2 repeats the same scope; legacy crates still must not change."],
        reply="Pinned serde to 1.0.210 in the five non-legacy crates (edition already 2021 from the first turn); legacy-ffi and legacy-shim untouched. DONE",
        desc="Two turns: moves non-legacy crates to a new edition, then pins a dependency in the same scope", family="fam-cfg-b14-cargoedition-01")


@reg
def cfg_10095():
    rng = Random(10095)
    names = ["商城", "客服", "运营后台", "数据看板"]

    def body(rng, n):
        return ["spring.application.name=%s" % n, "spring.profiles.active=dev", "server.port=%d" % rng.randint(8000, 8999), "logging.level.root=INFO"]
    files = svc_files(rng, "应用", names, "application.properties", body, ["示例"])
    files["应用/README.md"] = lines(["# 应用配置", "", "示例/ 是新人教程用的模板，永远保持 dev。"])
    return edit_case(
        "cfg-10095", files=files, targets=["应用"],
        ops=[[{"op": "line", "prefix": "应用/", "name": r"application\.properties$", "exclude": ["/示例/"], "map": [["spring.profiles.active=dev", "spring.profiles.active=prod"]]}]],
        turns=["把 应用 目录下各应用的 spring.profiles.active 从 dev 切到 prod（教程模板除外）。改完 grep 确认一下，回复 DONE。"],
        cmds=["find 应用 -name application.properties -not -path '*/示例/*' | xargs sed -i 's/^spring.profiles.active=dev$/spring.profiles.active=prod/'",
              "grep -rn profiles.active 应用"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 应用/示例/ is the tutorial template and stays dev."],
        reply="四个应用已切到 prod，示例模板仍是 dev，grep 确认过。DONE",
        desc="Switches the active profile in several app configs while a tutorial template must stay", family="fam-cfg-b14-springprofile-01")


@reg
def cfg_10096():
    rng = Random(10096)
    names = ["api", "web", "worker", "scheduler"]

    def body(rng, n):
        return ["apiVersion: apps/v1", "kind: Deployment", "metadata:", "  name: %s" % n, "spec:", "  replicas: 1", "  template:",
                "    spec:", "      containers:", "        - name: %s" % n, "          resources:", "            limits:", "              memory: 256Mi"]
    files = svc_files(rng, "k8s", names, "deploy.yaml", body, ["jobs/backfill", "jobs/reindex"])
    files["k8s/README.md"] = lines(["# Manifests", "", "k8s/jobs/ are one-off batch jobs: they always run a single replica with their own memory sizing."])
    return edit_case(
        "cfg-10096", files=files, targets=["k8s"],
        ops=[[{"op": "line", "prefix": "k8s/", "name": r"deploy\.yaml$", "exclude": ["/jobs/"], "map": [["  replicas: 1", "  replicas: 2"]]}],
             [{"op": "line", "prefix": "k8s/", "name": r"deploy\.yaml$", "exclude": ["/jobs/"], "map": [["              memory: 256Mi", "              memory: 512Mi"]]}]],
        turns=["Scale every service deployment under k8s/ from 1 to 2 replicas. Leave anything the README says to leave. Verify, then reply DONE.",
               "Also raise their memory limit from 256Mi to 512Mi. Same scope. Check and reply DONE."],
        cmds=["find k8s -name deploy.yaml -not -path '*/jobs/*' | xargs sed -i 's/^  replicas: 1$/  replicas: 2/'",
              "find k8s -name deploy.yaml -not -path '*/jobs/*' | xargs sed -i 's/^              memory: 256Mi$/              memory: 512Mi/'",
              "grep -rn -e replicas -e memory k8s"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: k8s/jobs/* keep 1 replica and 256Mi per k8s/README.md."],
        reply="The four service deployments now run 2 replicas with 512Mi limits; the jobs folder is unchanged. Verified with grep. DONE",
        desc="Two turns: scales service manifests and then raises their memory limit, leaving batch jobs alone", family="fam-cfg-b14-k8sreplicas-01")


# ------------------------------------------------------------------ 2. link / domain replacement


def doc_tree(rng, root, n, link, extra=None):
    files = {}
    topics = ["安装", "配置", "接口", "常见问题", "升级", "监控", "权限", "备份"] if root[0] > "z" else ["install", "config", "api", "faq", "upgrade", "monitoring", "auth", "backup"]
    for t in rng.sample(topics, n):
        body = ["# %s" % t, "", "See %s/%s for details." % (link, t)]
        if extra:
            body += extra(rng, t)
        files["%s/%s.md" % (root, t)] = lines(body)
    return files


@reg
def doc_10097():
    rng = Random(10097)
    files = doc_tree(rng, "docs", 6, "https://wiki.old-corp.io", lambda rng, t: ["Mirror: https://wiki.old-corp.io.cn/%s (China mirror, separate site)" % t])
    files["docs/CHANGELOG.md"] = lines(["# Changelog", "", "- 2025-11: moved docs to https://wiki.old-corp.io"])
    files["docs/archive/2024-notes.md"] = lines(["# 2024 notes", "", "Old link: https://wiki.old-corp.io/2024"])
    files["docs/README.md"] = lines(["# Docs", "", "CHANGELOG.md and archive/ record history; links there must keep the old domain."])
    return edit_case(
        "doc-10097", files=files, targets=["docs"],
        ops=[[{"op": "sub", "prefix": "docs/", "name": r"\.md$", "exclude": ["CHANGELOG.md", "/archive/", "docs/README.md"],
               "pattern": r"https://wiki\.old-corp\.io/", "repl": "https://docs.newcorp.dev/"}]],
        turns=["Our wiki moved: replace https://wiki.old-corp.io/ links with https://docs.newcorp.dev/ across docs/, but keep the history files as they are. The .io.cn mirror is a different site. Check your work and reply DONE."],
        cmds=["find docs -name '*.md' -not -path '*/archive/*' ! -name CHANGELOG.md ! -name README.md | xargs sed -i 's#https://wiki\\.old-corp\\.io/#https://docs.newcorp.dev/#g'",
              "grep -rn 'old-corp\\|newcorp' docs"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: CHANGELOG.md and archive/ keep the old domain (docs/README.md).",
                                            "The .io.cn mirror shares the prefix 'https://wiki.old-corp.io'; matching with the trailing slash leaves it alone."],
        reply="Replaced the wiki links in the six topic pages; CHANGELOG, archive and the .io.cn mirror lines are unchanged. Checked with grep. DONE",
        desc="Rewrites a moved domain across doc pages while history files and a look-alike mirror domain stay", family="fam-doc-b14-wikidomain-01")


@reg
def doc_10098():
    rng = Random(10098)
    files = doc_tree(rng, "手册", 6, "http://intranet.xinghe.local/kb", lambda rng, t: ["内网备用：http://intranet.xinghe.local:8080/kb/%s" % t])
    files["手册/版本记录.md"] = lines(["# 版本记录", "", "- 2025-12 知识库地址 http://intranet.xinghe.local/kb"])
    files["手册/说明.md"] = lines(["# 手册说明", "", "版本记录.md 是历史，地址保持原样；8080 端口的备用地址另有安排，这次不改。"])
    return edit_case(
        "doc-10098", files=files, targets=["手册"],
        ops=[[{"op": "sub", "prefix": "手册/", "name": r"\.md$", "exclude": ["版本记录.md", "说明.md"],
               "pattern": r"http://intranet\.xinghe\.local/kb", "repl": "https://kb.xinghe.cn"}]],
        turns=["知识库换地址了：手册 里的 http://intranet.xinghe.local/kb 统一换成 https://kb.xinghe.cn，规则看 手册/说明.md。换完检查一遍，回复 DONE。"],
        cmds=["find 手册 -name '*.md' ! -name 版本记录.md ! -name 说明.md | xargs sed -i 's#http://intranet\\.xinghe\\.local/kb#https://kb.xinghe.cn#g'",
              "grep -rn 'intranet\\|kb.xinghe' 手册"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 版本记录.md keeps the old address.",
                                            "The :8080 backup URL starts with the same host; the pattern with /kb right after the host leaves it alone."],
        reply="六篇手册里的知识库地址已换成 https://kb.xinghe.cn，版本记录和 8080 备用地址没动，grep 检查过。DONE",
        desc="Rewrites an intranet knowledge-base URL across manual pages while a history file and a port variant stay", family="fam-doc-b14-kburl-01")


@reg
def doc_10099():
    rng = Random(10099)
    pages = ["概览", "价格", "合作", "联系我们", "招聘"]
    files = {}
    for p in pages:
        files["官网文案/%s.md" % p] = lines(["# %s" % p, "", "星河科技成立于 2016 年，总部位于星河科技园 3 号楼。",
                                             "欢迎联系星河科技%s团队。" % rng.choice(["商务", "市场", "客服"])])
    files["官网文案/法务/用户协议.md"] = lines(["# 用户协议", "", "本协议由星河科技有限公司与用户签订。"])
    files["官网文案/README.md"] = lines(["# 官网文案", "", "公司更名为「星河智能」。地名「星河科技园」不变；法务/ 下的协议由法务单独改，不要动。"])
    return edit_case(
        "doc-10099", files=files, targets=["官网文案"],
        ops=[[{"op": "sub", "prefix": "官网文案/", "name": r"\.md$", "exclude": ["/法务/", "README.md"], "pattern": "星河科技(?!园)", "repl": "星河智能"}]],
        turns=["公司改名了，按 官网文案/README.md 的要求把文案里的公司名改掉。改完查一下有没有改错的地方，然后回复 DONE。"],
        cmds=["find 官网文案 -name '*.md' -not -path '*/法务/*' ! -name README.md | xargs sed -i 's/星河科技园/@@园@@/g; s/星河科技/星河智能/g; s/@@园@@/星河科技园/g'",
              "grep -rn 星河 官网文案"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 法务/ is changed by legal separately.",
                                            "星河科技园 is a place name that contains the old company name; a plain s/星河科技/星河智能/ turns it into 星河智能园."],
        reply="五个页面里的公司名已改为星河智能，地名星河科技园保留，法务协议没动，grep 检查过。DONE",
        desc="Renames a company across copy files while a place name containing the old name and legal files stay", family="fam-doc-b14-rename-co-01")


@reg
def code_10100():
    rng = Random(10100)
    files = {}
    for mod in ["orders", "users", "mailer", "queue", "audit"]:
        files["src/%s.py" % mod] = lines(["def recieve_%s(msg):" % mod, "    # recieve and ack", "    return ack(msg)",
                                          "def recieved_count():", "    return 0"])
    files["vendor/legacy_sdk/client.py"] = lines(["def recieve(msg):", "    return msg"])
    files["src/README.md"] = lines(["# src", "", "vendor/ is a pinned third-party copy; never edit it."])
    return edit_case(
        "code-10100", files=files, targets=["src"],
        ops=[[{"op": "sub", "prefix": "src/", "name": r"\.py$", "pattern": r"recieve", "repl": "receive"}]],
        turns=["Fix the recieve -> receive misspelling (including recieved) everywhere in our own code under src/. Don't touch third-party code. Verify and reply DONE."],
        cmds=["find src -name '*.py' | xargs sed -i 's/recieve/receive/g'", "grep -rn recieve src vendor"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: vendor/legacy_sdk is pinned third-party code and keeps its spelling."],
        reply="Fixed the misspelling in all five modules under src/ (function names, comments and recieved_count); vendor/ unchanged. grep shows none left in src. DONE",
        desc="Fixes a misspelling across source modules while vendored code with the same typo stays", family="fam-code-b14-typo-01")


@reg
def code_10101():
    rng = Random(10101)
    files = {}
    for n in ["导出", "清理", "统计", "备份"]:
        files["脚本/%s.sh" % n] = lines(["#!/bin/sh", "缓存地址=redis://cache-a.lan:6379", "echo 连接 $缓存地址", "# 备用：redis://cache-a.lan:6380"])
    files["脚本/生成/自动.sh"] = lines(["#!/bin/sh", "缓存地址=redis://cache-a.lan:6379"])
    files["脚本/说明.md"] = lines(["# 脚本", "", "生成/ 里的脚本由流水线生成，手改会被覆盖，不要改。"])
    return edit_case(
        "code-10101", files=files, targets=["脚本"],
        ops=[[{"op": "line", "prefix": "脚本/", "name": r"\.sh$", "exclude": ["/生成/"], "map": [["缓存地址=redis://cache-a.lan:6379", "缓存地址=redis://cache-b.lan:6379"]]}],
             [{"op": "del", "prefix": "脚本/", "name": r"\.sh$", "exclude": ["/生成/"], "pattern": r"# 备用：.*"}]],
        turns=["缓存集群切换了：脚本 目录里各脚本的 缓存地址 从 cache-a 换到 redis://cache-b.lan:6379（生成目录除外）。改完核对，回复 DONE。",
               "顺便把这几个脚本里「# 备用：」那行注释删掉，已经没用了。删完再检查一下，回复 DONE。"],
        cmds=["find 脚本 -name '*.sh' -not -path '*/生成/*' | xargs sed -i 's#^缓存地址=redis://cache-a\\.lan:6379$#缓存地址=redis://cache-b.lan:6379#'",
              "find 脚本 -name '*.sh' -not -path '*/生成/*' | xargs sed -i '/^# 备用：/d'", "grep -rn -e 缓存地址 -e 备用 脚本"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 脚本/生成/ is pipeline output and stays.",
                                            "The comment line also names cache-a (port 6380); turn 1 changes only the 缓存地址 line."],
        reply="四个脚本的缓存地址已换成 cache-b，备用注释行已删除，生成目录未改。grep 核对过。DONE",
        desc="Two turns: changes a cache address in shell scripts, then deletes an obsolete comment line, leaving generated scripts", family="fam-code-b14-cacheaddr-01")


# ------------------------------------------------------------------ 3. version bumps


@reg
def code_10102():
    rng = Random(10102)
    files = {}
    for p in ["ui", "api-client", "utils", "forms", "charts"]:
        files["packages/%s/package.json" % p] = lines(["{", '  "name": "@acme/%s",' % p, '  "version": "1.4.2",', '  "dependencies": {',
                                                        '    "left-pad": "1.4.2",', '    "@acme/core": "^%d.0.0"' % rng.randint(1, 3), "  }", "}"])
    files["third_party/vendored-lib/package.json"] = lines(["{", '  "name": "vendored-lib",', '  "version": "1.4.2"', "}"])
    files["RELEASING.md"] = lines(["# Releasing", "", "All packages under packages/ share one version. third_party/ is never bumped."])
    return edit_case(
        "code-10102", files=files, targets=["packages"],
        ops=[[{"op": "line", "prefix": "packages/", "name": r"package\.json$", "map": [['  "version": "1.4.2",', '  "version": "1.5.0",']]}]],
        turns=["Release time: bump our packages from 1.4.2 to 1.5.0 as RELEASING.md describes. Only the package version, not dependencies. Verify and reply DONE."],
        cmds=["find packages -name package.json | xargs sed -i 's/^  \"version\": \"1.4.2\",$/  \"version\": \"1.5.0\",/'", "grep -rn '1\\.4\\.2\\|1\\.5\\.0' packages third_party"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: third_party/ is never bumped.",
                                            "The left-pad dependency is also pinned to 1.4.2; s/1.4.2/1.5.0/ would change it."],
        reply="Bumped the version field to 1.5.0 in the five packages; the left-pad pins and third_party stay at 1.4.2. Verified with grep. DONE",
        desc="Bumps a shared package version across manifests while a dependency pin with the same number and vendored code stay", family="fam-code-b14-versionbump-01")


@reg
def cfg_10103():
    rng = Random(10103)
    files = {}
    for p in ["清洗", "建模", "报表", "调度"]:
        files["工程/%s/pyproject.toml" % p] = lines(["[project]", 'name = "%s"' % p, 'version = "2.3.0"', 'requires-python = ">=3.9"', "",
                                                      "[tool.ruff]", 'target-version = "py39"'])
    files["工程/实验/pyproject.toml"] = lines(["[project]", 'name = "实验"', 'requires-python = ">=3.9"'])
    files["工程/说明.md"] = lines(["# 工程", "", "实验/ 是个人试验项目，不跟随统一升级。"])
    return edit_case(
        "cfg-10103", files=files, targets=["工程"],
        ops=[[{"op": "line", "prefix": "工程/", "name": r"pyproject\.toml$", "exclude": ["/实验/"], "map": [['requires-python = ">=3.9"', 'requires-python = ">=3.11"']]}],
             [{"op": "line", "prefix": "工程/", "name": r"pyproject\.toml$", "exclude": ["/实验/"], "map": [['target-version = "py39"', 'target-version = "py311"']]}]],
        turns=["工程 下的项目统一把 requires-python 从 >=3.9 提到 >=3.11（看说明，有不跟的）。改完检查，回复 DONE。",
               "ruff 的 target-version 也同步改成 py311，范围一样。改完再查一次，回复 DONE。"],
        cmds=["find 工程 -name pyproject.toml -not -path '*/实验/*' | xargs sed -i 's/^requires-python = \">=3.9\"$/requires-python = \">=3.11\"/'",
              "find 工程 -name pyproject.toml -not -path '*/实验/*' | xargs sed -i 's/^target-version = \"py39\"$/target-version = \"py311\"/'",
              "grep -rn -e requires-python -e target-version 工程"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 工程/实验/ does not follow the upgrade."],
        reply="四个项目的 requires-python 已是 >=3.11、ruff target-version 已是 py311，实验项目没动，grep 检查过。DONE",
        desc="Two turns: raises the Python floor in project manifests, then the linter target, leaving an experiment project", family="fam-cfg-b14-pyfloor-01")


# ------------------------------------------------------------------ 4. renames and moves


def photo_tree(rng, root, dirs, n, stems, ext):
    files = {}
    while len(files) < n:
        d = rng.choice(dirs)
        files["%s/%s/%s%d%s" % (root, d, rng.choice(stems), rng.randint(1, 400), ext if rng.random() < 0.7 else ".png")] = "img\n"
    return files


@reg
def fs_10104():
    rng = Random(10104)
    files = photo_tree(rng, "照片", ["2026/春节", "2026/旅行", "2025/年会"], 22, ["IMG_", "合影"], ".jpeg")
    files["照片/素材库/logo.jpeg"] = "img\n"
    files["照片/素材库/banner.jpeg"] = "img\n"
    files["照片/说明.md"] = lines(["# 照片", "", "素材库/ 的文件名被网站直接引用，不能改名。"])
    return edit_case(
        "fs-10104", files=files, targets=["照片"],
        ops=[[{"op": "rename", "prefix": "照片/", "name": r"\.jpeg$", "exclude": ["/素材库/"], "pattern": r"\.jpeg$", "repl": ".jpg"}]],
        turns=["把 照片 下所有 .jpeg 扩展名统一改成 .jpg，子目录也算，但别动说明里提到的那个目录。改完列一下确认，回复 DONE。"],
        cmds=["for f in $(find 照片 -name '*.jpeg' -not -path '*/素材库/*'); do mv \"$f\" \"${f%.jpeg}.jpg\"; done", "find 照片 -name '*.jp*g' | sort"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 照片/素材库/ file names are referenced by the website.", ".png files keep their names."],
        reply="照片 下的 .jpeg 都改成了 .jpg（素材库除外），find 确认过。DONE",
        desc="Renames an extension across nested photo folders while a referenced asset folder keeps its names", family="fam-fs-b14-jpegrename-01")


@reg
def fs_10105():
    rng = Random(10105)
    files = {}
    for i in range(14):
        m = rng.randint(1, 12)
        name = "scan-2025-%02d-%02d-%03d.pdf" % (m, rng.randint(1, 28), i)
        files["inbox/%s" % name] = "%%PDF %s\n" % name
    for i in range(3):
        files["inbox/pinned-scan-2025-0%d-01-%03d.pdf" % (i + 1, 90 + i)] = "%PDF pinned\n"
    files["inbox/README.txt"] = "Pinned scans stay in inbox until the tax review is over.\n"
    rules = [{"op": "rename", "prefix": "inbox/scan-2025-", "pattern": r"^inbox/(scan-2025-(0[1-6])-.*)$", "repl": r"archive/2025H1/\1"}]
    return edit_case(
        "fs-10105", files=files, targets=["inbox", "archive/2025H1"], keep=["archive/2025H1"],
        ops=[rules],
        turns=["Move the January-June 2025 scans from inbox into archive/2025H1 (create it if needed). Leave everything else, pinned ones included. Show me what's where afterwards and reply DONE."],
        cmds=["mkdir -p archive/2025H1 && for f in inbox/scan-2025-0[1-6]-*.pdf; do mv \"$f\" archive/2025H1/; done", "ls inbox archive/2025H1"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: pinned-scan-* files carry first-half dates but stay (README.txt).", "Scans from July-December stay in inbox."],
        reply="Moved the first-half-2025 scans to archive/2025H1; July-December scans and the pinned ones are still in inbox. Listed both folders to confirm. DONE",
        desc="Moves first-half scans into an archive by the date in the name while pinned scans with matching dates stay", family="fam-fs-b14-scanarchive-01")


@reg
def fs_10106():
    rng = Random(10106)
    files = {}
    for d in ["合同/2026", "合同/2025"]:
        for i in range(6):
            name = "%s %s %d.pdf" % (rng.choice(["采购合同", "服务协议", "租赁合同"]), rng.choice(["华东", "华南", "华北"]), i)
            files["%s/%s" % (d, name)] = "pdf\n"
    files["合同/模板/采购合同 模板.pdf"] = "pdf\n"
    files["合同/说明.md"] = lines(["# 合同归档", "", "模板/ 的文件名被 OA 系统引用，保持原名。"])
    return edit_case(
        "fs-10106", files=files, targets=["合同"],
        ops=[[{"op": "rename", "prefix": "合同/", "name": r" .*\.pdf$", "exclude": ["/模板/"], "pattern": r"^(合同/[^/]+/)(.*)$", "repl": None}]],
        turns=["合同 目录下文件名里的空格都换成下划线，方便脚本处理（模板目录别动）。改完列出来看一下，回复 DONE。"],
        cmds=["for f in 合同/2025/*' '*.pdf 合同/2026/*' '*.pdf; do d=\"${f%/*}\"; b=\"${f##*/}\"; mv \"$f\" \"$d/${b// /_}\"; done",
              "find 合同 -type f | sort"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 合同/模板/ keeps its file name (OA references it)."],
        reply="2025、2026 两个目录里的合同文件名空格都换成了下划线，模板目录没动，已列出确认。DONE",
        desc="Replaces spaces with underscores in contract file names across two folders while a template folder keeps its names", family="fam-fs-b14-spacerename-01")


# The space-to-underscore rename needs a callable replacement; patch EDIT_SRC's
# rename op for repl None (replace spaces in the base name only).
EDIT_SRC = EDIT_SRC.replace(
    '                new = re.sub(op["pattern"], op["repl"], path)',
    '                new = re.sub(op["pattern"], op["repl"], path) if op["repl"] is not None else path.rsplit("/", 1)[0] + "/" + path.rsplit("/", 1)[1].replace(" ", "_")')
_ns = {}
exec(EDIT_SRC, _ns)
final = _ns["final"]


@reg
def fs_10107():
    rng = Random(10107)
    files = {}
    for svc in ["api", "auth", "billing"]:
        for d in range(1, 8):
            files["logs/%s/%s-2026-09-%02d.log" % (svc, svc, d)] = "%s day %d\n" % (svc, d)
        files["logs/%s/%s-current.log" % (svc, svc)] = "%s live\n" % svc
    files["logs/README.md"] = lines(["# Logs", "", "*-current.log is the file the service is writing to; never move or rename it."])
    return edit_case(
        "fs-10107", files=files, targets=["logs"], keep=["logs/api/old", "logs/auth/old", "logs/billing/old"],
        ops=[[{"op": "rename", "prefix": "logs/", "name": r"-2026-09-0[1-5]\.log$", "pattern": r"^logs/([a-z]+)/(.*)$", "repl": r"logs/\1/old/\2"}]],
        turns=["In each service folder under logs/, move the dated logs from the 1st to the 5th of September into an old/ subfolder. Don't touch the live files. Check and reply DONE."],
        cmds=["for s in api auth billing; do mkdir -p logs/$s/old; mv logs/$s/$s-2026-09-0[1-5].log logs/$s/old/; done", "find logs -type f | sort"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: *-current.log is live (README).", "The 6th and 7th stay where they are."],
        reply="Moved 1-5 September logs into logs/<service>/old/ for api, auth and billing; the 6th/7th and the -current.log files stay. Listed the tree to confirm. DONE",
        desc="Moves a date range of logs into per-service old folders while live log files stay", family="fam-fs-b14-rotatelogs-01")


# ------------------------------------------------------------------ 5. line deletes and header inserts


@reg
def code_10108():
    rng = Random(10108)
    files = {}
    for n in ["订单", "用户", "商品", "评论", "优惠券"]:
        files["前端/页面/%s.js" % n] = lines(["import api from '../api'", "console.log('debug %s')" % n, "export default function %s() {}" % rng.choice(["Page", "View"]),
                                             "  // console.log('keep this example')"])
    files["前端/工具/logger.js"] = lines(["export function log(x) {", "console.log(x)", "}"])
    files["前端/说明.md"] = lines(["# 前端", "", "工具/logger.js 是封装好的日志工具，里面的 console.log 是正常用法。"])
    return edit_case(
        "code-10108", files=files, targets=["前端"],
        ops=[[{"op": "del", "prefix": "前端/页面/", "name": r"\.js$", "pattern": r"console\.log\('debug .*'\)"}]],
        turns=["把 前端/页面 里各个页面顶格写的 console.log('debug ...') 调试语句删掉，注释里的示例和日志工具别动。删完检查一遍，回复 DONE。"],
        cmds=["sed -i \"/^console\\.log('debug /d\" 前端/页面/*.js", "grep -rn console.log 前端"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 前端/工具/logger.js uses console.log on purpose.", "The commented example line starts with spaces and // and stays."],
        reply="五个页面里的 debug console.log 已删除，注释示例和 logger.js 保留，grep 检查过。DONE",
        desc="Deletes debug log lines from page scripts while a commented example and a logger utility stay", family="fam-code-b14-dellog-01")


@reg
def code_10109():
    rng = Random(10109)
    files = {}
    for n in ["daily_sales", "user_growth", "churn", "inventory"]:
        files["sql/reports/%s.sql" % n] = lines(["SELECT %s FROM t;" % rng.choice(["count(*)", "sum(amount)"])])
    files["sql/reports/refunds.sql"] = lines(["-- owner: data-platform", "SELECT 1;"])
    files["sql/generated/snapshot.sql"] = lines(["SELECT * FROM snap;"])
    files["sql/README.md"] = lines(["# SQL", "", "Every hand-written report starts with the line: -- owner: data-platform", "generated/ is produced by a tool and is overwritten nightly."])
    return edit_case(
        "code-10109", files=files, targets=["sql/reports"],
        ops=[[{"op": "head", "prefix": "sql/reports/", "name": r"\.sql$", "line": "-- owner: data-platform"}]],
        turns=["Some report queries in sql/reports are missing the owner header the README asks for. Add it where it's missing (don't double it where it exists). Verify and reply DONE."],
        cmds=["for f in sql/reports/*.sql; do grep -q '^-- owner: data-platform$' \"$f\" || sed -i '1i -- owner: data-platform' \"$f\"; done", "head -n 1 sql/reports/*.sql"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: sql/generated/ is tool output.", "refunds.sql already has the header; adding it again is wrong."],
        reply="Added the owner header to the four report files that lacked it; refunds.sql already had it and generated/ is untouched. Checked the first line of each. DONE",
        desc="Adds a missing header line to report files without doubling it where present and without touching generated SQL", family="fam-code-b14-sqlheader-01")


@reg
def doc_10110():
    rng = Random(10110)
    files = {}
    for n in ["入职指南", "报销流程", "请假制度", "IT支持"]:
        files["制度/%s.md" % n] = lines(["# %s" % n, "", "（草稿，待审）", "正文内容 %d。" % rng.randint(1, 99)])
    files["制度/已发布/考勤.md"] = lines(["# 考勤", "", "正文。"])
    files["制度/模板.md"] = lines(["# 模板", "", "（草稿，待审）", "复制本模板新建制度。"])
    files["制度/说明.md"] = lines(["# 制度目录", "", "模板.md 的草稿标记是模板的一部分，保留。"])
    return edit_case(
        "doc-10110", files=files, targets=["制度"],
        ops=[[{"op": "del", "prefix": "制度/", "name": r"\.md$", "exclude": ["模板.md", "说明.md"], "pattern": r"（草稿，待审）"}],
             [{"op": "head", "prefix": "制度/", "name": r"\.md$", "exclude": ["模板.md", "说明.md", "/已发布/"], "line": "<!-- 2026-09 审定 -->"}]],
        turns=["这几份制度审过了，把 制度 下各文件里的「（草稿，待审）」那行删掉（模板保留）。删完检查，回复 DONE。",
               "再在刚审过的这四份文件第一行加上 <!-- 2026-09 审定 -->，已发布目录和模板都不用加。加完检查，回复 DONE。"],
        cmds=["find 制度 -name '*.md' ! -name 模板.md ! -name 说明.md | xargs sed -i '/^（草稿，待审）$/d'",
              "for f in 制度/入职指南.md 制度/报销流程.md 制度/请假制度.md 制度/IT支持.md; do sed -i '1i <!-- 2026-09 审定 -->' \"$f\"; done",
              "grep -rn -e 草稿 -e 审定 制度"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 模板.md keeps its draft marker.", "Turn 2 adds the header to the four reviewed files only, not to 已发布/考勤.md."],
        reply="四份制度的草稿标记已删除并在首行加了审定注释，模板和已发布目录未改，grep 检查过。DONE",
        desc="Two turns: removes a draft marker from policy docs except the template, then stamps the reviewed ones", family="fam-doc-b14-draftmark-01")


# ------------------------------------------------------------------ 6. parametrised families (more scopes, formats, languages)


def kv_family(cid, *, root, fname, names, protect, line_old, line_new, decoy_line, lang, prompt, prompt2=None, op2=None, readme, family, desc, extra_lines=()):
    rng = Random(int(cid.split("-")[1]))
    files = {}
    for n in names + protect:
        body = ["# %s" % n.split("/")[-1], line_old, decoy_line] + [l.format(n=rng.randint(1, 99)) for l in extra_lines]
        rng.shuffle(body[1:])
        files["%s/%s/%s" % (root, n, fname)] = lines(body)
    files["%s/README.md" % root] = lines(readme)
    excl = ["/%s/" % p.split("/")[0] for p in protect]
    ops = [[{"op": "line", "prefix": root + "/", "name": "%s$" % fname.replace(".", "\\."), "exclude": excl, "map": [[line_old, line_new]]}]]
    turns = [prompt]
    find = "find %s -name '%s'%s" % (root, fname, "".join(" -not -path '*%s*'" % e for e in excl))
    sed = lambda a, b: "%s | xargs sed -i 's|^%s$|%s|'" % (find, a.replace(".", "\\.").replace("[", "\\["), b)
    cmds = [sed(line_old, line_new)]
    if prompt2:
        ops.append([dict(ops[0][0], map=[op2])])
        turns.append(prompt2)
        cmds.append(sed(*op2))
    cmds.append("grep -rn '%s' %s" % (line_old.split("=")[0].split(":")[0].strip(), root))
    zh = lang == "zh"
    return edit_case(
        cid, files=files, targets=[root], ops=ops, turns=turns, cmds=cmds, traps=["TR-READONLY"],
        trap_notes=["TR-READONLY: %s stay unchanged per %s/README.md." % (", ".join(protect), root),
                    "Decoy line `%s` shares text with the target line." % decoy_line],
        reply=("已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE" if zh else "Changed the target line in every in-scope file; the protected folders and the look-alike line are untouched. Checked with grep. DONE"),
        desc=desc, family=family)


FAMILIES = [
    ("cfg-10111", dict(root="nginx/sites", fname="site.conf", names=["shop", "blog", "admin", "status"], protect=["staging"],
                       line_old="    client_max_body_size 10m;", line_new="    client_max_body_size 50m;", decoy_line="    # client_max_body_size 10m; (old default)", lang="en",
                       prompt="Raise client_max_body_size from 10m to 50m in every site config under nginx/sites, except where the README says not to. Check and reply DONE.",
                       readme=["# Sites", "", "staging/ mirrors production limits on its own schedule; leave it."],
                       family="fam-cfg-b14-nginxbody-01", desc="Raises a body-size limit across nginx site configs while staging and a commented copy of the line stay")),
    ("cfg-10112", dict(root="定时任务", fname="cron.conf", names=["对账", "清理", "推送", "统计", "备份"], protect=["停用"],
                       line_old="时区=UTC", line_new="时区=Asia/Shanghai", decoy_line="日志时区=UTC", lang="zh",
                       prompt="定时任务 下各任务的 时区=UTC 都改成 时区=Asia/Shanghai，按 README 来。改完检查，回复 DONE。",
                       readme=["# 定时任务", "", "停用/ 里的任务已经下线，配置原样留着备查。日志时区 是另一个设置，保持 UTC。"],
                       family="fam-cfg-b14-crontz-01", desc="Changes a timezone key in task configs while a longer key with the same value and a disabled folder stay")),
    ("cfg-10113", dict(root="ci/pipelines", fname="pipeline.yml", names=["web", "api", "mobile", "docs"], protect=["release-legacy"],
                       line_old="  node: 18", line_new="  node: 20", decoy_line="  # node: 18 pinned by legacy runner", lang="en",
                       prompt="Move the CI pipelines under ci/pipelines from node 18 to node 20, minding the README. Verify and reply DONE.",
                       prompt2="Also bump the cache key version from v3 to v4 in the same pipelines. Check and reply DONE.",
                       op2=["  cache_key: deps-v3", "  cache_key: deps-v4"], extra_lines=("  cache_key: deps-v3",),
                       readme=["# Pipelines", "", "release-legacy/ builds old branches and must keep node 18 and its cache."],
                       family="fam-cfg-b14-cinode-01", desc="Two turns: moves pipelines to a new runtime, then bumps a cache key, leaving a legacy pipeline")),
    ("cfg-10114", dict(root="门店配置", fname="收银.ini", names=["一号店", "二号店", "三号店", "四号店"], protect=["测试店"],
                       line_old="小票抬头=星河便利", line_new="小票抬头=星河便利（新）", decoy_line="备注=小票抬头=星河便利 为旧版", lang="zh",
                       prompt="门店配置 下各门店收银.ini 的 小票抬头 从「星河便利」改成「星河便利（新）」，测试店别改。改完核对，回复 DONE。",
                       readme=["# 门店配置", "", "测试店/ 用于收银机联调，配置不跟随正式门店。"],
                       family="fam-cfg-b14-receipt-01", desc="Changes a receipt header in store configs while a remark repeating it and a test store stay")),
    ("cfg-10115", dict(root="services", fname="feature-flags.properties", names=["checkout", "catalog", "profile", "search", "reviews"], protect=["canary"],
                       line_old="new_ui=false", line_new="new_ui=true", decoy_line="new_ui_beta=false", lang="en",
                       prompt="Turn on new_ui in every service's feature-flags.properties, except where the README says otherwise. Don't touch the beta flag. Check and reply DONE.",
                       readme=["# Services", "", "canary/ flags are flipped by the release bot only."],
                       family="fam-cfg-b14-featureflag-01", desc="Flips one feature flag across services while a longer flag name and a canary folder stay")),
    ("cfg-10116", dict(root="监控/规则", fname="告警.yaml", names=["接口", "数据库", "缓存", "队列"], protect=["演练"],
                       line_old="  阈值: 80", line_new="  阈值: 90", decoy_line="  恢复阈值: 80", lang="zh",
                       prompt="监控/规则 下的告警阈值 80 统一调到 90，按 README 的范围改。改完检查，回复 DONE。",
                       prompt2="通知渠道也一起从 邮件 改成 企业微信，范围同上。改完再检查一遍，回复 DONE。",
                       op2=["  通知: 邮件", "  通知: 企业微信"], extra_lines=("  通知: 邮件",),
                       readme=["# 告警规则", "", "演练/ 是故障演练用的规则，参数固定不改。恢复阈值 和 阈值 是两个参数。"],
                       family="fam-cfg-b14-alertthreshold-01", desc="Two turns: raises an alert threshold, then switches the notify channel, leaving drill rules and a look-alike key")),
    ("cfg-10117", dict(root="apps", fname="Dockerfile", names=["frontend", "backend", "worker", "cron"], protect=["third_party/pdf-render"],
                       line_old="FROM node:18-alpine", line_new="FROM node:20-alpine", decoy_line="# FROM node:18-alpine used before 2026", lang="en",
                       prompt="Update the base image in our app Dockerfiles from node:18-alpine to node:20-alpine. Third-party images stay as they are. Verify and reply DONE.",
                       readme=["# Apps", "", "third_party/ holds vendored images we do not maintain."],
                       family="fam-cfg-b14-dockerbase-01", desc="Updates a base image across Dockerfiles while a comment repeating it and vendored images stay")),
    ("cfg-10118", dict(root="渠道配置", fname="支付.conf", names=["微信", "支付宝", "银联", "云闪付"], protect=["沙箱"],
                       line_old="回调地址=https://pay.old.example.cn/notify", line_new="回调地址=https://pay.example.cn/v2/notify",
                       decoy_line="退款回调地址=https://pay.old.example.cn/notify", lang="zh",
                       prompt="各支付渠道的 回调地址 要换成 https://pay.example.cn/v2/notify，退款回调先不动，沙箱也不动。改完检查，回复 DONE。",
                       readme=["# 渠道配置", "", "沙箱/ 对接的是测试网关，地址不跟正式环境。"],
                       family="fam-cfg-b14-paycallback-01", desc="Changes a callback URL key across channel configs while a refund key with the same URL and a sandbox stay")),
    ("cfg-10119", dict(root="infra/terraform", fname="variables.tf", names=["vpc", "rds", "eks", "s3"], protect=["modules-vendor/aws-legacy"],
                       line_old='  default = "us-east-1"', line_new='  default = "eu-west-1"', decoy_line='  # dr_region default = "us-east-1"', lang="en",
                       prompt="We're moving regions: change the default region from us-east-1 to eu-west-1 in each stack's variables.tf, skipping the vendored modules. Check and reply DONE.",
                       readme=["# Terraform", "", "modules-vendor/ are upstream modules pinned by version; never edit them."],
                       family="fam-cfg-b14-tfregion-01", desc="Changes a default region across stack variables while a DR comment and vendored modules stay")),
    ("cfg-10120", dict(root="小程序/页面配置", fname="page.json", names=["首页", "分类", "购物车", "我的"], protect=["已下线"],
                       line_old='  "navigationBarBackgroundColor": "#ffffff",', line_new='  "navigationBarBackgroundColor": "#1677ff",',
                       decoy_line='  "backgroundColor": "#ffffff",', lang="zh",
                       prompt="小程序各页面的导航栏背景色从 #ffffff 改成 #1677ff，页面背景色别动，已下线的页面也不用改。改完检查，回复 DONE。",
                       readme=["# 页面配置", "", "已下线/ 的页面保留原配置备查。"],
                       family="fam-cfg-b14-navcolor-01", desc="Changes a nav-bar color across page configs while the page background with the same value and retired pages stay")),
    ("cfg-10121", dict(root="db/migrations-config", fname="flyway.conf", names=["orders", "users", "payments"], protect=["archive-2024"],
                       line_old="flyway.baselineOnMigrate=false", line_new="flyway.baselineOnMigrate=true", decoy_line="flyway.validateOnMigrate=false", lang="en",
                       prompt="Enable baselineOnMigrate in each flyway.conf under db/migrations-config, leaving the archive alone. Check and reply DONE.",
                       prompt2="Now set flyway.validateOnMigrate=true in the same three configs. Verify and reply DONE.",
                       op2=["flyway.validateOnMigrate=false", "flyway.validateOnMigrate=true"],
                       readme=["# Flyway", "", "archive-2024/ is kept for audit; byte-identical."],
                       family="fam-cfg-b14-flyway-01", desc="Two turns: enables one flyway option, then a second similar option, leaving an audit archive")),
    ("cfg-10122", dict(root="打印模板", fname="设置.ini", names=["发票", "出库单", "对账单", "合同"], protect=["旧版"],
                       line_old="纸张=A4", line_new="纸张=A5", decoy_line="备用纸张=A4", lang="zh",
                       prompt="打印模板 下各模板的 纸张 从 A4 改成 A5（备用纸张不改，旧版目录不改）。改完核对一下，回复 DONE。",
                       readme=["# 打印模板", "", "旧版/ 给老打印机用，参数不能动。"],
                       family="fam-cfg-b14-papersize-01", desc="Changes a paper size key across print templates while a backup key and an old-template folder stay")),
]


def _fam(cid, kw):
    def build():
        return kv_family(cid, **kw)
    build.__name__ = cid.replace("-", "_")
    return build


for _cid, _kw in FAMILIES:
    BUILDERS.append(_fam(_cid, _kw))


# ------------------------------------------------------------------ 7. text substitutions in docs/code (parametrised)


def sub_family(cid, *, root, ext, names, protect, pattern, repl, sed, body, lang, prompt, readme, family, desc, trap):
    rng = Random(int(cid.split("-")[1]))
    files = {}
    for n in names + protect:
        files["%s/%s%s" % (root, n, ext)] = lines([l.format(n=n.split("/")[-1], r=rng.randint(2, 99)) for l in body])
    files["%s/README.md" % root] = lines(readme)
    excl = ["%s/%s" % (root, p.split("/")[0] + "/") for p in protect]
    ops = [[{"op": "sub", "prefix": root + "/", "name": r"%s$" % ext.replace(".", "\\."), "exclude": excl + ["README.md"], "pattern": pattern, "repl": repl}]]
    find = "find %s -name '*%s'%s" % (root, ext, "".join(" -not -path '*/%s/*'" % p.split("/")[0] for p in protect))
    zh = lang == "zh"
    return edit_case(
        cid, files=files, targets=[root], ops=ops, turns=[prompt], cmds=["%s | xargs sed -i -E '%s'" % (find, sed), "grep -rnF '%s' %s" % (repl.split("\\")[0][:12], root)],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: %s stay unchanged per %s/README.md." % (", ".join(protect), root), trap],
        reply=("已全部改完，保护范围和容易误伤的写法都保留，grep 检查过。DONE" if zh else "Done across the in-scope files; the protected folder and the look-alike text are unchanged. Checked with grep. DONE"),
        desc=desc, family=family)


SUBS = [
    ("doc-10123", dict(root="docs/api", ext=".md", names=["orders", "users", "carts", "coupons", "refunds"], protect=["v1/legacy"],
                       pattern=r"/api/v2/", repl="/api/v3/", sed="s#/api/v2/#/api/v3/#g",
                       body=["# {n}", "", "GET /api/v2/{n}", "Deprecated alias: /api/v2beta/{n}", "Rate limit {r}/s"], lang="en",
                       prompt="The API moved to v3: update the /api/v2/ paths in docs/api to /api/v3/. Leave the legacy folder, and the v2beta aliases are a separate thing. Verify and reply DONE.",
                       readme=["# API docs", "", "v1/ documents retired endpoints and stays as written."],
                       trap="/api/v2beta/ starts with /api/v2 but is not /api/v2/; matching the slash keeps it.",
                       family="fam-doc-b14-apiv3-01", desc="Moves documented API paths to a new version while a beta alias and legacy docs stay")),
    ("doc-10124", dict(root="培训资料", ext=".md", names=["第一课", "第二课", "第三课", "第四课"], protect=["归档/2024版"],
                       pattern=r"钉钉群", repl="企业微信群", sed="s/钉钉群/企业微信群/g",
                       body=["# {n}", "", "课后问题请发到钉钉群。", "钉钉号：dd-{r}（个人号，不用改）", "作业截止前在钉钉群提交。"], lang="zh",
                       prompt="培训 改用企业微信了，把 培训资料 里的「钉钉群」都换成「企业微信群」，个人钉钉号不改，归档的旧版别动。改完检查，回复 DONE。",
                       readme=["# 培训资料", "", "归档/ 是往期版本，保持原样。"],
                       trap="钉钉号 also starts with 钉钉 but is a personal account id; only 钉钉群 changes.",
                       family="fam-doc-b14-imgroup-01", desc="Replaces a chat-group name across course notes while a personal account line and an archive stay")),
    ("code-10125", dict(root="src/handlers", ext=".go", names=["order", "user", "cart", "coupon", "refund"], protect=["generated/pb"],
                        pattern=r"\blog\.Printf\(", repl="slog.Info(", sed="s/\\blog\\.Printf\\(/slog.Info(/g",
                        body=["package handlers", "", "func handle{n}() {{", "\tlog.Printf(\"{n} start\")", "\tcatalog.Printf(\"x\")", "}}"], lang="en",
                        prompt="Switch log.Printf( calls to slog.Info( in src/handlers, but not in generated code. Be careful not to hit other identifiers that end in log. Verify and reply DONE.",
                        readme=["# Handlers", "", "generated/ is protoc output; never edit by hand."],
                        trap="catalog.Printf( ends with log.Printf(; a pattern without a word boundary rewrites it to catalslog.Info(.",
                        family="fam-code-b14-slog-01", desc="Rewrites a logging call across handlers with a word boundary while a longer identifier and generated code stay")),
    ("doc-10126", dict(root="客服话术", ext=".md", names=["售前", "售后", "投诉", "物流"], protect=["旧话术/2023版"],
                       pattern=r"400-800-1234", repl="400-800-5678", sed="s/400-800-1234/400-800-5678/g",
                       body=["# {n}", "", "客服热线 400-800-1234。", "传真 0571-400-800-12340（总部，不改）", "工作时间 9:00-21:00。"], lang="zh",
                       prompt="客服热线换号了：客服话术 里的 400-800-1234 换成 400-800-5678，旧话术目录不动。改完检查，回复 DONE。",
                       readme=["# 客服话术", "", "旧话术/ 是存档，不再使用，也不修改。"],
                       trap="The fax number contains 400-800-1234 as a substring (…12340); an unbounded replace corrupts it.",
                       family="fam-doc-b14-hotline-01", desc="Changes a hotline number across scripts while a longer number containing it and an archive stay")),
]
# the hotline fax trap needs a boundary; tighten pattern and sed so the fax (…12340) survives
SUBS[3][1]["pattern"] = r"400-800-1234(?![0-9])"
SUBS[3][1]["sed"] = "s/400-800-1234([^0-9]|$)/400-800-5678\\1/g"


def _sub(cid, kw):
    def build():
        return sub_family(cid, **kw)
    build.__name__ = cid.replace("-", "_")
    return build


for _cid, _kw in SUBS:
    BUILDERS.append(_sub(_cid, _kw))


# ------------------------------------------------------------------ 8. moves by name (parametrised)


@reg
def fs_10127():
    rng = Random(10127)
    files = {}
    for i in range(18):
        m = rng.choice(["07", "08", "09"])
        files["下载/账单-2026%s%02d-%d.pdf" % (m, rng.randint(1, 28), i)] = "pdf\n"
    files["下载/账单模板.pdf"] = "pdf\n"
    files["下载/说明.txt"] = "按月份把账单归到 账单/2026-07 这类目录；账单模板 不是账单。\n"
    ops = [[{"op": "rename", "prefix": "下载/账单-2026", "pattern": r"^下载/(账单-2026(0[7-9])\d\d-\d+\.pdf)$", "repl": r"账单/2026-\2/\1"}]]
    return edit_case(
        "fs-10127", files=files, targets=["下载", "账单"], ops=ops, keep=["账单/2026-07", "账单/2026-08", "账单/2026-09"],
        turns=["下载 目录里那堆账单 PDF，按文件名里的月份归档到 账单/2026-07、账单/2026-08、账单/2026-09 这几个目录。模板别动。弄完列一下目录确认，回复 DONE。"],
        cmds=["for m in 07 08 09; do mkdir -p 账单/2026-$m; for f in 下载/账单-2026$m*.pdf; do mv \"$f\" 账单/2026-$m/; done; done", "ls 下载 账单/*"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 账单模板.pdf starts with 账单 but is not a bill (说明.txt)."],
        reply="账单已按月份归到 账单/2026-07、08、09，模板留在 下载，已列目录确认。DONE",
        desc="Files bills into per-month folders by the date in their names while a template with a similar name stays", family="fam-fs-b14-billmonths-01")


@reg
def fs_10128():
    rng = Random(10128)
    files = {}
    for i in range(16):
        kind = rng.choice(["invoice", "receipt", "quote"])
        files["shared/%s_%04d.pdf" % (kind, rng.randint(1, 9999))] = "pdf\n"
    files["shared/invoice_template.pdf"] = "pdf\n"
    files["shared/README.md"] = lines(["# Shared drop", "", "Sort by prefix into finance/<kind>s/. invoice_template.pdf is the blank form; it stays here."])
    ops = [[{"op": "rename", "prefix": "shared/", "pattern": r"^shared/((invoice|receipt)_\d{4}\.pdf)$", "repl": r"finance/\2s/\1"}]]
    return edit_case(
        "fs-10128", files=files, targets=["shared", "finance"], ops=ops, keep=["finance/invoices", "finance/receipts"],
        turns=["Sort the invoices and receipts in shared/ into finance/invoices and finance/receipts. Quotes stay put, and so does anything the README says. List the folders after and reply DONE."],
        cmds=["mkdir -p finance/invoices finance/receipts && for f in shared/invoice_[0-9]*.pdf; do mv \"$f\" finance/invoices/; done && for f in shared/receipt_*.pdf; do mv \"$f\" finance/receipts/; done",
              "ls shared finance/invoices finance/receipts"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: invoice_template.pdf matches invoice_* but stays (README).", "Quotes stay in shared/."],
        reply="Moved the invoices to finance/invoices and receipts to finance/receipts; quotes and the blank invoice template are still in shared/. Listed all three to confirm. DONE",
        desc="Sorts dropped PDFs into folders by name prefix while a template with the same prefix and quotes stay", family="fam-fs-b14-sortdrop-01")


@reg
def fs_10129():
    rng = Random(10129)
    files = {}
    for d in ["素材/海报", "素材/详情页", "素材/主图"]:
        for i in range(5):
            files["%s/图%02d.PNG" % (d, i)] = "png\n"
        files["%s/说明.txt" % d] = "本目录素材\n"
    files["素材/外部/合作方LOGO.PNG"] = "png\n"
    files["素材/README.md"] = lines(["# 素材", "", "外部/ 是合作方提供的原文件，文件名必须保持原样。"])
    return edit_case(
        "fs-10129", files=files, targets=["素材"],
        ops=[[{"op": "rename", "prefix": "素材/", "name": r"\.PNG$", "exclude": ["/外部/"], "pattern": r"\.PNG$", "repl": ".png"}],
             [{"op": "rename", "prefix": "素材/主图/", "name": r"\.png$", "pattern": r"/图(\d\d)\.png$", "repl": r"/主图_\1.png"}]],
        turns=["素材 下的 .PNG 扩展名统一改成小写 .png（外部目录除外）。改完列出来确认，回复 DONE。",
               "主图 目录里的 图01.png 这种名字再改成 主图_01.png 的格式。改完再列一下，回复 DONE。"],
        cmds=["for f in $(find 素材 -name '*.PNG' -not -path '*/外部/*'); do mv \"$f\" \"${f%.PNG}.png\"; done",
              "for f in 素材/主图/图*.png; do mv \"$f\" \"素材/主图/主图_${f##*/图}\"; done", "find 素材 -type f | sort"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: 素材/外部/ keeps the partner's original name.", "Turn 2 renames only 主图/ files."],
        reply="扩展名已统一为 .png，主图目录的文件已改成 主图_NN.png，外部目录未改，已列出确认。DONE",
        desc="Two turns: lower-cases an image extension across folders, then renames one folder's files to a pattern", family="fam-fs-b14-pngcase-01")


@reg
def fs_10130():
    rng = Random(10130)
    files = {}
    for host in ["web-1", "web-2", "web-3"]:
        for d in range(1, 6):
            rows = ["2026-09-0%d %s %s" % (d, rng.choice(["INFO", "WARN"]), rng.choice(["ok", "slow", "retry"])) for _ in range(5)]
            rows.insert(2, "2026-09-0%d DEBUG heartbeat" % d)
            files["logs/%s/2026-09-0%d.log" % (host, d)] = lines(rows)
    files["logs/web-3/KEEP"] = "web-3 logs are under legal hold; do not modify.\n"
    return edit_case(
        "fs-10130", files=files, targets=["logs"],
        ops=[[{"op": "del", "prefix": "logs/", "name": r"\.log$", "exclude": ["logs/web-3/"], "pattern": r"\S+ DEBUG heartbeat"}]],
        turns=["Strip the DEBUG heartbeat lines out of the web logs under logs/ to shrink them. Check each host folder for notes first. Verify and reply DONE."],
        cmds=["find logs -name '*.log' -not -path '*/web-3/*' | xargs sed -i '/ DEBUG heartbeat$/d'", "grep -rc heartbeat logs"],
        traps=["TR-READONLY"], trap_notes=["TR-READONLY: logs/web-3/KEEP puts that host under legal hold."],
        reply="Removed the heartbeat lines from web-1 and web-2 logs; web-3 is under legal hold and untouched. grep -c confirms. DONE",
        desc="Deletes heartbeat lines across host logs while one host is under a legal hold marker", family="fam-fs-b14-heartbeat-01")
