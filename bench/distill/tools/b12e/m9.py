"""M9 (bash) half of the v1.41 b12e batch: ids 9121-9132, 9139, 9140. All cases have two turns.

M9b two-turn bulk edits (9121-9128): turn 2 changes or reverts part of what turn 1 did, so the final state is not a
plain replace-everywhere (shape of ../b12a/m9.py cfg_9025). Multi-file lookups (9129-9132): turn 1 is a single named
file (read tool), turn 2 needs an aggregate over other files (bash). Mixed (tab-9139, nt-9140)."""
import json
from random import Random

from common import DONE, files_check, has, lines, phrasings, rules_for, thousands, verify_src, write_case

REFS = {}


def edit_case(cid, *, desc, task_type, family, level, files, stages, c1, c2, c3, body, traps, trap_note, reply_notes,
              prompts, alts, axes=("CON",)):
    final = files
    for stage in stages:
        final = stage(final)
    rules = rules_for(files, final)
    notes = f"""## Traps
{trap_note}
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `{c1}`
2. bash: `{c3}`
Turn 2:
1. bash: `{c2}`
2. bash: `{c3}`
Final answers: DONE ({reply_notes}).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.
""" + phrasings(*alts)
    REFS[cid] = (files, [c1, c3, c2, c3], files_check(rules, files))
    return write_case(
        cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=4, traps=traps,
        decoys={t: None for t in traps}, axes=list(axes), files=files, verify=verify_src(files, body), notes=notes,
        case_expect={"files": rules}, turns=[{"prompt": p, "expect": dict(DONE)} for p in prompts])


# ---------------------------------------------------------------- M9b two-turn edits


