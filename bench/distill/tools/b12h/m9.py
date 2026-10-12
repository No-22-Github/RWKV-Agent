"""M9b bulk edits across file trees, batch b12h of v1.41: ids 9201-9220.

Twenty bash_edit cases, each touching 3+ files (or a pattern across a tree) with a README-protected
exclusion: key/value rewrites, renames, header/footer insertion, delimiter conversion, path rewriting,
whitespace/line-ending cleanup, deletion of generated files. One bounded bash action per case; the
criterion lives in a README the prompt points at."""
import json
import os
from random import Random

from common import lines
from common import write_case as _write_case

REFS = {}
_SPEC = {}


def write_case(cid, *, files, verify, **kw):
    """Adds a per-file line-count guard so deleting any fixture line breaks verify."""
    guard = "LINES = %r\nfor _p, _n in LINES.items():\n    assert len(case[\"files\"][_p].splitlines()) == _n, _p\n" % {p: len(t.splitlines()) for p, t in files.items()}
    verify = verify.replace('case = json.load(open("case.json"))\n', 'case = json.load(open("case.json"))\n' + guard, 1)
    return _write_case(cid, files=files, verify=verify, **kw)


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def files_check(rules, originals):
    def check(_out, root):
        for path, rule in rules.items():
            full = os.path.join(root, path)
            if rule.get("absent"):
                if os.path.exists(full):
                    return "%s should be gone" % path
                continue
            if not os.path.exists(full):
                return "%s missing" % path
            want = rule["equals"] if "equals" in rule else originals[path]
            text = open(full, encoding="utf-8", newline="").read()
            if text != want:
                return "%s = %r" % (path, text[:200])
        return None
    return check


def rules_for(files, final):
    out = {}
    for path, text in files.items():
        if path not in final:
            out[path] = {"absent": True}
        elif final[path] == text:
            out[path] = {"unchanged": True}
        else:
            out[path] = {"equals": final[path]}
    for path, text in final.items():
        if path not in files:
            out[path] = {"equals": text}
    return out


EDIT_VERIFY = '''
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = __LINES__
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F[__README__].startswith(__HEAD__)
__SRC__
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == __K__
print(json.dumps({"files": changed}))
'''

PLAN_FROM_REWRITE = '''
def plan(files):
    out = {}
    for path, text in files.items():
        new = rewrite(path, text)
        out[path] = text if new is None else new
    return out
'''


def edit_case(cid, *, topic, desc, prompt, files, readme, cmd, check, target, traps, decoys, alts, why,
              rewrite_src=None, plan_src=None, task_type="bulk_edit", level="L2"):
    task_type = {"scr": "fix_output", "tab": "write_summary"}.get(cid.split("-")[0], task_type)
    if cid == "doc-9217":
        task_type = "write_structured"
    ns = {}
    if rewrite_src is not None:
        src = rewrite_src.strip("\n") + "\n" + PLAN_FROM_REWRITE
    else:
        src = plan_src.strip("\n")
    exec(src, ns)
    final = ns["plan"](files)
    touched = sum(1 for p in files if p not in final or final[p] != files[p]) + sum(1 for p in final if p not in files)
    changed = sum(1 for p in files if p not in final or final[p] != files[p])
    assert changed >= 3, (cid, changed)
    rules = rules_for(files, final)
    head = files[readme].split("\n")[0]
    k = len({p for p in final if files.get(p) != final[p]}) + len([p for p in files if p not in final])
    verify = (EDIT_VERIFY.replace("__LINES__", repr({p: len(t.splitlines()) for p, t in files.items()}))
              .replace("__README__", repr(readme)).replace("__HEAD__", repr(head))
              .replace("__SRC__", src).replace("__K__", str(k)))
    trap_lines = "\n".join(f"- {k_}: {v}" for k_, v in traps.items())
    notes = f"""## Traps
{trap_lines}

## Reference solution
1. bash: `{cmd}`
2. bash: `{check}` to confirm the target files changed and the protected ones did not.
Final answer: DONE ({why}).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.
""" + phrasings(*alts)
    REFS[cid] = (files, [cmd, check], files_check(rules, files))
    _SPEC[cid] = dict(kind="bash_edit", sub="M9b", targets=[target])
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12h-{topic}-01", level=level, ref_calls=2,
        traps=list(traps), decoys=decoys, axes=["CON", "OBS"], files=files, verify=verify, notes=notes,
        case_expect={"files": rules},
        turns=[{"prompt": prompt, "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


# ---------------------------------------------------------------- key/value rewrites


def cfg_9201():
    rng = Random(9201)
    files = {}
    for env in ["dev", "test", "staging", "qa", "prod"]:
        files[f"env/{env}.env"] = lines([f"APP_NAME=shop-{env}", "DB_HOST=db-old.internal", "REPLICA_DB_HOST=db-old.internal",
                                          f"DB_PORT={rng.choice([5432, 5433])}", "POOL=10"])
    files["env/README.md"] = lines(["# 环境变量说明", "", "每个环境一个 .env 文件。prod.env 要等周六的维护窗口再切换，现在不要动。",
                                     "REPLICA_DB_HOST 是只读副本，由 DBA 单独迁移，不在这次范围内。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("env/") or not path.endswith(".env") or path == "env/prod.env":
        return None
    new = text.replace("\\nDB_HOST=db-old.internal\\n", "\\nDB_HOST=db-new.internal\\n")
    return new if new != text else None
'''
    return edit_case(
        "cfg-9201", topic="dbhost", desc="Points DB_HOST at the new database host in four env files while prod.env and the look-alike REPLICA_DB_HOST key stay",
        prompt="数据库换了新机器：env 目录下各 .env 里的 DB_HOST 从 db-old.internal 改成 db-new.internal。哪些文件和配置项先不动，env/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="env/README.md",
        cmd=r"""find env -name '*.env' | grep -v prod.env | xargs sed -i 's/^DB_HOST=db-old.internal$/DB_HOST=db-new.internal/'""",
        check="grep -rn DB_HOST env", target="env",
        traps={"TR-READONLY": "env/prod.env switches at the Saturday maintenance window (env/README.md).",
               "TR-DECOY": "REPLICA_DB_HOST=db-old.internal contains DB_HOST=db-old.internal as a substring and is migrated by the DBAs; an unanchored sed would change it."},
        decoys={"TR-READONLY": None, "TR-DECOY": "REPLICA_DB_HOST"},
        alts=["env 里的 .env 文件把 DB_HOST 换成 db-new.internal，README 里标注暂缓的别改，改完确认并回复 DONE。",
              "批量修改 env/*.env 的 DB_HOST（db-old.internal → db-new.internal），副本主机那一项不属于本次，检查后回复 DONE。",
              "各环境的数据库主机地址要切到 db-new.internal，只改 DB_HOST 这个键；env/README.md 说不动的保持原样，完成后回复 DONE。",
              "把 env 目录下 DB_HOST=db-old.internal 全部换成新地址 db-new.internal，prod 暂时跳过，核对后回复 DONE。",
              "更新 env 下的环境文件：DB_HOST 指向 db-new.internal，其余键不变，按 README 的说明排除例外，然后回复 DONE。"],
        why="dev, test, staging and qa now use db-new.internal; prod.env and every REPLICA_DB_HOST are unchanged", task_type="edit_value")


def cfg_9202():
    files = {}
    for name, tag in [("api", "v1.4.2"), ("web", "v1.4.2"), ("worker", "v1.4.2"), ("cron", "v1.4.2"), ("billing-legacy", "v1.4.2")]:
        rows = [f"name: {name}", "image:", f"  repo: registry.local/{name}", f"  tag: {tag}", "replicas: 2"]
        if name in ("api", "cron"):
            rows += ["sidecar:", "  image: registry.local/envoy", "  tag: v1.4.20"]
        if name == "worker":
            rows += ["migration:", "  tag_hint: v1.4.2"]
        files[f"charts/{name}/values.yaml"] = lines(rows)
    files["charts/README.md"] = lines(["# Charts", "", "Only the top-level image tag moves with this release.",
                                        "billing-legacy stays pinned until finance signs off on the new build.",
                                        "Sidecar versions follow their own schedule."])
    src = '''
def rewrite(path, text):
    if not path.startswith("charts/") or not path.endswith("values.yaml") or "billing-legacy" in path:
        return None
    new = text.replace("\\nimage:\\n  repo: registry.local/", "\\nimage:\\n  repo: registry.local/")
    rows = ["  tag: v1.5.0" if r == "  tag: v1.4.2" else r for r in text.split("\\n")]
    new = "\\n".join(rows)
    return new if new != text else None
'''
    return edit_case(
        "cfg-9202", topic="imagetag", desc="Bumps the top-level image tag in four chart values files while a pinned legacy chart and look-alike sidecar tags stay",
        prompt="Release day: in every charts/*/values.yaml bump the image tag from v1.4.2 to v1.5.0. charts/README.md says which chart and which tags must stay as they are. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="charts/README.md",
        cmd=r"""find charts -name values.yaml | grep -v billing-legacy | xargs sed -i 's/^  tag: v1.4.2$/  tag: v1.5.0/'""",
        check="grep -rn 'tag' charts", target="charts",
        traps={"TR-READONLY": "charts/billing-legacy stays pinned (charts/README.md).",
               "TR-DECOY": "sidecar `tag: v1.4.20` and `tag_hint: v1.4.2` look like the image tag; only the two-space-indented top-level `  tag: v1.4.2` line changes."},
        decoys={"TR-READONLY": None, "TR-DECOY": "tag_hint"},
        alts=["Bump the image tag v1.4.2 to v1.5.0 in the values.yaml of each chart, except the pinned one; sidecars are separate. Verify and reply DONE.",
              "In charts, change `tag: v1.4.2` under image to v1.5.0 for every service chart the README allows, then confirm and say DONE.",
              "charts 下各个 values.yaml 的镜像 tag 从 v1.4.2 升到 v1.5.0，README 里说保持不变的别动，改完检查并回复 DONE。",
              "Update the app image tag to v1.5.0 across charts/*/values.yaml (v1.4.2 only), leaving billing-legacy and the sidecar tags alone. Reply DONE once checked.",
              "Please roll every chart's image tag forward from v1.4.2 to v1.5.0 except where charts/README.md says otherwise, check, and reply DONE."],
        why="api, web, worker and cron now use tag v1.5.0; billing-legacy and the sidecar and hint lines are unchanged", task_type="edit_value")


def cfg_9203():
    files = {}
    for name in ["sync", "report", "cleanup", "export", "nightly"]:
        files[f"jobs/{name}.toml"] = lines([f'name = "{name}"', "retries = 3", "max_retries = 3", "backoff = 30"] + (['[alert]', 'retries = 3'] if name == "export" else []))
    files["jobs/README.md"] = lines(["# 定时任务", "", "nightly.toml 由运维托管，别手改。", "max_retries 是硬上限，不随 retries 调整。",
                                      "[alert] 段里的 retries 指告警重发次数，同样保持 3。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("jobs/") or not path.endswith(".toml") or path == "jobs/nightly.toml":
        return None
    rows = text.split("\\n")
    out, section = [], ""
    for r in rows:
        if r.startswith("["):
            section = r
        out.append("retries = 5" if (r == "retries = 3" and section == "") else r)
    new = "\\n".join(out)
    return new if new != text else None
'''
    return edit_case(
        "cfg-9203", topic="retries", desc="Raises the top-level retries from 3 to 5 in four job toml files while a managed file, max_retries and an alert-section retries stay",
        prompt="jobs 目录下各任务 .toml 里顶层的 retries 从 3 改成 5。哪些文件和配置项不能动，jobs/README.md 里有说明。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="jobs/README.md",
        cmd=r"""find jobs -name '*.toml' | grep -v nightly.toml | xargs sed -i '/^\[/,$!s/^retries = 3$/retries = 5/'""",
        check="grep -rn retries jobs", target="jobs",
        traps={"TR-READONLY": "jobs/nightly.toml is managed by ops (jobs/README.md).",
               "TR-DECOY": "max_retries = 3 and the [alert] section's own `retries = 3` look the same; only the top-level key changes."},
        decoys={"TR-READONLY": None, "TR-DECOY": "max_retries"},
        alts=["把 jobs/*.toml 顶层的 retries = 3 全部改为 5，README 里提到的例外别碰，检查后回复 DONE。",
              "各任务配置里的重试次数 retries 从 3 调到 5（只改顶层那一项），按 jobs/README.md 排除不该改的，完成后回复 DONE。",
              "jobs 下的 toml，retries 改成 5，max_retries 和 [alert] 里的不动，nightly 也不动，核对后回复 DONE。",
              "批量把任务配置的 retries 由 3 提高到 5，注意 README 的说明，改完确认并回复 DONE。",
              "请更新 jobs 里托管之外的所有 .toml：顶层 retries 设为 5，其余保持原样，检查完回复 DONE。"],
        why="sync, report, cleanup and export have retries = 5; nightly.toml, max_retries and the [alert] retries are unchanged", task_type="edit_value")


def cfg_9215():
    files = {}
    for env in ["dev", "test", "staging", "qa", "prod"]:
        files[f"flags/{env}.json"] = lines(["{", '  "beta": false,', '  "beta_ui": false,', '  "dark_mode": true,', f'  "env": "{env}"', "}"])
    files["flags/README.md"] = lines(["# 功能开关", "", "每个环境一个 json。prod.json 的开关要走发布评审，不能直接改。",
                                       "beta_ui 是单独的界面开关，保持 false。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("flags/") or not path.endswith(".json") or path == "flags/prod.json":
        return None
    new = text.replace('"beta": false', '"beta": true')
    return new if new != text else None
'''
    return edit_case(
        "cfg-9215", topic="betaflag", desc="Turns the beta flag on in four environment json files while prod.json and the look-alike beta_ui flag stay off",
        prompt="flags 目录里各环境 json 的 beta 开关从 false 改成 true。哪些文件和开关不能动，flags/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="flags/README.md",
        cmd=r"""find flags -name '*.json' | grep -v prod.json | xargs sed -i 's/"beta": false/"beta": true/'""",
        check="grep -rn beta flags", target="flags",
        traps={"TR-READONLY": "flags/prod.json needs a release review (flags/README.md).",
               "TR-DECOY": '"beta_ui": false is a separate switch with a similar name.'},
        decoys={"TR-READONLY": None, "TR-DECOY": "beta_ui"},
        alts=["把 flags 下各环境配置里的 beta 打开（false 改 true），生产环境和 beta_ui 不要动，检查后回复 DONE。",
              "批量开启 beta 功能开关：flags/*.json 里 \"beta\": false 换成 true，README 里的例外保持原样，完成后回复 DONE。",
              "flags 里除 prod 外每个 json 的 beta 设成 true，beta_ui 另算，不改，改完核对并回复 DONE。",
              "请在 flags 目录里把 beta 开关全部置为 true，遵守 flags/README.md 的限制，然后检查并回复 DONE。",
              "各环境的 beta 开关改成开启状态（只改 beta 这个键），其他开关与生产配置保持不变，确认后回复 DONE。"],
        why="dev, test, staging and qa have beta true; prod.json and every beta_ui are unchanged", task_type="edit_value")


def cfg_9216():
    files = {}
    for name in ["app", "worker", "gateway", "batch", "audit"]:
        files[f"conf/{name}.properties"] = lines([f"app.name={name}", "log4j.rootLogger=INFO, stdout", "log4j.logger.audit=INFO", "log4j.appender.stdout=console"])
    files["conf/README.txt"] = lines(["Logging notes", "", "audit.properties is owned by the compliance team: never edit it.",
                                       "log4j.logger.audit is a named logger with its own level; leave it at INFO."])
    src = '''
def rewrite(path, text):
    if not path.startswith("conf/") or not path.endswith(".properties") or path == "conf/audit.properties":
        return None
    new = text.replace("\\nlog4j.rootLogger=INFO,", "\\nlog4j.rootLogger=WARN,")
    return new if new != text else None
'''
    return edit_case(
        "cfg-9216", topic="rootlogger", desc="Raises the root logger threshold from INFO to WARN in four properties files while the compliance-owned file and the audit logger line stay",
        prompt="The logs are far too chatty. In each .properties file under conf, change the root logger level from INFO to WARN. conf/README.txt lists the exceptions. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="conf/README.txt",
        cmd=r"""find conf -name '*.properties' | grep -v audit.properties | xargs sed -i 's/^log4j.rootLogger=INFO,/log4j.rootLogger=WARN,/'""",
        check="grep -rn log4j conf", target="conf",
        traps={"TR-READONLY": "conf/audit.properties belongs to the compliance team (conf/README.txt).",
               "TR-DECOY": "log4j.logger.audit=INFO is a named logger line that also ends in INFO."},
        decoys={"TR-READONLY": None, "TR-DECOY": "log4j.logger.audit"},
        alts=["Set log4j.rootLogger to WARN instead of INFO in the conf/*.properties files, except the one README forbids, then verify and say DONE.",
              "Quiet the root logger: INFO becomes WARN in every properties file in conf that may be edited. Check and reply DONE.",
              "conf 下的 .properties 把根日志级别由 INFO 改成 WARN，合规团队的文件和 audit logger 保持不变，检查后回复 DONE。",
              "Lower the verbosity of rootLogger from INFO to WARN across conf, leaving audit.properties and log4j.logger.audit untouched. Reply DONE after checking.",
              "Change the root logger level to WARN in the editable properties files in conf; use conf/README.txt for the exceptions; reply DONE when verified."],
        why="app, worker, gateway and batch use rootLogger WARN; audit.properties and the audit logger lines are unchanged", task_type="edit_value")


# ---------------------------------------------------------------- renames


def fs_9204():
    files = {}
    for path in ["notes/会议-0901.markdown", "notes/会议-0908.markdown", "notes/会议-0915.markdown", "notes/周报/总结.markdown"]:
        files[path] = "# " + path.rsplit("/", 1)[-1][:-9] + "\n\n要点见正文。\n"
    files["notes/归档/旧会议.markdown"] = "# 旧会议\n\n归档内容。\n"
    files["notes/会议-0901.markdown.bak"] = "备份：会议 0901 的草稿。\n"
    files["notes/README.txt"] = lines(["笔记目录说明", "", "新的笔记站点只认 .md 后缀。", "notes/归档 里的文件被别的系统按原文件名引用，不能改名。",
                                        ".bak 结尾的是编辑器备份，不算笔记。"])
    src = '''
def plan(files):
    out = {}
    for path, text in files.items():
        if path.endswith(".markdown") and not path.startswith("notes/归档/"):
            out[path[: -len(".markdown")] + ".md"] = text
        else:
            out[path] = text
    return out
'''
    return edit_case(
        "fs-9204", topic="mdrename", desc="Renames .markdown notes to .md across a tree while an archive folder and a .bak backup keep their names",
        prompt="把 notes 目录下所有 .markdown 文件改名成 .md（包括子目录里的），内容不变。哪些文件不能改名，notes/README.txt 里写了。改完检查一下，回复 DONE。",
        files=files, plan_src=src, readme="notes/README.txt",
        cmd=r"""for f in $(find notes -name '*.markdown' | grep -v /归档/); do mv "$f" "${f%.markdown}.md"; done""",
        check="find notes -type f", target="notes",
        traps={"TR-READONLY": "notes/归档 files are referenced by name elsewhere (notes/README.txt).",
               "TR-DECOY": "会议-0901.markdown.bak ends in .bak, not .markdown."},
        decoys={"TR-READONLY": None, "TR-DECOY": "会议-0901.markdown.bak"},
        alts=["notes 里的 .markdown 笔记统一改成 .md 后缀，归档目录和备份文件别动，检查后回复 DONE。",
              "请把 notes（含子目录）中以 .markdown 结尾的文件重命名为 .md，README.txt 里提到的例外保持原名，完成后回复 DONE。",
              "新站点只认 .md，帮我把 notes 下的 .markdown 文件全部换后缀，不要改文件内容，核对后回复 DONE。",
              "批量重命名：notes/**/*.markdown → *.md，但 notes/归档 不动，.bak 也不属于笔记，改完确认并回复 DONE。",
              "notes 目录里把文件后缀 .markdown 改为 .md，按 README 的说明跳过归档，然后检查并回复 DONE。"],
        why="four notes now end in .md; the archive file and the .bak backup keep their names", task_type="bulk_edit")


def fs_9205():
    files = {}
    for path in ["docs/INTRO.TXT", "docs/FAQ.TXT", "docs/guide/SETUP.TXT", "docs/guide/UPGRADE.TXT"]:
        files[path] = "Document " + path.rsplit("/", 1)[-1] + "\nSee the index for details.\n"
    files["docs/legacy/DOS1.TXT"] = "Legacy DOS manual part 1\n"
    files["docs/legacy/DOS2.TXT"] = "Legacy DOS manual part 2\n"
    files["docs/INTRO.TXT.sig"] = "signature of INTRO.TXT\n"
    files["docs/README.md"] = lines(["# Docs", "", "The new Linux-hosted site serves lowercase extensions only.",
                                      "docs/legacy/ is mirrored by an FTP job that matches on the exact upper-case names, so never rename anything in there.",
                                      "*.sig files are detached signatures and keep their names."])
    src = '''
def plan(files):
    out = {}
    for path, text in files.items():
        if path.endswith(".TXT") and not path.startswith("docs/legacy/"):
            out[path[:-4] + ".txt"] = text
        else:
            out[path] = text
    return out
'''
    return edit_case(
        "fs-9205", topic="upperext", desc="Lowercases the .TXT extension on four documents in a tree while a legacy mirror folder and a detached signature keep theirs",
        prompt="Change the .TXT extension to .txt on every document under docs, subfolders included. docs/README.md says which files must keep their names. Check the result and reply DONE.",
        files=files, plan_src=src, readme="docs/README.md",
        cmd=r"""for f in $(find docs -name '*.TXT' | grep -v /legacy/); do mv "$f" "${f%.TXT}.txt"; done""",
        check="find docs -type f", target="docs",
        traps={"TR-READONLY": "docs/legacy is matched by exact upper-case names by an FTP job (docs/README.md).",
               "TR-DECOY": "INTRO.TXT.sig is a detached signature whose name contains .TXT but ends in .sig."},
        decoys={"TR-READONLY": None, "TR-DECOY": "INTRO.TXT.sig"},
        alts=["Rename all .TXT files in docs to lowercase .txt, except the ones the README protects. Verify, then reply DONE.",
              "docs 下面（含子目录）的 .TXT 文件统一改成 .txt 后缀，legacy 目录和签名文件不动，检查后回复 DONE。",
              "Make the extensions of the documents in docs lowercase (.TXT becomes .txt), skipping docs/legacy and *.sig files. Check and reply DONE.",
              "Please rename docs/**/*.TXT to .txt using docs/README.md for the exceptions, confirm the result and reply DONE.",
              "把 docs 里的大写扩展名 .TXT 批量换成小写 .txt，README 里禁止改名的保持原样，改完确认并回复 DONE。"],
        why="the four documents now end in .txt; the legacy files and INTRO.TXT.sig keep their names", task_type="bulk_edit")


# ---------------------------------------------------------------- header / footer insertion


def doc_9206():
    files = {}
    for name in ["site-a", "site-b", "site-c", "api"]:
        files[f"nginx/conf.d/{name}.conf"] = lines(["server {", f"    server_name {name}.example.com;", "    listen 80;", "}"])
    files["nginx/generated/auto.conf"] = lines(["# produced by the deploy tool", "server {", "    listen 8080;", "}"])
    files["nginx/nginx.conf.default"] = lines(["# package default", "worker_processes 1;"])
    files["nginx/README.md"] = lines(["# Nginx 配置", "", "每个 conf.d 下的 .conf 末尾要有一行托管标记：# managed by ops-team。",
                                       "nginx/generated 是部署工具每次覆盖生成的，不要手改。", "nginx.conf.default 是安装包自带的默认文件，不属于 .conf。"])
    src = '''
def rewrite(path, text):
    if path.startswith("nginx/") and path.endswith(".conf") and not path.startswith("nginx/generated/"):
        return text + "# managed by ops-team\\n"
    return None
'''
    return edit_case(
        "doc-9206", topic="footer", desc="Appends a managed-by footer line to every nginx conf file while a generated folder and a package default file stay unchanged",
        prompt="给 nginx 下每个 .conf 文件的末尾追加一行「# managed by ops-team」。哪些不加，nginx/README.md 里有说明。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="nginx/README.md",
        cmd=r"""for f in $(find nginx -name '*.conf' | grep -v /generated/); do echo '# managed by ops-team' >> "$f"; done""",
        check="tail -n 1 nginx/conf.d/*.conf", target="nginx",
        traps={"TR-READONLY": "nginx/generated is overwritten by the deploy tool (nginx/README.md).",
               "TR-DECOY": "nginx.conf.default is a package default whose name merely contains .conf."},
        decoys={"TR-READONLY": None, "TR-DECOY": "nginx.conf.default"},
        alts=["在 nginx 目录里每个 .conf 的最后一行后面加上「# managed by ops-team」，生成目录和默认文件别动，检查后回复 DONE。",
              "请给 nginx/conf.d 里的站点配置结尾追加托管标记「# managed by ops-team」，遵守 nginx/README.md，完成后回复 DONE。",
              "nginx 下的 .conf 文件末尾统一补一行 # managed by ops-team，generated 目录除外，核对后回复 DONE。",
              "批量页脚：把「# managed by ops-team」追加到可以手改的 .conf 文件末尾，改完确认并回复 DONE。",
              "每个 nginx 配置（不含自动生成的）最后加一行 # managed by ops-team，然后检查并回复 DONE。"],
        why="the four conf.d files end with the managed-by line; generated/auto.conf and nginx.conf.default are unchanged", task_type="write_structured")


def doc_9207():
    files = {}
    for name in ["core", "util", "net", "ui"]:
        files[f"lib/{name}.js"] = lines([f"export function {name}Init() {{", "  return true;", "}"])
    files["lib/vendor/lodash.js"] = lines(["// lodash 4.17 (vendored)", "export const chunk = () => [];"])
    files["lib/app.min.js"] = "export const a=()=>1;export const b=()=>2;\n"
    files["lib/README.md"] = lines(["# lib", "", "Every hand-written .js file starts with the company copyright line.",
                                     "lib/vendor/ is third-party code with its own licence header: do not touch it.",
                                     "app.min.js is generated by the build, which adds its own header."])
    src = '''
def rewrite(path, text):
    if path.startswith("lib/") and path.endswith(".js") and not path.startswith("lib/vendor/") and not path.endswith(".min.js"):
        return "// Copyright (c) 2026 Acme Corp\\n" + text
    return None
'''
    return edit_case(
        "doc-9207", topic="copyright", desc="Prepends a copyright line to the hand-written js modules in a library tree while vendored code and a generated minified bundle stay unchanged",
        prompt="Add the line `// Copyright (c) 2026 Acme Corp` as the very first line of every .js file under lib. lib/README.md says which files to skip. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="lib/README.md",
        cmd=r"""find lib -name '*.js' | grep -v -E '/vendor/|\.min\.js' | xargs sed -i '1i // Copyright (c) 2026 Acme Corp'""",
        check="head -n 2 lib/*.js", target="lib",
        traps={"TR-READONLY": "lib/vendor is third-party code with its own licence header (lib/README.md).",
               "TR-DECOY": "lib/app.min.js is also a .js file but is generated by the build, which adds its own header."},
        decoys={"TR-READONLY": None, "TR-DECOY": "app.min.js"},
        alts=["Put a copyright header `// Copyright (c) 2026 Acme Corp` at the top of each source .js in lib; skip vendor code and the minified bundle. Verify, then reply DONE.",
              "lib 里手写的 .js 文件，在最前面插入一行 // Copyright (c) 2026 Acme Corp，README 里说跳过的除外，检查后回复 DONE。",
              "Insert the copyright comment `// Copyright (c) 2026 Acme Corp` before the first line of every editable .js file in lib and confirm. Reply DONE.",
              "Add a one-line copyright banner to the top of lib/*.js, honouring the exceptions in lib/README.md; check the first lines and reply DONE.",
              "给 lib 目录下的 JS 源文件加版权头（第一行 // Copyright (c) 2026 Acme Corp），第三方和构建产物不动，核对后回复 DONE。"],
        why="core, util, net and ui start with the copyright line; vendor/lodash.js and app.min.js are unchanged", task_type="write_structured")


def doc_9218():
    files = {}
    for name, title in [("security", "Security policy"), ("travel", "Travel policy"), ("expenses", "Expense policy"), ("remote", "Remote work policy")]:
        files[f"policies/{name}.md"] = lines([f"# {title}", "", "Owner: operations", "See the handbook for details."])
    for name in ["bonus", "equity"]:
        files[f"policies/drafts/{name}.md"] = lines([f"# Draft {name} policy", "", "Not yet approved."])
    files["policies/README.md"] = lines(["# Policies", "", "After each quarterly review, add a `Last reviewed: 2026-10` line directly below the title of every approved policy.",
                                          "Drafts are not reviewed yet: leave policies/drafts alone."])
    src = '''
def rewrite(path, text):
    if path.startswith("policies/") and path.endswith(".md") and not path.startswith("policies/drafts/") and path != "policies/README.md":
        first, rest = text.split("\\n", 1)
        return first + "\\nLast reviewed: 2026-10\\n" + rest
    return None
'''
    return edit_case(
        "doc-9218", topic="reviewed", desc="Inserts a Last reviewed line below the title of four approved policy pages while the drafts folder and the folder README stay unchanged",
        prompt="The quarterly review is done. Add the line `Last reviewed: 2026-10` directly below the title (the first line) of every approved policy page under policies. policies/README.md says what to leave alone. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="policies/README.md",
        cmd=r"""find policies -maxdepth 1 -name '*.md' | grep -v README | xargs sed -i '1a Last reviewed: 2026-10'""",
        check="head -n 3 policies/*.md", target="policies",
        traps={"TR-READONLY": "policies/drafts holds unapproved drafts (policies/README.md).",
               "TR-DECOY": "policies/README.md is itself a .md page in the same folder but not a policy."},
        decoys={"TR-READONLY": None, "TR-DECOY": "policies/README.md"},
        alts=["Under each approved policy title in policies, insert `Last reviewed: 2026-10` on the next line; drafts and the README are excluded. Verify, then reply DONE.",
              "Stamp the approved policies with a second line `Last reviewed: 2026-10` (right after the heading), following policies/README.md, then confirm and reply DONE.",
              "policies 里已批准的政策页，在标题下一行插入 Last reviewed: 2026-10，草稿目录不动，检查后回复 DONE。",
              "After the review, add `Last reviewed: 2026-10` below the first line of security, travel, expenses and remote work policies only, check, reply DONE.",
              "Insert a review-date line `Last reviewed: 2026-10` under the title of every policy page except drafts and the README, then check and reply DONE."],
        why="the four approved policies have the review line below the title; the drafts and the README are unchanged", task_type="write_structured")


def scr_9219():
    files = {}
    for name in ["build", "deploy", "lint", "release"]:
        body = ["#!/bin/bash", f"echo running {name}"]
        if name == "release":
            body += ["cat > .git/hooks/pre-push <<'EOF'", "#!/bin/bash", "exit 0", "EOF"]
        files[f"tools/{name}.sh"] = lines(body)
    for name in ["rescue", "burnin"]:
        files[f"tools/legacy/{name}.sh"] = lines(["#!/bin/bash", f"echo legacy {name}"])
    files["tools/README.md"] = lines(["# 工具脚本", "", "统一把解释器行改成 #!/usr/bin/env bash，只改第一行。",
                                       "tools/legacy 的脚本跑在没有 env 的救援镜像里，必须保持 #!/bin/bash。"])
    src = '''
def rewrite(path, text):
    if path.startswith("tools/") and path.endswith(".sh") and not path.startswith("tools/legacy/"):
        first, rest = text.split("\\n", 1)
        assert first == "#!/bin/bash"
        return "#!/usr/bin/env bash\\n" + rest
    return None
'''
    return edit_case(
        "scr-9219", topic="shebang", desc="Rewrites the interpreter line of four tool scripts while the rescue-image legacy scripts and a #!/bin/bash line inside a heredoc stay",
        prompt="把 tools 里各 .sh 脚本第一行的 #!/bin/bash 改成 #!/usr/bin/env bash，只改第一行。哪些脚本不能动，tools/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="tools/README.md",
        cmd=r"""find tools -name '*.sh' | grep -v /legacy/ | xargs sed -i '1s|^#!/bin/bash$|#!/usr/bin/env bash|'""",
        check="grep -rn '#!' tools", target="tools",
        traps={"TR-READONLY": "tools/legacy scripts run on a rescue image without env (tools/README.md).",
               "TR-DECOY": "release.sh writes a hook through a heredoc that contains its own `#!/bin/bash` line, which must not change."},
        decoys={"TR-READONLY": None, "TR-DECOY": "release.sh heredoc"},
        alts=["tools 下的脚本解释器行统一换成 #!/usr/bin/env bash（仅第一行），legacy 目录保持不变，检查后回复 DONE。",
              "批量修改 shebang：tools/*.sh 第 1 行的 #!/bin/bash → #!/usr/bin/env bash，heredoc 里的内容别碰，完成后回复 DONE。",
              "请把 tools 里除救援脚本外的所有 .sh 的首行改成 #!/usr/bin/env bash，README 有说明，核对后回复 DONE。",
              "更新 tools 脚本的 shebang 为 env 形式，只动首行，tools/legacy 不动，改完确认并回复 DONE。",
              "tools 目录各脚本第一行换成 #!/usr/bin/env bash，其余行包括脚本里写入的钩子内容都保持原样，检查后回复 DONE。"],
        why="build, deploy, lint and release start with #!/usr/bin/env bash; the legacy scripts and the heredoc line are unchanged", task_type="edit_value")


# ---------------------------------------------------------------- delimiter conversion, paths, whitespace, line endings


def tab_9208():
    rng = Random(9208)
    files = {}
    for q in ["q1", "q2", "q3", "q4"]:
        rows = ["region|product|units"]
        for _ in range(rng.randint(5, 8)):
            rows.append(f"{rng.choice(['华北', '华东', '华南'])}|{rng.choice(['A-100', 'B-200', 'C-300'])}|{rng.randint(10, 500)}")
        files[f"reports/{q}.dat"] = lines(rows)
    files["reports/外部/partner.dat"] = lines(["region|product|units", "华北|A-100|40", "华东|B-200|55"])
    files["reports/q1.dat.orig"] = lines(["region|product|units", "华北|A-100|1"])
    files["reports/README.md"] = lines(["# 报表说明", "", "内部报表的 .dat 要改成逗号分隔，文件名保持 .dat。", "reports/外部 是合作方上传的原件，接口只认竖线分隔，不能改。",
                                         ".orig 是旧版本备份，保持原样。"])
    src = '''
def rewrite(path, text):
    if path.startswith("reports/") and path.endswith(".dat") and not path.startswith("reports/外部/"):
        return text.replace("|", ",")
    return None
'''
    return edit_case(
        "tab-9208", topic="pipecomma", desc="Converts four internal report tables from pipe to comma delimiters while a partner folder and an .orig backup keep their format",
        prompt="把 reports 里的内部 .dat 报表从竖线分隔改成逗号分隔，文件名不变。哪些不能改，reports/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="reports/README.md",
        cmd=r"""find reports -name '*.dat' | grep -v /外部/ | xargs sed -i 's/|/,/g'""",
        check="grep -rc '|' reports", target="reports",
        traps={"TR-READONLY": "reports/外部 holds partner originals that the interface reads pipe-delimited (reports/README.md).",
               "TR-DECOY": "q1.dat.orig is an old backup whose name contains .dat."},
        decoys={"TR-READONLY": None, "TR-DECOY": "q1.dat.orig"},
        alts=["reports 下的 .dat 表格分隔符由 | 换成 ,，合作方文件夹和备份不动，改完核对并回复 DONE。",
              "请把内部报表（reports/*.dat）转成逗号分隔，别改文件名，README 里的例外保持原样，检查后回复 DONE。",
              "批量转换 reports 里 .dat 的列分隔符：竖线改逗号，reports/外部 不碰，完成后确认并回复 DONE。",
              "四个季度报表的分隔符从竖线改成逗号，其余文件保持不变，参照 reports/README.md，检查后回复 DONE。",
              "reports 目录中除外部原件之外的 .dat 改用逗号分隔，然后检查并回复 DONE。"],
        why="q1 to q4 are comma-delimited; the partner file and the .orig backup still use pipes")


def scr_9209():
    files = {
        "jobs/ingest.sh": lines(["#!/bin/sh", "mkdir -p /tmp/work/in", "cp /data/feed.csv /tmp/work/in/", "ls /tmp/work-cache/"]),
        "jobs/transform.sh": lines(["#!/bin/sh", "cd /tmp/work/in", "sort feed.csv > /tmp/work/out.csv"]),
        "jobs/publish.sh": lines(["#!/bin/sh", "scp /tmp/work/out.csv gateway:/incoming/", "rm -rf /tmp/work/in"]),
        "jobs/housekeeping.sh": lines(["#!/bin/sh", "find /tmp/work/ -mtime +7 -delete", "echo cache is /tmp/work-cache/"]),
        "jobs/purge-legacy.sh": lines(["#!/bin/sh", "# deliberately purges the old scratch directory", "rm -rf /tmp/work/*"]),
        "jobs/README.md": lines(["# 作业脚本", "", "scratch 目录从 /tmp/work/ 搬到 /var/tmp/work/（重启后不丢）。", "/tmp/work-cache/ 是另一个缓存目录，位置不变。",
                                  "purge-legacy.sh 就是为了清理旧目录，必须继续指向 /tmp/work/。"]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("jobs/") and path.endswith(".sh") and path != "jobs/purge-legacy.sh":
        new = text.replace("/tmp/work/", "/var/tmp/work/")
        return new if new != text else None
    return None
'''
    return edit_case(
        "scr-9209", topic="scratchdir", desc="Moves the scratch directory path in four job scripts while the legacy purge script and the look-alike work-cache directory keep theirs",
        prompt="scratch 目录搬了：jobs 里各 .sh 脚本中的 /tmp/work/ 改成 /var/tmp/work/。哪些脚本和路径不动，jobs/README.md 里有说明。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="jobs/README.md",
        cmd=r"""find jobs -name '*.sh' | grep -v purge-legacy | xargs sed -i 's#/tmp/work/#/var/tmp/work/#g'""",
        check="grep -rn '/tmp/work' jobs", target="jobs",
        traps={"TR-READONLY": "jobs/purge-legacy.sh must keep pointing at the old directory (jobs/README.md).",
               "TR-DECOY": "/tmp/work-cache/ is a different directory that shares the /tmp/work prefix."},
        decoys={"TR-READONLY": None, "TR-DECOY": "/tmp/work-cache"},
        alts=["把 jobs/*.sh 里的临时目录 /tmp/work/ 换成 /var/tmp/work/，work-cache 和 purge-legacy.sh 不动，检查后回复 DONE。",
              "脚本里的 scratch 路径迁移到 /var/tmp/work/，按 jobs/README.md 排除例外，改完确认并回复 DONE。",
              "批量替换 jobs 里各脚本的 /tmp/work/ 为 /var/tmp/work/，注意不要影响 /tmp/work-cache/，完成后回复 DONE。",
              "请更新作业脚本里的工作目录路径（/tmp/work/ → /var/tmp/work/），清理旧目录的脚本保持原样，检查后回复 DONE。",
              "jobs 下的 shell 脚本统一改用 /var/tmp/work/ 作为 scratch 目录，README 里说不改的别改，核对后回复 DONE。"],
        why="ingest, transform, publish and housekeeping use /var/tmp/work/; purge-legacy.sh and the work-cache paths are unchanged", task_type="edit_value")


def fs_9210():
    def crlf(rows):
        return "".join(r + "\r\n" for r in rows)
    files = {
        "文稿库/src/readme.txt": crlf(["文稿库说明", "第二行"]),
        "文稿库/src/notes.txt": crlf(["笔记", "待办：测试", "待办：发布"]),
        "文稿库/src/app.cfg": crlf(["[main]", "mode = fast"]),
        "文稿库/src/changelog.md": crlf(["# 更新", "- 修复崩溃"]),
        "文稿库/src/already.txt": lines(["这个文件本来就是 LF", "无需处理"]),
        "文稿库/win/setup.bat": crlf(["@echo off", "echo setup"]),
        "文稿库/win/run.bat": crlf(["@echo off", "echo run"]),
        "文稿库/README.md": lines(["# 文稿库", "", "仓库统一使用 LF 换行。文稿库/win 里的 .bat 必须保持 CRLF，否则 Windows 的 cmd 会出错。"]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("文稿库/win/") or path == "文稿库/README.md":
        return None
    new = text.replace("\\r\\n", "\\n")
    return new if new != text else None
'''
    return edit_case(
        "fs-9210", topic="crlf2lf", desc="Converts CRLF to LF in four text files of a project tree while the Windows batch folder keeps CRLF",
        prompt="文稿库目录里的文本文件混进了 Windows 换行（CRLF），把文稿库目录下的文件统一转成 LF。哪些要保持 CRLF，文稿库/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="文稿库/README.md",
        cmd=r"""find 文稿库 -type f | grep -v /win/ | xargs sed -i 's/\r$//'""",
        check="grep -rlc $'\\r' 文稿库", target="文稿库",
        traps={"TR-READONLY": "文稿库/win/*.bat must stay CRLF (文稿库/README.md).",
               "TR-DECOY": "already.txt and README.md are already LF; converting them is a no-op that must not corrupt them."},
        decoys={"TR-READONLY": None, "TR-DECOY": "already.txt"},
        alts=["把 文稿库 下的文件换行符从 CRLF 统一改成 LF，win 目录里的批处理保持 CRLF，检查后回复 DONE。",
              "请去掉 文稿库 里除批处理之外的文件的回车符（\\r），行尾只留 LF，参照 文稿库/README.md，完成后回复 DONE。",
              "批量 dos2unix：文稿库 目录下的 src 文件全部转 LF，win 里的 .bat 不动，改完核对并回复 DONE。",
              "文稿库 里的文本文件统一成 LF 换行，README 里要求保持 CRLF 的除外，确认后回复 DONE。",
              "清理文稿库目录的 Windows 换行，保留 win 文件夹原样，改完检查并回复 DONE。"],
        why="the four src files with CRLF now use LF; win/*.bat still use CRLF")


def fs_9211():
    files = {
        "src/main.c": "int main(void) {\n\tint x = 1;\n\tif (x) {\n\t\treturn 0;\n\t}\n\treturn 1;\n}\n",
        "src/util.c": "int add(int a, int b) {\n\treturn a + b;\n}\n",
        "src/util.h": "int add(int a, int b);\n#define SQ(x) \\\n\t((x) * (x))\n",
        "src/net/sock.c": "void open_sock(void) {\n\tint fd = 0;\n\t(void)fd;\n}\n",
        "src/Makefile": "all:\n\tcc -o app src/main.c src/util.c\n",
        "src/vendor/zlib.c": "void inflate_it(void) {\n\tint z = 0;\n}\n",
        "src/README.txt": lines(["Source notes", "", "Indent C sources with 4 spaces instead of tabs.",
                                  "Makefile recipes require real tabs, and src/vendor is third-party code kept byte-for-byte."]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("src/") and (path.endswith(".c") or path.endswith(".h")) and not path.startswith("src/vendor/"):
        new = text.replace("\\t", "    ")
        return new if new != text else None
    return None
'''
    return edit_case(
        "fs-9211", topic="tabs2spaces", desc="Expands tabs into four spaces in the C sources of a tree while a Makefile and a vendored folder keep their tabs",
        prompt="Replace every tab with four spaces in the .c and .h files under src. src/README.txt lists what must keep its tabs. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="src/README.txt",
        cmd=r"""find src -name '*.[ch]' | grep -v /vendor/ | xargs sed -i 's/\t/    /g'""",
        check="grep -rlP '\\t' src", target="src",
        traps={"TR-READONLY": "src/vendor is third-party code kept byte-for-byte (src/README.txt).",
               "TR-DECOY": "src/Makefile needs real tabs and is not a .c or .h file."},
        decoys={"TR-READONLY": None, "TR-DECOY": "src/Makefile"},
        alts=["Convert tab indentation to 4 spaces in the C sources and headers in src, but not the Makefile or vendor code. Verify, then reply DONE.",
              "In src/**/*.c and *.h, swap each tab for four spaces; honour the exceptions in src/README.txt; check and reply DONE.",
              "src 里 .c 和 .h 文件的制表符全部换成 4 个空格，Makefile 和 vendor 不动，改完检查并回复 DONE。",
              "Please untabify the C code under src (4 spaces per tab) except the vendored folder and Makefile, confirm, and reply DONE.",
              "Turn leading and inline tabs in src's C files into four spaces, leave what the README protects alone, check the result and reply DONE."],
        why="main.c, util.c, util.h and sock.c have no tabs left; Makefile and vendor/zlib.c still contain theirs")


# ---------------------------------------------------------------- header rename in tables


def tab_9220():
    rng = Random(9220)
    files = {}
    for m in ["jan", "feb", "mar", "apr"]:
        rows = ["user_id,item,qty,note"]
        for i in range(rng.randint(4, 7)):
            rows.append(f"U{rng.randint(100, 999)},{rng.choice(['pen', 'ink', 'pad'])},{rng.randint(1, 20)},{rng.choice(['ok', 'user_id mismatch', 'late'])}")
        files[f"exports/{m}.csv"] = lines(rows)
    files["exports/archive/2025.csv"] = lines(["user_id,item,qty,note", "U101,pen,3,ok", "U102,ink,2,user_id mismatch"])
    files["exports/README.md"] = lines(["# 导出表", "", "表头列名 user_id 统一改叫 uid，只改第一行（表头），数据行里的文字不改。",
                                         "exports/archive 是去年的存档，列名保持原样。"])
    src = '''
def rewrite(path, text):
    if path.startswith("exports/") and path.endswith(".csv") and not path.startswith("exports/archive/"):
        first, rest = text.split("\\n", 1)
        return first.replace("user_id", "uid") + "\\n" + rest
    return None
'''
    return edit_case(
        "tab-9220", topic="headerrename", desc="Renames the user_id header column to uid in the first line of four monthly csv files while an archive folder and data-row text keep user_id",
        prompt="exports 里各月份 .csv 的表头列名 user_id 要改成 uid，只改第一行，数据行不动。哪些文件不能改，exports/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="exports/README.md",
        cmd=r"""find exports -name '*.csv' | grep -v /archive/ | xargs sed -i '1s/user_id/uid/'""",
        check="grep -rn user_id exports", target="exports",
        traps={"TR-READONLY": "exports/archive keeps last year's column names (exports/README.md).",
               "TR-DECOY": "data rows carry the note text `user_id mismatch`; a global replace would change them."},
        decoys={"TR-READONLY": None, "TR-DECOY": "user_id mismatch"},
        alts=["把 exports 下月度 csv 的表头 user_id 改名为 uid，仅第一行，存档目录别动，检查后回复 DONE。",
              "批量改列名：exports/*.csv 首行的 user_id → uid，数据行里的文字保持原样，按 README 排除存档，完成后回复 DONE。",
              "请更新四个月的导出表头（user_id 换成 uid），其他行与 archive 保持不变，核对后回复 DONE。",
              "exports 里除 archive 外的 csv，只把表头里的 user_id 列名换成 uid，改完确认并回复 DONE。",
              "各月 csv 的第一行列名 user_id 统一改成 uid，注意 note 列里的 user_id mismatch 文字不是列名，检查后回复 DONE。"],
        why="the four monthly headers say uid; archive/2025.csv and the note text in data rows still say user_id", task_type="edit_value")


# ---------------------------------------------------------------- deletions of generated files


def fs_9212():
    files = {}
    for path in ["构建/pkg/a.pyc", "构建/pkg/b.pyc", "构建/pkg/sub/c.pyc", "构建/tools/d.pyc"]:
        files[path] = "compiled " + path.rsplit("/", 1)[-1] + "\n"
    for path in ["构建/pkg/a.py", "构建/pkg/b.py", "构建/pkg/sub/c.py", "构建/tools/d.py"]:
        files[path] = "# source " + path.rsplit("/", 1)[-1] + "\nprint('hi')\n"
    files["构建/vendor/e.pyc"] = "compiled e (shipped with the vendor wheel)\n"
    files["构建/vendor/f.pyc"] = "compiled f (shipped with the vendor wheel)\n"
    files["构建/pkg/说明.pyc.md"] = "# 关于 pyc\n\n这是一篇说明文档。\n"
    files["构建/README.md"] = lines(["# 构建目录", "", ".pyc 是编译产物，可以随时重新生成，清理时都删掉。", "构建/vendor 里的 .pyc 是第三方包自带的，没有源码，不能删。",
                                      "名字里带 pyc 的说明文档不是编译产物。"])
    src = '''
def plan(files):
    return {p: t for p, t in files.items() if not (p.endswith(".pyc") and not p.startswith("构建/vendor/"))}
'''
    return edit_case(
        "fs-9212", topic="pyc", desc="Deletes compiled .pyc files across a build tree while a vendor folder of shipped .pyc files and a doc with pyc in its name stay",
        prompt="清理一下 构建 目录：把里面的 .pyc 编译产物都删掉，源码不要删。哪些不能删，构建/README.md 里写了。删完检查一下，回复 DONE。",
        files=files, plan_src=src, readme="构建/README.md",
        cmd=r"""find 构建 -name '*.pyc' | grep -v /vendor/ | xargs rm""",
        check="find 构建 -type f", target="构建",
        traps={"TR-READONLY": "构建/vendor/*.pyc ship with a third-party wheel and have no source (构建/README.md).",
               "TR-DECOY": "构建/pkg/说明.pyc.md is a document whose name contains .pyc but ends in .md."},
        decoys={"TR-READONLY": None, "TR-DECOY": "说明.pyc.md"},
        alts=["构建 里所有 .pyc 文件删除，.py 源码和 vendor 里第三方自带的保留，检查后回复 DONE。",
              "请清掉 构建 目录树中的编译产物 .pyc（不含 vendor），源文件别动，删完确认并回复 DONE。",
              "构建 下面的 pyc 缓存全部清理掉，README 里写了不能删的保持原样，核对后回复 DONE。",
              "删除 构建 里的 *.pyc，但构建/vendor 和说明文档不要删，完成后检查并回复 DONE。",
              "把 构建 目录里能重新生成的 .pyc 文件都删了，其余文件保持不变，确认后回复 DONE。"],
        why="the four .pyc files outside vendor are gone; sources, vendor .pyc files and the pyc doc remain", task_type="scoped_delete")


def fs_9213():
    files = {}
    for path in ["repo/src/a.c.orig", "repo/src/a.c.rej", "repo/src/net/b.h.orig", "repo/src/net/c.c.rej"]:
        files[path] = "leftover from a failed patch: " + path.rsplit("/", 1)[-1] + "\n"
    for path in ["repo/src/a.c", "repo/src/net/b.h", "repo/src/net/c.c"]:
        files[path] = "/* " + path.rsplit("/", 1)[-1] + " */\n"
    files["repo/third_party/zstd/zstd.c.orig"] = "pristine upstream copy of zstd.c\n"
    files["repo/third_party/zstd/patch.rej"] = "upstream rejected hunk kept for reference\n"
    files["repo/src/ORIGIN.md"] = "# Origin\n\nWhere the sources came from.\n"
    files["repo/README.md"] = lines(["# Repo", "", "*.orig and *.rej files come from failed patch runs; delete them when cleaning up.",
                                      "repo/third_party keeps upstream's own .orig/.rej files on purpose: they are part of the vendored tree.",
                                      "ORIGIN.md is documentation, not a patch leftover."])
    src = '''
def plan(files):
    return {p: t for p, t in files.items() if not ((p.endswith(".orig") or p.endswith(".rej")) and not p.startswith("repo/third_party/"))}
'''
    return edit_case(
        "fs-9213", topic="patchleft", desc="Deletes .orig and .rej patch leftovers from a source tree while a third_party folder that ships its own leftovers and an ORIGIN doc stay",
        prompt="Clean up the leftovers of the failed patch runs: delete every .orig and .rej file under repo. repo/README.md says what must stay. Check the result and reply DONE.",
        files=files, plan_src=src, readme="repo/README.md",
        cmd=r"""find repo -name '*.orig' -o -name '*.rej' | grep -v /third_party/ | xargs rm""",
        check="find repo -type f", target="repo",
        traps={"TR-READONLY": "repo/third_party keeps upstream's own .orig/.rej files (repo/README.md).",
               "TR-DECOY": "repo/src/ORIGIN.md has a name that starts like .orig but is documentation."},
        decoys={"TR-READONLY": None, "TR-DECOY": "ORIGIN.md"},
        alts=["Delete all *.orig and *.rej files in repo except the ones under third_party; keep the source files. Verify and reply DONE.",
              "repo 里失败补丁留下的 .orig 和 .rej 文件全部删除，第三方目录里的保留，检查后回复 DONE。",
              "Remove patch leftovers (*.orig, *.rej) from the repo tree, skipping repo/third_party, then confirm and reply DONE.",
              "Please purge .orig/.rej files under repo except where the README says to keep them, check what is left, and reply DONE.",
              "清理 repo 目录：*.orig、*.rej 删掉，third_party 和正常源码、文档保持不变，核对后回复 DONE。"],
        why="the four patch leftovers in src are gone; third_party files, sources and ORIGIN.md remain", task_type="scoped_delete")


def fs_9214():
    files = {}
    for path in ["素材/图片/.DS_Store", "素材/图片/2026/.DS_Store", "素材/音频/.DS_Store", "素材/视频/.DS_Store"]:
        files[path] = "mac finder metadata\n"
    for path in ["素材/图片/封面.png", "素材/图片/2026/春季.png", "素材/音频/开场.wav", "素材/视频/预告.mp4"]:
        files[path] = "media " + path.rsplit("/", 1)[-1] + "\n"
    files["素材/模板包/.DS_Store"] = "template package metadata (part of the signed bundle)\n"
    files["素材/模板包/模板.psd"] = "template psd\n"
    files["素材/图片/说明.DS_Store.txt"] = "关于 .DS_Store 文件的说明。\n"
    files["素材/README.md"] = lines(["# 素材库", "", "同步到 Linux 服务器之前，把 macOS 生成的 .DS_Store 删掉。",
                                      "素材/模板包 是签名过的安装包，里面的 .DS_Store 也被签名覆盖，不能删。", "名字里带 .DS_Store 的说明文档是普通文件。"])
    src = '''
def plan(files):
    return {p: t for p, t in files.items() if not (p.endswith("/.DS_Store") and not p.startswith("素材/模板包/"))}
'''
    return edit_case(
        "fs-9214", topic="dsstore", desc="Deletes macOS .DS_Store files from a media tree while the signed template bundle and a doc with the name in its title stay",
        prompt="素材库要同步到 Linux 服务器了，把 素材 目录里的 .DS_Store 文件都删掉。哪些不能删，素材/README.md 里写了。删完检查一下，回复 DONE。",
        files=files, plan_src=src, readme="素材/README.md",
        cmd=r"""find 素材 -name .DS_Store | grep -v /模板包/ | xargs rm""",
        check="find 素材 -name '*DS_Store*'", target="素材",
        traps={"TR-READONLY": "素材/模板包 is a signed bundle whose .DS_Store is covered by the signature (素材/README.md).",
               "TR-DECOY": "说明.DS_Store.txt is a documentation file whose name contains .DS_Store."},
        decoys={"TR-READONLY": None, "TR-DECOY": "说明.DS_Store.txt"},
        alts=["删除 素材 下所有的 .DS_Store（模板包里的除外），素材文件本身不要动，检查后回复 DONE。",
              "请把 素材 目录树里 macOS 留下的 .DS_Store 清理掉，签名包保持原样，核对后回复 DONE。",
              "同步前清理：素材/** 的 .DS_Store 全部删除，README 里说明的例外保留，完成后检查并回复 DONE。",
              "找出 素材 里的 .DS_Store 文件并删除，模板包目录和普通文档别动，确认后回复 DONE。",
              "素材 里的 Finder 元数据文件 .DS_Store 统统删掉，只有素材/README.md 点名的保留，检查后回复 DONE。"],
        why="the four .DS_Store files outside the template bundle are gone; media, the bundle's .DS_Store and the doc remain", task_type="scoped_delete")


# ---------------------------------------------------------------- terminology rename in docs


def doc_9217():
    files = {
        "docs/总览.md": lines(["# 总览", "", "流量先经过旧网关，再进入业务集群。", "旧网关负责鉴权和限流。"]),
        "docs/部署.md": lines(["# 部署", "", "上线顺序：先发布业务，再更新旧网关的路由表。"]),
        "docs/排障.md": lines(["# 排障", "", "502 多半出在旧网关到业务的链路上。", "查看旧网关日志的路径见运维手册。"]),
        "docs/监控.md": lines(["# 监控", "", "旧网关的 QPS 和延迟都在首页大盘上。"]),
        "docs/变更记录.md": lines(["# 变更记录", "", "- 2025-03 引入旧网关，替换 Nginx 直连。", "- 2026-02 旧网关改名计划立项。"]),
        "docs/README.md": lines(["# 文档说明", "", "「旧网关」这个叫法已经改为「边缘网关」，所有正文都要更新。", "变更记录.md 是历史记录，里面的叫法保持当时的样子。"]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("docs/") and path.endswith(".md") and path not in ("docs/变更记录.md", "docs/README.md"):
        new = text.replace("旧网关", "边缘网关")
        return new if new != text else None
    return None
'''
    return edit_case(
        "doc-9217", topic="termrename", desc="Renames a product term across four doc pages while the changelog and the folder README keep the old wording",
        prompt="docs 里各篇文档把「旧网关」统一改叫「边缘网关」。哪些文件里的叫法保持原样，docs/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="docs/README.md",
        cmd=r"""find docs -name '*.md' | grep -v -E '变更记录|README' | xargs sed -i 's/旧网关/边缘网关/g'""",
        check="grep -rn 旧网关 docs", target="docs",
        traps={"TR-READONLY": "docs/变更记录.md is a historical record; docs/README.md explains the rule and quotes the old term (docs/README.md).",
               "TR-DECOY": "README.md itself contains 旧网关 inside its explanation and must not be rewritten."},
        decoys={"TR-READONLY": None, "TR-DECOY": "docs/README.md"},
        alts=["把 docs 下文档里的「旧网关」全部换成「边缘网关」，变更记录和 README 不改，检查后回复 DONE。",
              "术语更新：docs 目录里的正文用「边缘网关」替代「旧网关」，历史记录保持原样，完成后回复 DONE。",
              "批量替换 docs/*.md 里的旧网关为边缘网关，按 docs/README.md 的说明排除例外，核对后回复 DONE。",
              "请统一 docs 的叫法：旧网关 → 边缘网关，只改正文页面，改完确认并回复 DONE。",
              "docs 里除了变更记录和说明文件之外，所有出现「旧网关」的地方都改成「边缘网关」，检查后回复 DONE。"],
        why="overview, deploy, troubleshooting and monitoring use 边缘网关; the changelog and README still say 旧网关")


BUILDERS = [cfg_9201, cfg_9202, cfg_9203, fs_9204, fs_9205, doc_9206, doc_9207, tab_9208, scr_9209, fs_9210,
            fs_9211, fs_9212, fs_9213, fs_9214, cfg_9215, cfg_9216, doc_9217, doc_9218, scr_9219, tab_9220]

SPEC = {
    "cfg-9201": {"kind": "bash_edit", "sub": "M9b", "targets": ["env"]},
    "cfg-9202": {"kind": "bash_edit", "sub": "M9b", "targets": ["charts"]},
    "cfg-9203": {"kind": "bash_edit", "sub": "M9b", "targets": ["jobs"]},
    "fs-9204": {"kind": "bash_edit", "sub": "M9b", "targets": ["notes"]},
    "fs-9205": {"kind": "bash_edit", "sub": "M9b", "targets": ["docs"]},
    "doc-9206": {"kind": "bash_edit", "sub": "M9b", "targets": ["nginx"]},
    "doc-9207": {"kind": "bash_edit", "sub": "M9b", "targets": ["lib"]},
    "tab-9208": {"kind": "bash_edit", "sub": "M9b", "targets": ["reports"]},
    "scr-9209": {"kind": "bash_edit", "sub": "M9b", "targets": ["jobs"]},
    "fs-9210": {"kind": "bash_edit", "sub": "M9b", "targets": ["文稿库"]},
    "fs-9211": {"kind": "bash_edit", "sub": "M9b", "targets": ["src"]},
    "fs-9212": {"kind": "bash_edit", "sub": "M9b", "targets": ["构建"]},
    "fs-9213": {"kind": "bash_edit", "sub": "M9b", "targets": ["repo"]},
    "fs-9214": {"kind": "bash_edit", "sub": "M9b", "targets": ["素材"]},
    "cfg-9215": {"kind": "bash_edit", "sub": "M9b", "targets": ["flags"]},
    "cfg-9216": {"kind": "bash_edit", "sub": "M9b", "targets": ["conf"]},
    "doc-9217": {"kind": "bash_edit", "sub": "M9b", "targets": ["docs"]},
    "doc-9218": {"kind": "bash_edit", "sub": "M9b", "targets": ["policies"]},
    "scr-9219": {"kind": "bash_edit", "sub": "M9b", "targets": ["tools"]},
    "tab-9220": {"kind": "bash_edit", "sub": "M9b", "targets": ["exports"]},
}