def cfg_9121():
    rng = Random(9121)
    names = ["网关", "订单", "报表", "搜索", "通知"]
    imgs = {"网关": "gateway", "订单": "orders", "报表": "reports", "搜索": "search", "通知": "notify", "_样例": "sample"}
    files = {}
    for n in names + ["_样例"]:
        files[f"编排/{n}/deploy.yaml"] = lines([f"name: {'样例' if n == '_样例' else n}", "replicas: 2", "minReplicas: 2",
                                              f"image: registry.corp/{imgs[n]}:1.{rng.randint(2, 9)}"])
    files["编排/README.md"] = lines(["# 编排配置", "", "每个服务一个目录；_样例 是新服务的复制模板，保持原样。",
                                   "minReplicas 是保底副本数，大促也不随扩容改动。"])

    def s1(f):
        return {p: (t.replace("\nreplicas: 2\n", "\nreplicas: 4\n") if p.endswith("deploy.yaml") and "/_样例/" not in p else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        out["编排/报表/deploy.yaml"] = f["编排/报表/deploy.yaml"].replace("\nreplicas: 4\n", "\nreplicas: 2\n")
        out["编排/订单/deploy.yaml"] = f["编排/订单/deploy.yaml"].replace("\nreplicas: 4\n", "\nreplicas: 6\n")
        return out

    body = r'''
assert case["files"]["编排/README.md"].startswith("# 编排配置")
assert "minReplicas 是保底副本数" in case["files"]["编排/README.md"]
want = {"网关": 4, "订单": 6, "报表": 2, "搜索": 4, "通知": 4}
out = {}
for n, k in want.items():
    path = "编排/" + n + "/deploy.yaml"
    rows = case["files"][path].splitlines()
    assert rows[0] == "name: " + n and rows[1] == "replicas: 2" and rows[2] == "minReplicas: 2", path
    out[path] = case["files"][path].replace("\nreplicas: 2\n", "\nreplicas: %d\n" % k)
assert case["files"]["编排/_样例/deploy.yaml"].splitlines()[1] == "replicas: 2"
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    c1 = r"""find 编排 -name deploy.yaml | grep -v /_样例/ | xargs sed -i 's/^replicas: 2$/replicas: 4/'"""
    c2 = r"""sed -i 's/^replicas: 4$/replicas: 2/' 编排/报表/deploy.yaml && sed -i 's/^replicas: 4$/replicas: 6/' 编排/订单/deploy.yaml"""
    return edit_case(
        "cfg-9121", desc="Two turns: scales replicas from 2 to 4 in five service manifests without touching the template or minReplicas, then sets one service back to 2 and another to 6",
        task_type="edit_value", family="fam-cfg-b12e-replicas-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rn replicas 编排", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 编排/_样例 is the copy-me template and stays as it is; minReplicas: 2 is a look-alike key the README says never changes (a global `s/2/4/` or `s/replicas: 2/replicas: 4/` would also hit minReplicas).",
        reply_notes="turn 1: five services at replicas 4; turn 2: 报表 back to 2, 订单 at 6, the rest still 4",
        prompts=["大促要扩容：把 编排 下各服务 deploy.yaml 里的 replicas 从 2 改成 4，哪些文件和字段不能动看 编排/README.md。改完回复 DONE。",
                 "报表是离线任务，不用扩，replicas 改回 2；订单要多撑一点，改成 6。其他服务保持现在的样子。改完回复 DONE。"],
        alts=["编排里 replicas 全部翻倍到 4，再把报表恢复、订单加到 6", "给各服务扩容到 4 个副本，然后报表还原成 2、订单调成 6", "replicas 2 改 4（模板和保底副本不动），之后报表改回去、订单设成 6",
              "大促扩容 4 副本，报表不扩，订单 6 副本", "Scale every service to 4 replicas, then put reports back to 2 and orders at 6."])


def fs_9122():
    files = {
        "笔记/工作/周会.txt": "周会要点：排期、风险\n", "笔记/工作/复盘.txt": "复盘：上线延迟两天\n", "笔记/工作/清单.txt.bak": "旧清单备份\n",
        "笔记/生活/食谱.txt": "番茄炒蛋的做法\n", "笔记/生活/书单.txt": "下半年想读的五本书\n",
        "笔记/草稿/想法1.txt": "做一个命令行记账工具\n", "笔记/草稿/想法2.txt": "给家里的路由器写监控\n",
        "笔记/归档/2025年总结.txt": "2025 年总结\n", "笔记/归档/旧项目.txt": "旧项目资料\n",
        "笔记/说明.md": lines(["# 笔记说明", "", "整理时把 .txt 统一成 .md。", "归档 里的文件名被别的程序按原名引用，不要改名。"]),
    }

    def s1(f):
        out = {}
        for p, t in f.items():
            out[p[:-4] + ".md" if p.endswith(".txt") and "/归档/" not in p else p] = t
        return out

    def s2(f):
        return {(p[:-3] + ".txt" if p.startswith("笔记/草稿/") and p.endswith(".md") else p): t for p, t in f.items()}

    body = r'''
assert case["files"]["笔记/说明.md"].startswith("# 笔记说明")
assert "归档 里的文件名被别的程序按原名引用" in case["files"]["笔记/说明.md"]
assert case["files"]["笔记/工作/清单.txt.bak"].startswith("旧清单")
out = {}
for path, text in case["files"].items():
    if path.endswith(".txt") and "/归档/" not in path and "/草稿/" not in path:
        out[path[:-4] + ".md"] = text
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    c1 = r"""for f in $(find 笔记 -name '*.txt' | grep -v /归档/); do mv "$f" "${f%.txt}.md"; done"""
    c2 = r"""for f in 笔记/草稿/*.md; do mv "$f" "${f%.md}.txt"; done"""
    return edit_case(
        "fs-9122", desc="Two turns: renames .txt notes to .md except an archive folder, then renames the drafts folder back to .txt",
        task_type="bulk_edit", family="fam-fs-b12e-notesmd-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="find 笔记 -type f", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 笔记/归档 keeps its names (笔记/说明.md); 清单.txt.bak merely contains .txt in its name; 草稿 is renamed twice in total (to .md, then back).",
        reply_notes="turn 1: .txt -> .md outside 归档; turn 2: 草稿 files are .txt again",
        prompts=["笔记整理：把 笔记 下的 .txt 文件统一改成 .md 扩展名，哪些不能改名看 笔记/说明.md。改完回复 DONE。",
                 "草稿 里的文件其实还要给导入脚本用，脚本只认 .txt，把草稿那几个改回 .txt，别的保持现在的样子。改完回复 DONE。"],
        alts=["笔记里的 txt 全部换成 md（归档除外），然后草稿文件再换回 txt", "把笔记改成 Markdown 扩展名，草稿目录之后恢复成 txt", "统一 .md 后，草稿因为脚本要求改回 .txt",
              "txt 改 md，归档不动；草稿再还原", "Rename the notes from .txt to .md except the archive, then turn the drafts back into .txt."])


def doc_9123():
    def page(title, rows):
        return lines([f"# {title}", ""] + rows)
    files = {
        "手册/安装.md": page("安装", ["先下载客户端安装包，双击运行。", "客户端首次启动会要求登录。", "客户支持电话见首页。"]),
        "手册/使用.md": page("使用", ["在客户端左侧选择项目。", "客户反馈请通过菜单提交。", "客户端支持离线模式。"]),
        "手册/排错.md": page("排错", ["客户端打不开时先清理缓存。", "仍无法解决请联系客户成功团队。"]),
        "手册/法务条款.md": page("法务条款", ["第 3 条：客户端的所有权归公司所有。", "第 7 条：客户不得拆解客户端。"]),
        "手册/术语表.md": page("术语表", ["客户端：用户在本机安装的程序。", "客户：购买服务的单位。"]),
        "手册/README.md": lines(["# 手册说明", "", "统一用语：文档里的「客户端」逐步改称「终端」。", "术语表.md 是定义页，保留原词；README.md 本身不改。"]),
    }
    guides = ["安装", "使用", "排错", "法务条款"]

    def s1(f):
        return {p: (t.replace("客户端", "终端") if p in {f"手册/{g}.md" for g in guides} else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        for g in ("法务条款", "安装"):
            out[f"手册/{g}.md"] = files[f"手册/{g}.md"]
        return out

    body = r'''
assert all("终端" not in t for p, t in case["files"].items() if p != "手册/README.md")
assert case["files"]["手册/README.md"].startswith("# 手册说明")
assert case["files"]["手册/术语表.md"].startswith("# 术语表")
out = {}
for g in ["使用", "排错"]:
    path = "手册/%s.md" % g
    assert "客户端" in case["files"][path]
    out[path] = case["files"][path].replace("客户端", "终端")
assert "客户端" in case["files"]["手册/法务条款.md"]
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    c1 = r"""sed -i 's/客户端/终端/g' 手册/安装.md 手册/使用.md 手册/排错.md 手册/法务条款.md"""
    c2 = r"""sed -i 's/终端/客户端/g' 手册/法务条款.md 手册/安装.md"""
    return edit_case(
        "doc-9123", desc="Two turns: replaces a product term across manual pages except a glossary, then restores the original term in two files",
        task_type="write_structured", family="fam-doc-b12e-termswap-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rn '客户端\\|终端' 手册", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 术语表.md (definition page) and README.md keep the old word; 「客户」 alone (客户支持, 客户反馈, 客户不得) is a different word that `s/客户/终端/` would break.",
        reply_notes="turn 1: 安装/使用/排错/法务条款 say 终端; turn 2: 法务条款 and 安装 say 客户端 again",
        prompts=["产品统一用语：把 手册 下文档里的「客户端」都换成「终端」。哪些文件要保留原词看 手册/README.md。改完回复 DONE。",
                 "法务条款.md 里的「客户端」是合同用语，安装.md 里的是界面上显示的原文，这两份必须保持原词，改回来，其他文件保持现在的样子。改完回复 DONE。"],
        alts=["手册里客户端全改叫终端，法务条款再恢复原词", "统一称呼为终端（术语表除外），之后把法务条款里的改回客户端", "客户端→终端 批量替换，法务条款那份还原",
              "手册用语改成终端；合同用语的法务条款保留客户端", "Rename 客户端 to 终端 across the manual, then put the original word back in the legal terms."])


def cfg_9124():
    envs = ["prod", "qa", "staging", "dev"]
    files = {}
    for e in envs + ["_template"]:
        files[f"envs/{e}/db.env"] = lines(["DB_HOST=db-old.internal", "DB_PORT=5432", "REPLICA_HOST=db-old.internal",
                                          f"DB_NAME=app_{'tpl' if e == '_template' else e}"])
    files["envs/README.md"] = lines(["# Environment files", "", "One directory per environment; _template is copied for new environments and stays as it is.",
                                     "REPLICA_HOST moves next month, leave it on db-old.internal for now."])

    def s1(f):
        return {p: (t.replace("DB_HOST=db-old.internal", "DB_HOST=db-new.internal") if p.endswith("db.env") and "/_template/" not in p else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        out["envs/staging/db.env"] = f["envs/staging/db.env"].replace("DB_HOST=db-new.internal", "DB_HOST=db-old.internal")
        out["envs/dev/db.env"] = f["envs/dev/db.env"].replace("DB_HOST=db-new.internal", "DB_HOST=db-dev.internal")
        return out

    body = r'''
assert case["files"]["envs/README.md"].startswith("# Environment files")
assert "REPLICA_HOST moves next month" in case["files"]["envs/README.md"]
want = {"prod": "db-new.internal", "qa": "db-new.internal", "staging": "db-old.internal", "dev": "db-dev.internal"}
out = {}
for e, host in want.items():
    path = "envs/%s/db.env" % e
    rows = case["files"][path].splitlines()
    assert rows[0] == "DB_HOST=db-old.internal" and rows[2] == "REPLICA_HOST=db-old.internal", path
    out[path] = case["files"][path].replace("DB_HOST=db-old.internal", "DB_HOST=" + host)
assert case["files"]["envs/_template/db.env"].splitlines()[0] == "DB_HOST=db-old.internal"
print(json.dumps({"files": out}))
'''
    c1 = r"""find envs -name db.env | grep -v /_template/ | xargs sed -i 's/^DB_HOST=db-old\.internal$/DB_HOST=db-new.internal/'"""
    c2 = r"""sed -i 's/^DB_HOST=db-new\.internal$/DB_HOST=db-old.internal/' envs/staging/db.env && sed -i 's/^DB_HOST=db-new\.internal$/DB_HOST=db-dev.internal/' envs/dev/db.env"""
    return edit_case(
        "cfg-9124", desc="Two turns: moves DB_HOST to a new database host in four environment files without touching the template or REPLICA_HOST, then puts staging back and points dev at its own host",
        task_type="edit_value", family="fam-cfg-b12e-dbhost-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rn HOST envs", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: envs/_template stays as it is; REPLICA_HOST=db-old.internal is a look-alike line the README says to keep (a global `s/db-old.internal/db-new.internal/` changes it).",
        reply_notes="turn 1: prod, qa, staging, dev on db-new.internal; turn 2: staging back on db-old.internal, dev on db-dev.internal",
        prompts=["The primary database moved. In every environment's db.env under envs, change DB_HOST from db-old.internal to db-new.internal. envs/README.md says what must stay as it is. Reply DONE when finished.",
                 "Staging cannot reach the new host until the firewall change lands, so put staging back on db-old.internal, and point dev at db-dev.internal instead. Leave the other environments as they are now. Reply DONE when finished."],
        alts=["Switch DB_HOST to db-new.internal everywhere except the template, then revert staging and give dev its own host.", "Update the database host in all env files, then staging goes back to the old one and dev gets db-dev.",
              "Migrate DB_HOST (leave REPLICA_HOST), afterwards undo it for staging and use db-dev.internal for dev.", "db-old to db-new in envs, except template; then staging old again and dev db-dev.internal.",
              "把各环境的 DB_HOST 迁到新库，之后 staging 改回旧库、dev 改成 db-dev.internal"])


def fs_9125():
    files = {
        "inbox/q3-sales.csv": "sku,qty\nA1,40\nB2,12\n", "inbox/q3-refunds.csv": "sku,qty\nA1,3\n", "inbox/q3-returns.csv": "sku,qty\nC3,5\nB2,1\n",
        "inbox/q3-stock.csv": "sku,qty\nA1,210\nB2,98\nC3,17\n", "inbox/tmp_scratch.csv": "scratch export\n", "inbox/tmp_probe.csv": "probe export\n",
        "inbox/notes.txt": "remember to ask finance about the refund batch\n",
        "inbox/README.md": lines(["# Inbox", "", "Finished CSV exports move to processed/. Only .csv files move; notes.txt stays.",
                                  "tmp_*.csv are scratch exports from the BI tool: they never go to processed/."]),
        "processed/q2-sales.csv": "sku,qty\nA1,35\n",
    }

    def s1(f):
        out = {}
        for p, t in f.items():
            if p.startswith("inbox/") and p.endswith(".csv") and not p.startswith("inbox/tmp_"):
                out["processed/" + p[6:]] = t
            else:
                out[p] = t
        return out

    def s2(f):
        out = {}
        for p, t in f.items():
            if p in ("processed/q3-sales.csv", "processed/q3-refunds.csv"):
                out["inbox/" + p[10:]] = t
            else:
                out[p] = t
        return out

    body = r'''
assert case["files"]["inbox/README.md"].startswith("# Inbox")
assert "never go to processed/" in case["files"]["inbox/README.md"]
out = {}
for name in ["q3-returns", "q3-stock"]:
    text = case["files"]["inbox/%s.csv" % name]
    assert text.startswith("sku,qty" + chr(10)), name
    out["processed/%s.csv" % name] = text
for name in ["q3-sales", "q3-refunds"]:
    assert case["files"]["inbox/%s.csv" % name].startswith("sku,qty")
assert case["files"]["processed/q2-sales.csv"].startswith("sku,qty")
print(json.dumps({"files": out}))
'''
    c1 = r"""for f in $(ls inbox/*.csv | grep -v /tmp_); do mv "$f" processed/; done"""
    c2 = r"""mv processed/q3-sales.csv processed/q3-refunds.csv inbox/"""
    return edit_case(
        "fs-9125", desc="Two turns: moves finished CSV exports from an inbox to a processed folder except scratch exports, then moves two of them back",
        task_type="bulk_edit", family="fam-fs-b12e-inboxmove-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="ls inbox processed", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: tmp_*.csv scratch exports and notes.txt stay in inbox (inbox/README.md); a `mv inbox/*.csv processed/` moves the scratch files too.",
        reply_notes="turn 1: q3-sales, q3-refunds, q3-returns, q3-stock in processed; turn 2: q3-sales and q3-refunds back in inbox",
        prompts=["Move the finished CSV exports from inbox to processed. inbox/README.md says what stays behind. Reply DONE when finished.",
                 "q3-sales.csv and q3-refunds.csv need another pass, so put those two back in inbox; everything else stays where it is now. Reply DONE when finished."],
        alts=["File the finished exports under processed (not the scratch ones), then bring the sales and refunds files back to inbox.", "Archive the CSVs from inbox into processed per the README, then return q3-sales and q3-refunds.",
              "inbox csv -> processed, except tmp files; afterwards q3-sales.csv and q3-refunds.csv go back.", "Shift completed exports to processed; two of them (sales, refunds) must return to inbox.",
              "把 inbox 里处理完的 csv 挪到 processed，之后再把 q3-sales 和 q3-refunds 挪回来"])


def scr_9126():
    names = ["夜间", "周度", "清理", "校验", "同步"]
    files = {}
    for n in names:
        files[f"脚本/{n}.sh"] = lines(["#!/bin/sh", f"# {n}任务", f"DEST=/mnt/old/backup/{n}", "ARCHIVE=/mnt/old/archive", f'echo "{n} run"'])
    files["脚本/README.md"] = lines(["# 脚本说明", "", "备份盘迁移：DEST 里的 /mnt/old/backup 换成 /mnt/new/backup。",
                                   "/mnt/old/archive 是只读归档挂载，不迁移，ARCHIVE 行保持原样。"])

    def s1(f):
        return {p: (t.replace("/mnt/old/backup", "/mnt/new/backup") if p.endswith(".sh") else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        for n in ("夜间", "周度"):
            out[f"脚本/{n}.sh"] = f[f"脚本/{n}.sh"].replace("/mnt/new/backup", "/mnt/cold/backup")
        return out

    body = r'''
assert case["files"]["脚本/README.md"].startswith("# 脚本说明")
assert "只读归档挂载" in case["files"]["脚本/README.md"]
out = {}
for n in ["夜间", "周度", "清理", "校验", "同步"]:
    path = "脚本/%s.sh" % n
    rows = case["files"][path].splitlines()
    assert rows[0] == "#!/bin/sh" and rows[2] == "DEST=/mnt/old/backup/" + n and rows[3] == "ARCHIVE=/mnt/old/archive", path
    root = "/mnt/cold/backup" if n in ("夜间", "周度") else "/mnt/new/backup"
    out[path] = case["files"][path].replace("/mnt/old/backup", root)
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    c1 = r"""find 脚本 -name '*.sh' | xargs sed -i 's#/mnt/old/backup#/mnt/new/backup#g'"""
    c2 = r"""sed -i 's#/mnt/new/backup#/mnt/cold/backup#' 脚本/夜间.sh 脚本/周度.sh"""
    return edit_case(
        "scr-9126", desc="Two turns: repoints the backup path in five shell scripts without touching the read-only archive path, then sends two scripts to a cold-storage path",
        task_type="fix_output", family="fam-scr-b12e-backuppath-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rn /mnt 脚本", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: ARCHIVE=/mnt/old/archive stays on the old mount (脚本/README.md); a global `s#/mnt/old#/mnt/new#` would move it too.",
        reply_notes="turn 1: five scripts write DEST to /mnt/new/backup; turn 2: 夜间.sh and 周度.sh write to /mnt/cold/backup",
        prompts=["备份盘换了：把 脚本 下各 .sh 里的 /mnt/old/backup 换成 /mnt/new/backup，哪些路径不迁移看 脚本/README.md。改完回复 DONE。",
                 "夜间.sh 和 周度.sh 要写到冷存储，路径改成 /mnt/cold/backup，其余脚本保持现在的样子。改完回复 DONE。"],
        alts=["脚本里备份路径迁到 /mnt/new/backup（归档路径不动），夜间脚本再改到冷存储", "把 DEST 的老盘路径换成新盘，之后夜间脚本用 /mnt/cold/backup", "备份路径统一搬家，夜间和周度任务之后单独指向冷盘",
              "old/backup → new/backup，夜间.sh、周度.sh 再改 cold/backup", "Move the backup path in all scripts to the new disk, then point the nightly one at cold storage."])


def tab_9127():
    rng = Random(9127)
    states = ["待处理", "待处理", "待处理-补录", "已完成"]
    files = {}
    for m in ("07", "08", "09"):
        rows = ["单号,客户,金额,状态"]
        for i in range(14):
            rows.append(f"{m}{i + 1:02d},客户{rng.randint(10, 99)},{rng.randint(100, 9000)}.{rng.randint(0, 9)}0,{states[(i * 3 + int(m)) % 4]}")
        files[f"订单/2026-{m}.csv"] = lines(rows)
    files["订单/模板.csv"] = lines(["单号,客户,金额,状态", "示例,示例客户,0.00,待处理"])
    files["订单/README.md"] = lines(["# 订单表", "", "每月一个 CSV，最后一列是状态。", "模板.csv 是空白导入模板，保持原样。", "「待处理-补录」是另一种状态，不属于「待处理」。"])

    def s1(f):
        return {p: ("".join(r.replace(",待处理", ",已受理") + "\n" if r.endswith(",待处理") else r + "\n" for r in t.splitlines())
                    if p.startswith("订单/2026-") else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        for m in ("08", "09"):
            out[f"订单/2026-{m}.csv"] = files[f"订单/2026-{m}.csv"]
        return out

    body = r'''
assert case["files"]["订单/README.md"].startswith("# 订单表")
assert case["files"]["订单/模板.csv"].splitlines()[1].endswith(",待处理")
out = {}
for m in ["07"]:
    path = "订单/2026-%s.csv" % m
    rows = case["files"][path].splitlines()
    assert rows[0] == "单号,客户,金额,状态" and all(not r.endswith(",已受理") for r in rows), path
    out[path] = "".join((r[:-3] + "已受理" if r.endswith(",待处理") else r) + chr(10) for r in rows)
for m in ["08", "09"]:
    rows = case["files"]["订单/2026-%s.csv" % m].splitlines()
    assert rows[0] == "单号,客户,金额,状态" and any(r.endswith(",待处理") for r in rows)
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    c1 = r"""find 订单 -name '2026-*.csv' | xargs sed -i 's/,待处理$/,已受理/'"""
    c2 = r"""sed -i 's/,已受理$/,待处理/' 订单/2026-08.csv 订单/2026-09.csv"""
    return edit_case(
        "tab-9127", desc="Two turns: marks pending orders as accepted in three monthly CSVs without touching the blank template or the look-alike backfill status, then reverts two months",
        task_type="filter_count", family="fam-tab-b12e-orderstatus-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rc 已受理 订单", body=body, traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 订单/模板.csv stays as it is. TR-DECOY: 「待处理-补录」 shares the prefix with 「待处理」 but is a different status (a substring `s/待处理/已受理/` also rewrites it).",
        reply_notes="turn 1: 七月、八月、九月的待处理订单已受理; turn 2: 八月九月又变回待处理，七月仍是已受理",
        axes=("CON", "OBS"),
        prompts=["把 订单 下各月 CSV 里状态为「待处理」的订单改成「已受理」，哪些不能动看 订单/README.md。改完回复 DONE。",
                 "八月和九月的订单还没对账，状态改回「待处理」，七月保持现在的样子。改完回复 DONE。"],
        alts=["订单表里待处理的全部标成已受理，九月那份再还原", "把各月待处理订单批量改为已受理（模板和补录状态除外），之后九月恢复原状", "待处理→已受理，九月撤销",
              "各月订单状态改成已受理；九月因为没对账改回待处理", "Mark every pending order as accepted in the monthly files, then undo it for September."])


def cfg_9128():
    names = ["web", "mobile", "admin", "billing", "payments", "search"]
    files = {}
    for n in names:
        files[f"features/{n}.toml"] = lines(["[flags]", "new_ui = false", "new_ui_v2 = false", "beta_search = false"])
    files["features/frozen/legacy.toml"] = lines(["[flags]", "new_ui = false", "new_ui_v2 = false", "beta_search = false"])
    files["features/README.md"] = lines(["# Feature flags", "", "One TOML file per service; features/frozen/ is the legacy snapshot and is never edited.",
                                         "new_ui_v2 is an experiment owned by the design team: do not flip it."])

    def s1(f):
        return {p: (t.replace("\nnew_ui = false\n", "\nnew_ui = true\n") if p.endswith(".toml") and "/frozen/" not in p else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        for n in ("billing", "payments"):
            out[f"features/{n}.toml"] = f[f"features/{n}.toml"].replace("\nnew_ui = true\n", "\nnew_ui = false\n")
        out["features/search.toml"] = f["features/search.toml"].replace("\nbeta_search = false\n", "\nbeta_search = true\n")
        return out

    body = r'''
assert case["files"]["features/README.md"].startswith("# Feature flags")
assert "new_ui_v2 is an experiment" in case["files"]["features/README.md"]
out = {}
for n in ["web", "mobile", "admin", "billing", "payments", "search"]:
    path = "features/%s.toml" % n
    rows = case["files"][path].splitlines()
    assert rows == ["[flags]", "new_ui = false", "new_ui_v2 = false", "beta_search = false"], path
    on = n not in ("billing", "payments")
    rows[1] = "new_ui = true" if on else "new_ui = false"
    if n == "search":
        rows[3] = "beta_search = true"
    out[path] = chr(10).join(rows) + chr(10)
assert case["files"]["features/frozen/legacy.toml"].splitlines()[1] == "new_ui = false"
print(json.dumps({"files": out}))
'''
    c1 = r"""find features -name '*.toml' | grep -v /frozen/ | xargs sed -i 's/^new_ui = false$/new_ui = true/'"""
    c2 = r"""sed -i 's/^new_ui = true$/new_ui = false/' features/billing.toml features/payments.toml && sed -i 's/^beta_search = false$/beta_search = true/' features/search.toml"""
    return edit_case(
        "cfg-9128", desc="Two turns: turns on a UI flag in six service TOML files while a frozen snapshot and a look-alike v2 flag stay, then switches it off for two services and turns on another flag for one",
        task_type="edit_value", family="fam-cfg-b12e-uiflag-01", level="L3", files=files, stages=[s1, s2], c1=c1, c2=c2,
        c3="grep -rn '_ui\\|beta' features", body=body, traps=["TR-READONLY"],
        trap_note="- TR-READONLY: features/frozen is never edited and new_ui_v2 must not flip (a `s/= false/= true/` would flip every flag).",
        reply_notes="turn 1: new_ui = true in the six services; turn 2: billing and payments back to false, search has beta_search = true",
        prompts=["Turn on the new_ui flag (set it to true) in every service's TOML under features. features/README.md says what must not change. Reply DONE when finished.",
                 "Compliance wants billing and payments back on the old UI, so set new_ui to false in those two files, and search also needs beta_search = true. Leave every other file as it is now. Reply DONE when finished."],
        alts=["Enable new_ui across the services (not the frozen snapshot), then disable it for billing and payments and enable beta_search for search.", "Flip new_ui to true in all feature files, afterwards revert billing and payments and switch on beta_search in search.",
              "new_ui = true everywhere except frozen; then billing and payments false again, search gets beta_search.", "Roll out the new UI flag to every service, then pull it back for the two finance services and give search the beta flag.",
              "把 features 里各服务的 new_ui 打开，之后 billing 和 payments 关回去，search 再开 beta_search"])


# ---------------------------------------------------------------- multi-file lookups (read tool, then bash)


def lookup_case(cid, *, desc, task_type, family, level, files, body, c, want, traps, decoys, trap_note, ref1, ref2, prompts, expects, alts, axes=("OBS", "CHN")):
    notes = f"""## Traps
{trap_note}

## Reference solution
Turn 1: {ref1}
Turn 2:
1. bash: `{c}`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, read_file is the direct read. Turn 2 spans many files, where one pipeline beats opening them one by one.
""" + phrasings(*alts)
    REFS[cid] = (files, [c], has(*want))
    return write_case(
        cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=2, traps=traps, decoys=decoys, axes=list(axes),
        files=files, verify=verify_src(files, body), notes=notes,
        turns=[{"prompt": p, "expect": e} for p, e in zip(prompts, expects)])


def doc_9129():
    rng = Random(9129)
    projects = ["门户改版", "支付升级", "数据迁移", "移动端重构", "监控接入", "风控模型", "客服机器人", "会员体系", "搜索优化", "报表平台"]
    states = ["正常", "正常", "延期", "延期风险", "已完成"]
    files = {"值班/本周.md": lines(["# 本周值班", "", "- 周一：赵雷", "- 周二：钱宁", "- 周三：孙岩", "- 周四：李想", "- 周五：周楠"])}
    total = loose = 0
    for w in range(1, 19):
        rows = [f"# 第 {w} 周周报", ""]
        for p in rng.sample(projects, 8):
            s = rng.choice(states)
            total += s == "延期"
            loose += s.startswith("延期")
            rows.append(f"- 项目：{p} | 状态：{s}")
        files[f"周报/2026-W{w:02d}.md"] = lines(rows)
    files["周报/README.md"] = lines(["# 周报说明", "", "每周一个文件，每行一个项目：「项目：名称 | 状态：取值」。", "状态取值：正常、延期、延期风险、已完成。「延期风险」只是预警，不算延期。"])
    body = r'''
assert case["files"]["值班/本周.md"].splitlines()[4] == "- 周三：孙岩"
assert case["files"]["周报/README.md"].startswith("# 周报说明")
n = 0
for path, text in case["files"].items():
    if path.startswith("周报/2026-W"):
        n += sum(1 for r in text.splitlines() if r.endswith("| 状态：延期"))
print(json.dumps({"expected_number": n}))
'''
    cmd = "cat 周报/*.md | grep -c '状态：延期$'"
    return lookup_case(
        "doc-9129", desc="Two turns: a duty roster lookup from one named file, then counting delayed project lines across eighteen weekly reports with a look-alike status",
        task_type="extract_items", family="fam-doc-b12e-weeklydelay-01", level="L3", files=files, body=body, c=cmd, want=[str(total)],
        traps=["TR-DECOY"], decoys={"TR-DECOY": str(loose)},
        trap_note="- TR-DECOY: 「延期风险」 lines contain 延期 but are only warnings (周报/README.md); 18 weekly files, one file is not enough.",
        ref1="read_file 值班/本周.md -> 孙岩 is on duty on Wednesday.",
        ref2=None,
        prompts=["值班/本周.md 里周三是谁值班？", "周报目录下各周的周报里，状态为延期的项目行一共有多少条？"],
        expects=[{"output_contains": ["孙岩"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains": [str(total)], "max_output_chars": 600}],
        alts=["周报里「延期」状态的项目一共出现几次", "所有周报中状态是延期（不含延期风险）的行有多少", "统计各周报里延期项目的总条数", "18 周周报里延期的项目共多少个", "How many project lines marked 延期 are in all the weekly reports?"])


def tab_9130():
    for seed in range(300):
        rng = Random(9130 + seed * 7919)
        regions = ["华东", "华东二区", "华北", "华南", "西南"]
        files, total, loose = {}, 0, 0
        for m in range(1, 13):
            rows = ["区域,品类,销售额"]
            for _ in range(rng.randint(35, 60)):
                r, v = rng.choice(regions), rng.randint(200, 9000)
                rows.append(f"{r},{rng.choice(['饮料', '零食', '日用'])},{v}")
                total += (r == "华东") * v
                loose += r.startswith("华东") * v
            files[f"明细/2026-{m:02d}.csv"] = lines(rows)
        aug = rng.randint(30000, 90000)
        files["汇总/2026-08.txt"] = lines(["2026 年 8 月各区域销售额（元）", f"华东 {aug}", f"华东二区 {rng.randint(10000, 30000)}", f"华北 {rng.randint(20000, 80000)}", f"华南 {rng.randint(20000, 80000)}"])
        files["明细/README.md"] = lines(["# 销售明细", "", "每月一个文件，列：区域、品类、销售额，销售额单位是元。", "区域名要完整匹配，「华东二区」是另一个区域。"])
        if not any(str(total) in t or f"{total:,}" in t for t in files.values()) and aug != total:
            break
    body = r'''
assert case["files"]["明细/README.md"].startswith("# 销售明细")
assert case["files"]["汇总/2026-08.txt"].splitlines()[1].startswith("华东 ")
n = 0
for path, text in case["files"].items():
    if path.startswith("明细/2026-"):
        rows = text.splitlines()
        assert rows[0] == "区域,品类,销售额", path
        n += sum(int(r.split(",")[2]) for r in rows[1:] if r.split(",")[0] == "华东")
aug = int(case["files"]["汇总/2026-08.txt"].splitlines()[1].split()[1])
print(json.dumps({"expected_contains_any": [str(aug), format(aug, ","), str(n), format(n, ",")]}))
'''
    cmd = """cat 明细/*.csv | awk -F, '$1=="华东" {s+=$3} END{print s}'"""
    return lookup_case(
        "tab-9130", desc="Two turns: one region's August figure from a single named summary file, then its yearly total across twelve monthly detail files with a look-alike region name",
        task_type="aggregate", family="fam-tab-b12e-eastyear-01", level="L3", files=files, body=body, c=cmd, want=[str(total)],
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": str(aug), "TR-DECOY": str(loose)},
        trap_note=f"- TR-MULTISRC: 汇总/2026-08.txt gives only August ({aug}); the yearly total needs all twelve 明细 files. TR-DECOY: 「华东二区」 shares the prefix with 华东 and must not be counted.",
        ref1=f"read_file 汇总/2026-08.txt -> 华东 is {aug}.", ref2=None,
        prompts=["汇总/2026-08.txt 里华东的销售额是多少？", "明细目录里 2026 年十二个月的文件，区域为华东的销售额全年合计多少元？"],
        expects=[{"output_contains_any": thousands(aug), "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains_any": thousands(total), "max_output_chars": 600}],
        alts=["华东全年销售额一共多少", "把明细里 12 个月的华东销售额加起来", "2026 年华东的销售额合计（不含华东二区）", "明细表里华东这一年卖了多少钱", "What is the yearly total for the 华东 region across the monthly detail files?"])


def log_9131():
    for seed in range(300):
        rng = Random(9131 + seed * 7919)
        paths = ["/checkout", "/checkout", "/checkout/confirm", "/cart", "/search", "/checkout/"]
        files, count, loose, first = {}, 0, 0, 0
        for n in range(1, 7):
            rows = []
            for _ in range(rng.randint(180, 240)):
                p, st = rng.choice(paths), rng.choice([200, 200, 200, 302, 404, 500, 502, 503])
                rows.append(f"2026-10-{rng.randint(1, 9):02d} {rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d} GET {p} {st} {rng.randint(8, 900)}ms")
                count += p == "/checkout" and st >= 500
                loose += p.startswith("/checkout") and st >= 500
                first += n == 1 and p == "/checkout" and st >= 500
            files[f"server/access/web-{n}.log"] = lines(rows)
        files["server/access/README.md"] = lines(["# Access logs", "", "One file per web node. Fields: date time method path status duration."])
        files["server/last-deploy.txt"] = lines(["2026-10-01 09:00 deploy 4.11.9 ok", "2026-10-03 09:00 deploy 4.12.0 rolled back", "2026-10-05 09:00 deploy 4.12.2 ok",
                                                 "2026-10-08 09:00 deploy 4.12.3 ok"])
        if count >= 60 and not any(str(count) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["server/access/README.md"].startswith("# Access logs")
assert case["files"]["server/last-deploy.txt"].splitlines()[-1] == "2026-10-08 09:00 deploy 4.12.3 ok"
n = 0
for path, text in case["files"].items():
    if path.startswith("server/access/web-"):
        for r in text.splitlines():
            f = r.split()
            assert len(f) == 6, r
            n += f[3] == "/checkout" and int(f[4]) >= 500
print(json.dumps({"expected_number": n}))
'''
    cmd = """cat server/access/*.log | awk '$4=="/checkout" && $5>=500 {n++} END{print n}'"""
    return lookup_case(
        "log-9131", desc="Two turns: the last deployed version from one named deploy log, then counting 5xx responses for one exact path across six access logs",
        task_type="count_events", family="fam-log-b12e-checkout5xx-01", level="L3", files=files, body=body, c=cmd, want=[str(count)],
        traps=["TR-DECOY", "TR-MULTISRC"], decoys={"TR-DECOY": str(loose), "TR-MULTISRC": str(first)},
        trap_note="- TR-DECOY: /checkout/confirm and /checkout/ are different paths from /checkout; 5xx means status 500-599, 404 does not count. TR-MULTISRC: six node logs.",
        ref1="read_file server/last-deploy.txt -> the last line is 4.12.3 (4.12.0 was rolled back).", ref2=None,
        prompts=["Which version did the last deploy in server/last-deploy.txt ship?", "Across the access logs in server/access, how many requests to exactly /checkout got a 5xx status?"],
        expects=[{"output_contains": ["4.12.3"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains": [str(count)], "output_contains_token": True, "max_output_chars": 600}],
        alts=["How many /checkout requests failed with a server error across the web nodes?", "Count the 5xx hits on the /checkout path in every access log.", "Total 500-599 responses for /checkout over all six logs?",
              "Sum of server-error responses on exactly /checkout from all nodes.", "统计所有 web 节点日志里 /checkout 返回 5xx 的次数"])


def fs_9132():
    rng = Random(9132)
    files = {"release/VERSION": "3.8.1\n", "release/NOTES.md": lines(["# Release notes", "", "3.8.1: bug fixes."])}
    count = 0
    for sec in ["guide", "api", "ops", "faq", "internal"]:
        for i in range(rng.randint(4, 7)):
            files[f"docs/{sec}/page-{i + 1}.md"] = f"# {sec} page {i + 1}\n"
            count += 1
    files["docs/guide/advanced/tuning.md"] = "# tuning\n"
    files["docs/api/v2/endpoints.md"] = "# endpoints\n"
    count += 2
    files["docs/guide/old-page.md.bak"] = "# stale copy\n"
    files["docs/ops/runbook.mdx"] = "# runbook (mdx)\n"
    files["docs/faq/ideas.txt"] = "ideas\n"
    for i in range(1, 6):
        files[f"docs/_build/page-{i}.md"] = f"# generated {i}\n"
    files["docs/README.md"] = lines(["# Docs", "", "Markdown sources live in the section folders.", "docs/_build/ is generated by the site build: never count it as source."])
    count += 1
    body = r'''
assert case["files"]["release/VERSION"] == "3.8.1" + chr(10)
assert case["files"]["docs/README.md"].startswith("# Docs")
n = sum(1 for p in case["files"] if p.startswith("docs/") and p.endswith(".md") and not p.startswith("docs/_build/"))
print(json.dumps({"expected_number": n}))
'''
    cmd = "find docs -name '*.md' | grep -v /_build/ | wc -l"
    return lookup_case(
        "fs-9132", desc="Two turns: a version number from one named file, then counting Markdown sources in a docs tree where generated output, backups and look-alike extensions do not count",
        task_type="count_by_type", family="fam-fs-b12e-docscount-01", level="L2", files=files, body=body, c=cmd, want=[str(count)],
        traps=["TR-DECOY"], decoys={"TR-DECOY": str(count + 5)},
        trap_note="- TR-DECOY: docs/_build holds generated .md copies (docs/README.md); .md.bak, .mdx and .txt files are not Markdown sources.",
        ref1="read_file release/VERSION -> 3.8.1.", ref2=None,
        prompts=["What version number is in release/VERSION?", "How many Markdown source files (.md) are under docs, subfolders included? docs/README.md says what does not count."],
        expects=[{"output_contains": ["3.8.1"], "forbidden_tools": ["bash"], "max_output_chars": 600},
                 {"output_contains": [str(count)], "output_contains_token": True, "max_output_chars": 600}],
        alts=["Count the .md files in docs recursively, leaving out the generated ones.", "How many Markdown pages does docs hold, excluding build output?", "Total number of source .md files under docs?",
              "Number of Markdown sources in the docs tree (not the _build folder).", "docs 目录下（含子目录）有多少个 .md 源文件？"])


# ---------------------------------------------------------------- mixed


def tab_9139():
    for seed in range(300):
        rng = Random(9139 + seed * 7919)
        cats = ["奶茶", "奶茶", "奶茶杯套", "咖啡", "果汁"]
        kinds = ["销售", "销售", "销售", "退货", "赠送"]
        files, sold, back, loose = {}, 0, 0, 0
        for store in ["东门店", "西湖店", "南站店", "高新店", "滨江店"]:
            rows = ["日期,品类,数量,类型"]
            for _ in range(rng.randint(170, 240)):
                c, k, q = rng.choice(cats), rng.choice(kinds), rng.randint(1, 9)
                rows.append(f"2026-09-{rng.randint(1, 28):02d},{c},{q},{k}")
                loose += q * (c.startswith("奶茶") and k == "退货")
                if c == "奶茶":
                    sold += q * (k == "销售")
                    back += q * (k == "退货")
            files[f"流水/{store}.csv"] = lines(rows)
        files["流水/说明.md"] = lines(["# 流水说明", "", "每个门店一个文件，列：日期、品类、数量、类型。数量单位：杯（杯套按个）。", "类型取值：销售、退货、赠送；统计销量只算「销售」，退货和赠送单独统计。",
                                      "品类名完整匹配，「奶茶杯套」不是奶茶。"])
        if sold >= 300 and back >= 100 and sold != back and not any(str(sold) in t or str(back) in t for t in files.values()):
            break
    body = r'''
assert case["files"]["流水/说明.md"].startswith("# 流水说明")
n = 0
for path, text in case["files"].items():
    if path.startswith("流水/") and path.endswith(".csv"):
        rows = text.splitlines()
        assert rows[0] == "日期,品类,数量,类型", path
        for r in rows[1:]:
            d, c, q, k = r.split(",")
            n += int(q) * (c == "奶茶" and k == "退货")
print(json.dumps({"expected_number": n}))
'''
    c1 = """cat 流水/*.csv | awk -F, '$2=="奶茶" && $4=="销售" {s+=$3} END{print s}'"""
    c2 = """cat 流水/*.csv | awk -F, '$2=="奶茶" && $4=="退货" {s+=$3} END{print s}'"""
    REFS["tab-9139"] = (files, [c1, c2], has(str(back)))
    notes = f"""## Traps
- TR-MULTISRC: five store files. TR-DECOY: 「奶茶杯套」 shares the prefix; 退货 and 赠送 rows must not count as sales (and sales rows are not returns).
- Turn 2 asks a different type ({back} cups returned) over the same files, so turn 1's number ({sold}) is the wrong answer.

## Reference solution
Turn 1: bash: `{c1}` -> {sold}
Turn 2: bash: `{c2}` -> {back}
Final answers: 奶茶卖出 {sold} 杯；退货 {back} 杯.

## Why the answer is unique
品类 and 类型 are exact fields; 流水/说明.md fixes the unit as cups.
""" + phrasings("退货的奶茶共多少杯", "各门店奶茶退货数量合计", "奶茶被退了多少杯（全部门店）", "统计所有门店退回的奶茶杯数", "How many cups of 奶茶 were returned across all stores?")
    return write_case(
        "tab-9139", desc="Two turns over five store ledgers: total milk-tea cups sold, then milk-tea cups returned, with a look-alike category and other record types",
        task_type="aggregate", family="fam-tab-b12e-milktea-01", level="L3", ref_calls=2, traps=["TR-MULTISRC", "TR-DECOY"],
        decoys={"TR-MULTISRC": str(sold), "TR-DECOY": str(loose)}, axes=["OBS", "CHN"], files=files, verify=verify_src(files, body), notes=notes,
        turns=[{"prompt": "全部门店里，奶茶卖出去的数量合计是多少杯？", "expect": {"output_contains": [str(sold)], "max_output_chars": 600}},
               {"prompt": "那被退回来的奶茶一共多少杯？", "expect": {"output_contains": [str(back)], "max_output_chars": 600}}])


def nt_9140():
    words1, words2 = ["风", "湿度", "体感"], ["回收站", "无法", "不能", "恢复"]
    body = r'''
assert len(case["turns"]) == 2 and case["turns"][0]["prompt"] and case["turns"][1]["prompt"]
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(words1 + words2, ensure_ascii=False)
    notes = """## Traps
- TR-NOTOOLNEED: both turns are general-knowledge questions; get_weather and bash are offered but no city, file or directory is involved.

## Reference solution
Turn 1: no tool call. Final answer: 体感温度是综合气温、湿度和风速得出的人体感受温度：湿度大会觉得更闷热，风大会觉得更冷。
Turn 2: no tool call. Final answer: 命令行 rm 是直接删除，不经过回收站，一般无法直接找回；要恢复只能靠备份或专门的数据恢复工具，而且越早越好。

## Why the answer is unique
Standard explanations; neither turn names a place, file or path.
""" + phrasings("体感温度和实际气温为什么不一样", "rm 删掉的文件能恢复吗", "为什么湿度大的时候体感更热", "命令行删除的东西进回收站吗", "Does the feels-like temperature depend on humidity and wind?")
    return write_case(
        "nt-9140", desc="Two concept questions (feels-like temperature, command-line delete) with get_weather and bash offered; both answered without a call",
        task_type="concept", family="fam-nt-b12e-concepts-01", level="L1", ref_calls=0, traps=["TR-NOTOOLNEED"],
        decoys={"TR-NOTOOLNEED": "查一下今天的天气"}, axes=["DEC"], files={}, verify=verify_src({}, body), notes=notes,
        turns=[{"prompt": "天气预报里的「体感温度」是怎么得出来的？为什么有时候和实际气温差很多？",
                "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words1, "max_output_chars": 600}},
               {"prompt": "还有个问题：在 Linux 命令行里用 rm 删掉的文件，还能从回收站里找回来吗？",
                "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words2, "max_output_chars": 600}}])


BUILDERS = [cfg_9121, fs_9122, doc_9123, cfg_9124, fs_9125, scr_9126, tab_9127, cfg_9128,
            doc_9129, tab_9130, log_9131, fs_9132, tab_9139, nt_9140]

SPEC = {
    "cfg-9121": dict(kind="bash_edit", sub="M9b", targets=["编排"]),
    "fs-9122": dict(kind="bash_edit", sub="M9b", targets=["笔记"]),
    "doc-9123": dict(kind="bash_edit", sub="M9b", targets=["手册"]),
    "cfg-9124": dict(kind="bash_edit", sub="M9b", targets=["envs"]),
    "fs-9125": dict(kind="bash_edit", sub="M9b", targets=["inbox", "processed"]),
    "scr-9126": dict(kind="bash_edit", sub="M9b", targets=["脚本"]),
    "tab-9127": dict(kind="bash_edit", sub="M9b", targets=["订单"]),
    "cfg-9128": dict(kind="bash_edit", sub="M9b", targets=["features"]),
    "doc-9129": dict(kind="bash_aggregate", sub="M9a", needs=["周报/README.md"]),
    "tab-9130": dict(kind="bash_aggregate", sub="M9a", needs=["明细/README.md"]),
    "log-9131": dict(kind="bash_aggregate", sub="M9a", needs=["server/access/README.md"]),
    "fs-9132": dict(kind="bash_aggregate", sub="M9a", needs=["docs/README.md"]),
    "tab-9139": dict(kind="bash_aggregate", sub="M9a", needs=["流水/说明.md"]),
    "nt-9140": dict(kind="zero_call", sub="M9e"),
}
