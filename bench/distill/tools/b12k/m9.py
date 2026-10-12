"""M9 (bash) half of the v1.41 b12k batch: ids 9261-9280. Every case is multi-turn (two or three turns).

Refine / partial revert (9261-9272): turn 1 changes a setting across a tree (README-protected exclusions stay), turn 2
reverts or re-targets part of it in two files, so the final state is not a plain replace-everywhere.
Verify (9273-9276): turn 1 is a bulk edit, turn 2 asks for a count or a name list over the whole tree that the edit
alone does not reveal (pre-existing look-alikes), answered with one bounded bash command.
Undo (9277-9280): three turns: edit, refine, then undo the whole change; the final tree equals the fixture."""
import json
from random import Random

from common import DONE, files_check, has, lines, phrasings, rules_for, verify_src, write_case

REFS = {}
BUILDERS = []


def under(f, prefix, suffix="", skip=()):
    return [p for p in f if p.startswith(prefix) and p.endswith(suffix) and not any(s in p for s in skip)]


def rep(f, paths, old, new):
    """Replace every whole line equal to old by new in the given files; the line must exist in each file."""
    out = dict(f)
    for p in paths:
        rows = f[p].split("\n")
        assert old in rows, (p, old)
        out[p] = "\n".join(new if r == old else r for r in rows)
    return out


def ren(f, pairs):
    out = {}
    moved = dict(pairs)
    for p, t in f.items():
        out[moved.get(p, p)] = t
    return out


def add_first(f, paths, line):
    out = dict(f)
    for p in paths:
        out[p] = line + "\n" + f[p]
    return out


def drop_first(f, paths, line):
    out = dict(f)
    for p in paths:
        assert f[p].startswith(line + "\n"), p
        out[p] = f[p][len(line) + 1:]
    return out


def add_second(f, paths, line):
    out = dict(f)
    for p in paths:
        first, rest = f[p].split("\n", 1)
        out[p] = first + "\n" + line + "\n" + rest
    return out


def drop_second(f, paths, line):
    out = dict(f)
    for p in paths:
        first, second, rest = f[p].split("\n", 2)
        assert second == line, p
        out[p] = first + "\n" + rest
    return out


def add_last(f, paths, line):
    return {**f, **{p: f[p] + line + "\n" for p in paths}}


def drop_last(f, paths, line):
    out = dict(f)
    for p in paths:
        assert f[p].endswith(line + "\n"), p
        out[p] = f[p][:-len(line) - 1]
    return out


def chain(cid, *, desc, task_type, family, level, files, turns, check, readme, readme_pin, traps, trap_note, alts,
          targets=None, answer=None, axes=("CON",), decoys=None):
    """turns: dicts with prompt, cmd, stage (files -> files, or None for a query turn), reply and, for the query turn,
    expect. answer (query cases): dict(needles=[...], code=<python computing the answer from `state`>, shape=...)."""
    states = [files]
    for t in turns:
        states.append(t["stage"](states[-1]) if t.get("stage") else states[-1])
    final = states[-1]
    rules = rules_for(files, final)
    expected = {p: r["equals"] for p, r in rules.items() if "equals" in r}
    commands, steps = [], []
    for i, t in enumerate(turns, 1):
        commands.append(t["cmd"])
        if t.get("stage"):
            commands.append(check)
            steps.append(f"Turn {i}:\n1. bash: `{t['cmd']}`\n2. bash: `{check}`\nFinal answer: DONE ({t['reply']}).")
        else:
            steps.append(f"Turn {i}:\n1. bash: `{t['cmd']}`\nFinal answer: {t['reply']}.")
    checker = files_check(rules, files)
    if answer:
        needles = answer["needles"]
        inner = checker

        def checker(out, root, inner=inner, needles=needles):
            return inner(out, root) or has(*needles)(out, root)
    REFS[cid] = (files, commands, checker)
    notes = f"""## Traps
{trap_note}
- Turn 2 {"asks about the whole tree, including files that already differed before turn 1" if answer else "changes part of what turn 1 did, so the final state is not a plain replace-everywhere"}{"" if len(turns) < 3 else "; turn 3 undoes the whole change"}.

## Reference solution
{chr(10).join(steps)}

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.
""" + phrasings(*alts)
    body = f"""assert case["files"][{readme!r}].startswith({readme_pin[0]!r})
assert {readme_pin[1]!r} in case["files"][{readme!r}]
FINAL = json.loads(r'''{json.dumps(expected, ensure_ascii=False)}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in %s.items():
    assert case["expect"]["files"][path] == {{"unchanged": True}}, path
state = dict(case["files"])
state.update(FINAL)
""" % json.dumps({p: 1 for p, r in rules.items() if r.get("unchanged")}, ensure_ascii=False)
    if answer:
        body += answer["code"].strip("\n") + "\n"
    else:
        body += 'print(json.dumps({"files": FINAL}, ensure_ascii=False))\n'
    turn_objs = [{"prompt": t["prompt"], "expect": dict(DONE) if t.get("stage") else answer["expect"]} for t in turns]
    axes = ["CON"] + (["OBS"] if "TR-DECOY" in traps else []) + (["CHN"] if "TR-MULTISRC" in traps else [])
    return write_case(
        cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=len(commands), traps=list(traps),
        decoys=decoys or {t: None for t in traps}, axes=axes, files=files, verify=verify_src(files, body), notes=notes,
        case_expect={"files": rules}, turns=turn_objs)


# ---------------------------------------------------------------- refine / partial revert


def cfg_9261():
    srcs = {"订单": 10, "用户": 10, "报表": 10, "日志": 10, "风控": 10}
    files = {}
    for n in srcs:
        files[f"数据源/{n}.properties"] = lines([f"# {n}库", f"url=jdbc:mysql://db-{n}:3306/{n}", "pool.size=10", "pool.size.min=10"])
    files["数据源/_归档/旧库.properties"] = lines(["# 旧库", "url=jdbc:mysql://db-old:3306/old", "pool.size=10", "pool.size.min=10"])
    files["数据源/README.md"] = lines(["# 数据源", "", "每个库一个 .properties；_归档 是已下线的库，不再维护，保持原样。",
                                      "pool.size.min 是最小空闲连接数，不随连接池上限改动。"])
    live = under(files, "数据源/", ".properties", skip=["/_归档/"])
    s1 = lambda f: rep(f, live, "pool.size=10", "pool.size=20")
    s2 = lambda f: rep(rep(f, ["数据源/订单.properties"], "pool.size=20", "pool.size=10"), ["数据源/报表.properties"], "pool.size=20", "pool.size=40")
    c1 = r"""find 数据源 -name '*.properties' | grep -v /_归档/ | xargs sed -i 's/^pool\.size=10$/pool.size=20/'"""
    c2 = r"""sed -i 's/^pool\.size=20$/pool.size=10/' 数据源/订单.properties && sed -i 's/^pool\.size=20$/pool.size=40/' 数据源/报表.properties"""
    return chain(
        "cfg-9261", desc="Two turns: raises the connection pool size from 10 to 20 in five datasource files without touching the archive or the min-size key, then returns one datasource to 10 and sets another to 40",
        task_type="edit_value", family="fam-cfg-b12k-poolsize-01", level="L3", files=files, check="grep -rn '^pool' 数据源",
        readme="数据源/README.md", readme_pin=("# 数据源", "pool.size.min 是最小空闲连接数"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 数据源/_归档 stays as it is; `pool.size.min=10` is a look-alike key the README says never changes (`s/=10/=20/` or `s/pool.size=10/.../` without anchors also hits it).",
        turns=[dict(prompt="数据库扩容：把 数据源 下各 .properties 里的 pool.size 从 10 改成 20，哪些文件和配置项不能动看 数据源/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个库的 pool.size 为 20"),
               dict(prompt="订单库只有一个小实例，pool.size 退回 10；报表库要多一点，改成 40。其余保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="订单回 10，报表 40，其余 20")],
        alts=["数据源连接池上限全部翻倍到 20（归档除外），再把订单库退回去、报表库提到 40", "pool.size 10 改 20，之后订单恢复 10，报表设为 40", "各库连接池扩到 20，订单库不扩，报表库扩到 40",
              "把连接池上限 10 批量调成 20，订单还原，报表 40", "Raise pool.size to 20 in all datasources, then put orders back to 10 and set reports to 40."])


def cfg_9262():
    svcs = ["web", "mobile", "billing", "admin", "jobs"]
    files = {}
    for n in svcs + ["example"]:
        files[f"config/{n}.env"] = lines([f"APP_NAME={n}", "API_BASE=https://api-v1.corp.io", "API_BASE_LEGACY=https://api-v1.corp.io", "TIMEOUT=30"])
    files["config/README.md"] = lines(["# Service env files", "", "One .env per service. example.env is the template for new services and stays as it is.",
                                      "API_BASE_LEGACY keeps pointing at v1 until the partner cut-over; never change it."])
    live = under(files, "config/", ".env", skip=["example.env"])
    s1 = lambda f: rep(f, live, "API_BASE=https://api-v1.corp.io", "API_BASE=https://api-v2.corp.io")
    s2 = lambda f: rep(rep(f, ["config/billing.env"], "API_BASE=https://api-v2.corp.io", "API_BASE=https://api-v1.corp.io"),
                       ["config/jobs.env"], "API_BASE=https://api-v2.corp.io", "API_BASE=https://api-v2-eu.corp.io")
    c1 = r"""find config -name '*.env' | grep -v example.env | xargs sed -i 's#^API_BASE=https://api-v1\.corp\.io$#API_BASE=https://api-v2.corp.io#'"""
    c2 = r"""sed -i 's#^API_BASE=.*$#API_BASE=https://api-v1.corp.io#' config/billing.env && sed -i 's#^API_BASE=.*$#API_BASE=https://api-v2-eu.corp.io#' config/jobs.env"""
    return chain(
        "cfg-9262", desc="Two turns: points API_BASE at the v2 endpoint in five service env files without touching the template or the legacy key, then puts billing back on v1 and jobs on a regional v2 endpoint",
        task_type="edit_value", family="fam-cfg-b12k-apibase-01", level="L3", files=files, check="grep -rn '^API_BASE=' config",
        readme="config/README.md", readme_pin=("# Service env files", "API_BASE_LEGACY keeps pointing at v1"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: config/example.env is the template and stays; API_BASE_LEGACY=https://api-v1.corp.io is a look-alike line (a global `s/api-v1/api-v2/` changes it).",
        turns=[dict(prompt="The API moved to v2. In every service's env file under config, change API_BASE from https://api-v1.corp.io to https://api-v2.corp.io. config/README.md says what must stay as it is. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="web, mobile, billing, admin, jobs on api-v2"),
               dict(prompt="Billing is not ready for v2, so put its API_BASE back on https://api-v1.corp.io. The jobs service should use the EU endpoint https://api-v2-eu.corp.io instead. Leave the other services as they are now. Reply DONE when finished.",
                    cmd=c2, stage=s2, reply="billing on v1, jobs on api-v2-eu, the rest on v2")],
        alts=["Switch API_BASE to api-v2 in all services except the template, then billing goes back to v1 and jobs gets the EU host.", "Move every service to the v2 API (not the legacy key), afterwards undo billing and give jobs api-v2-eu.",
              "api-v1 to api-v2 for API_BASE everywhere except example.env; then billing reverts and jobs uses api-v2-eu.corp.io.", "Update API_BASE for the services, then billing stays on the old API and jobs on the EU one.",
              "把各服务的 API_BASE 改到 v2，之后 billing 改回 v1、jobs 改成 EU 地址"])


def fs_9263():
    pages = {"指南/安装": "安装步骤", "指南/导入": "如何导入数据", "指南/导出": "如何导出数据", "参考/接口": "接口说明", "参考/术语": "术语说明", "博客/发布说明": "新版本发布"}
    files = {f"文档站/{p}.markdown": t + "\n" for p, t in pages.items()}
    files["文档站/发布镜像/安装.markdown"] = "安装步骤（镜像）\n"
    files["文档站/发布镜像/接口.markdown"] = "接口说明（镜像）\n"
    files["文档站/参考/变更.md"] = "变更记录\n"
    files["文档站/参考/旧笔记.markdown.bak"] = "旧笔记备份\n"
    files["文档站/README.md"] = lines(["# 文档站", "", "页面统一使用 .md 扩展名。", "发布镜像 是同步给外部站点的只读副本，文件名保持原样。"])
    mv1 = [(p, p[:-9] + ".md") for p in files if p.endswith(".markdown") and "/发布镜像/" not in p]
    mv2 = [("文档站/指南/导入.md", "文档站/指南/导入.markdown"), ("文档站/指南/导出.md", "文档站/指南/导出.markdown")]
    c1 = r"""for f in $(find 文档站 -name '*.markdown' | grep -v /发布镜像/); do mv "$f" "${f%.markdown}.md"; done"""
    c2 = r"""for n in 导入 导出; do mv 文档站/指南/$n.md 文档站/指南/$n.markdown; done"""
    return chain(
        "fs-9263", desc="Two turns: renames .markdown pages to .md except a read-only mirror folder, then renames two guide pages back to .markdown",
        task_type="bulk_edit", family="fam-fs-b12k-markdownext-01", level="L3", files=files, check="find 文档站 -type f",
        readme="文档站/README.md", readme_pin=("# 文档站", "发布镜像 是同步给外部站点的只读副本"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 文档站/发布镜像 keeps its names. TR-DECOY: 旧笔记.markdown.bak is a backup, not a .markdown page; 参考/变更.md is already .md.",
        turns=[dict(prompt="统一文档站的扩展名：把 文档站 下的 .markdown 文件都改成 .md，哪些不能改名看 文档站/README.md。改完回复 DONE。",
                    cmd=c1, stage=lambda f: ren(f, mv1), reply="六个页面改为 .md，发布镜像未动"),
               dict(prompt="旧版站点生成器还按 .markdown 引用 指南 里的导入页和导出页，这两个文件的扩展名改回 .markdown，其余保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=lambda f: ren(f, mv2), reply="导入、导出改回 .markdown，安装等仍为 .md")],
        alts=["文档站里的 .markdown 全部改成 .md（镜像除外），然后导入页和导出页再改回去", "把文档页统一成 .md 扩展名，指南里的导入导出两页之后恢复 .markdown", "markdown 扩展名换成 md，导入和导出页因为旧生成器要还原",
              ".markdown → .md，发布镜像不动；导入、导出两个文件撤销", "Rename .markdown pages to .md except the mirror, then restore .markdown for the import and export guides."])


def fs_9264():
    files = {"pipelines/build.yml": "name: build\n", "pipelines/test.yml": "name: test\n", "pipelines/deploy.yml": "name: deploy\n",
             "pipelines/lint/style.yml": "name: style\n", "pipelines/lint/types.yml": "name: types\n",
             "pipelines/legacy/nightly.yml": "name: nightly\n", "pipelines/legacy/cleanup.yml": "name: cleanup\n",
             "pipelines/vendor/upstream.yml": "name: upstream\n", "pipelines/vendor/shared.yml": "name: shared\n",
             "pipelines/old-notes.yml.bak": "stale notes\n",
             "pipelines/README.md": lines(["# Pipelines", "", "Pipeline files use the .yaml extension.", "vendor/ mirrors an upstream repository: never rename anything inside it."])}
    mv1 = [(p, p[:-4] + ".yaml") for p in files if p.endswith(".yml") and "/vendor/" not in p]
    mv2 = [("pipelines/legacy/nightly.yaml", "pipelines/legacy/nightly.yml"), ("pipelines/legacy/cleanup.yaml", "pipelines/legacy/cleanup.yml")]
    c1 = r"""for f in $(find pipelines -name '*.yml' | grep -v /vendor/); do mv "$f" "${f%.yml}.yaml"; done"""
    c2 = r"""for f in pipelines/legacy/*.yaml; do mv "$f" "${f%.yaml}.yml"; done"""
    return chain(
        "fs-9264", desc="Two turns: renames .yml pipeline files to .yaml except a vendored mirror, then renames the legacy folder's files back to .yml",
        task_type="bulk_edit", family="fam-fs-b12k-yamlext-01", level="L3", files=files, check="find pipelines -type f",
        readme="pipelines/README.md", readme_pin=("# Pipelines", "never rename anything inside it"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: pipelines/vendor stays as it is. TR-DECOY: old-notes.yml.bak is a backup file, not a .yml pipeline.",
        turns=[dict(prompt="Standardize the pipeline extension: rename every .yml file under pipelines to .yaml. pipelines/README.md says what must not be renamed. Reply DONE when finished.",
                    cmd=c1, stage=lambda f: ren(f, mv1), reply="seven pipelines renamed to .yaml, vendor untouched"),
               dict(prompt="The legacy runner only loads .yml, so rename the two files in pipelines/legacy back to .yml. Everything else stays as it is now. Reply DONE when finished.",
                    cmd=c2, stage=lambda f: ren(f, mv2), reply="legacy nightly and cleanup are .yml again")],
        alts=["Change .yml to .yaml across pipelines (vendor excluded), then restore .yml in the legacy folder.", "Rename the pipelines to the .yaml extension, but the legacy ones must go back to .yml afterwards.", "yml -> yaml everywhere except vendor; then legacy back to yml.",
              "Move all pipeline files to .yaml, leave the vendor mirror; the two legacy pipelines return to .yml.", "把 pipelines 里的 .yml 统一改成 .yaml，之后 legacy 里的两个改回 .yml"])


def doc_9265():
    head = "// 版权所有 2026 星河科技"
    names = ["core/router", "core/store", "core/utils", "ui/button", "ui/modal", "gen/schema", "gen/client", "vendor/polyfill", "vendor/mini"]
    files = {f"lib/{n}.js": lines(['"use strict";', f"exports.name = '{n.split('/')[1]}';"]) for n in names}
    files["lib/README.md"] = lines(["# lib", "", f"源文件第一行统一写版权声明：{head}", "lib/vendor 是第三方代码，保持原样。"])
    live = under(files, "lib/", ".js", skip=["/vendor/"])
    s1 = lambda f: add_first(f, live, head)
    gen = ["lib/gen/schema.js", "lib/gen/client.js"]
    s2 = lambda f: drop_first(f, gen, head)
    c1 = f"""find lib -name '*.js' | grep -v /vendor/ | xargs sed -i '1i {head}'"""
    c2 = f"""sed -i '1{{/^\\/\\/ 版权所有 2026 星河科技$/d}}' lib/gen/schema.js lib/gen/client.js"""
    return chain(
        "doc-9265", desc="Two turns: adds a copyright header line to seven JavaScript sources except a vendored folder, then removes it again from the two generated files",
        task_type="write_structured", family="fam-doc-b12k-copyhead-01", level="L3", files=files, check="head -n 2 -q lib/*/*.js",
        readme="lib/README.md", readme_pin=("# lib", "lib/vendor 是第三方代码"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: lib/vendor is third-party code and gets no header. The exact header text is only in lib/README.md.",
        turns=[dict(prompt="给 lib 下的 .js 源文件加版权声明：第一行写 lib/README.md 里规定的那一行，不该加的目录也看 README。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="七个源文件第一行已加声明，vendor 未动"),
               dict(prompt="gen 下的两个文件是构建时生成的，每次都会被重写，把它们第一行的声明去掉，其他文件保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="gen 下两个文件无声明，其余五个有")],
        alts=["lib 里的源码文件头部统一补上版权行（第三方除外），生成文件之后再去掉", "按 README 的版权声明给 js 文件加首行，vendor 不加；gen 目录两个文件撤销", "给 lib 的 js 批量加头部声明，然后 gen 里的不要",
              "添加版权头（除 vendor），再移除 gen/schema.js 和 gen/client.js 上的", "Add the copyright line to the lib sources, skip vendor, then remove it from the generated files."])


def doc_9266():
    head = "<!-- owner: docs-team -->"
    names = ["onboarding", "faq", "runbook", "eng/style", "eng/release", "legal/terms", "legal/privacy", "archive/2024-notes", "archive/old-faq"]
    files = {f"wiki/{n}.md": lines([f"# {n.split('/')[-1]}", "", f"Notes for {n}."]) for n in names}
    files["wiki/README.md"] = lines(["# Wiki", "", f"Every live page starts with the line {head}", "wiki/archive is frozen and never edited. README.md itself is not a page."])
    live = under(files, "wiki/", ".md", skip=["/archive/", "README.md"])
    s1 = lambda f: add_first(f, live, head)
    legal = ["wiki/legal/terms.md", "wiki/legal/privacy.md"]
    s2 = lambda f: drop_first(f, legal, head)
    c1 = f"""find wiki -name '*.md' | grep -v '/archive/\\|README' | xargs sed -i '1i {head}'"""
    c2 = f"""sed -i '1{{/^<!-- owner: docs-team -->$/d}}' wiki/legal/terms.md wiki/legal/privacy.md"""
    return chain(
        "doc-9266", desc="Two turns: adds an owner comment as first line of every live wiki page except the frozen archive and README, then removes it from the two legal pages",
        task_type="write_structured", family="fam-doc-b12k-ownerline-01", level="L3", files=files, check="head -n 1 -q wiki/*.md wiki/*/*.md",
        readme="wiki/README.md", readme_pin=("# Wiki", "wiki/archive is frozen"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: wiki/archive is frozen and README.md is not a page, so neither gets the line; the exact text of the line is in wiki/README.md.",
        turns=[dict(prompt="Add the owner line described in wiki/README.md as the first line of every live page under wiki. The README also says what must not be touched. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="seven live pages start with the owner comment"),
               dict(prompt="Legal owns its own pages, so remove that first line again from the two files in wiki/legal. Leave every other page as it is now. Reply DONE when finished.",
                    cmd=c2, stage=s2, reply="legal terms and privacy are back to their original text, the other five keep the line")],
        alts=["Stamp each wiki page (not the archive, not the README) with the owner comment on line one, then strip it from the legal pages.", "Put the docs-team owner comment at the top of the live wiki pages, and afterwards take it off terms.md and privacy.md.",
              "Prepend the owner line to all wiki pages except archive; legal pages must not have it.", "First line owner comment on every live page; remove from wiki/legal/*.", "给 wiki 里的在用页面第一行加上 owner 注释，再把 legal 下两页的去掉"])


def cfg_9267():
    names = ["商城", "后台", "结算", "报表", "小程序"]

    def pkg(n, retry="0.21.1"):
        return lines(["{", f'  "name": "{n}",', '  "dependencies": {', '    "axios": "0.21.1",', f'    "axios-retry": "{retry}",', '    "lodash": "4.17.21"', "  }", "}"])
    files = {f"项目/{n}/package.json": pkg(n) for n in names}
    files["项目/_vendored/package.json"] = pkg("vendored")
    files["项目/README.md"] = lines(["# 项目依赖", "", "统一升到 axios 1.6.2。", "_vendored 是拷贝来的第三方包，保持原样；axios-retry 由平台组统一管理，不动。"])
    live = under(files, "项目/", "package.json", skip=["/_vendored/"])
    s1 = lambda f: rep(f, live, '    "axios": "0.21.1",', '    "axios": "1.6.2",')
    pins = ["项目/结算/package.json", "项目/后台/package.json"]
    s2 = lambda f: rep(f, pins, '    "axios": "1.6.2",', '    "axios": "0.21.1",')
    c1 = r"""find 项目 -name package.json | grep -v /_vendored/ | xargs sed -i 's/"axios": "0\.21\.1"/"axios": "1.6.2"/'"""
    c2 = r"""sed -i 's/"axios": "1\.6\.2"/"axios": "0.21.1"/' 项目/结算/package.json 项目/后台/package.json"""
    return chain(
        "cfg-9267", desc="Two turns: bumps axios from 0.21.1 to 1.6.2 in five package.json files without touching the vendored copy or axios-retry, then pins two projects back to 0.21.1",
        task_type="edit_value", family="fam-cfg-b12k-axiosbump-01", level="L3", files=files, check="grep -rn axios 项目",
        readme="项目/README.md", readme_pin=("# 项目依赖", "axios-retry 由平台组统一管理"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 项目/_vendored stays. TR-DECOY: `\"axios-retry\": \"0.21.1\"` shares the version string with axios (a global `s/0.21.1/1.6.2/` changes it).",
        turns=[dict(prompt="依赖升级：把 项目 下各 package.json 里 axios 的版本从 0.21.1 升到 1.6.2，哪些不能动看 项目/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个项目 axios 为 1.6.2"),
               dict(prompt="结算和后台依赖的支付 SDK 只兼容 axios 0.x，这两个项目的 axios 钉回 0.21.1，其余项目保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="结算、后台回到 0.21.1，商城、报表、小程序是 1.6.2")],
        alts=["把 axios 升到 1.6.2（第三方拷贝和 axios-retry 除外），然后结算和后台再钉回 0.21.1", "项目依赖里 axios 0.21.1 全部升级，结算与后台因为支付 SDK 回退", "axios 批量升级，之后后台和结算固定回旧版本",
              "升 axios 到 1.6.2，其中结算、后台改回 0.21.1", "Bump axios to 1.6.2 in all projects, then pin settlement and admin back to 0.21.1."])


def cfg_9268():
    svcs = ["api", "web", "reports", "exporter", "worker"]

    def dockerfile(n):
        rows = ["FROM node:16-alpine", "WORKDIR /app", "COPY . .", "RUN npm ci", 'CMD ["node", "server.js"]']
        if n == "reports":
            rows = ["FROM node:16-alpine AS build", "RUN npm ci && npm run build", "FROM nginx:1.16-alpine", "COPY --from=build /app/dist /usr/share/nginx/html"]
        return lines(rows)
    files = {f"services/{n}/Dockerfile": dockerfile(n) for n in svcs}
    files["services/_base/Dockerfile"] = lines(["FROM node:16-alpine", "RUN apk add --no-cache tini"])
    files["services/README.md"] = lines(["# Services", "", "Each service has its own Dockerfile. _base is the shared base image, built by the platform team: it is not part of a version sweep."])
    live = under(files, "services/", "Dockerfile", skip=["/_base/"])

    def s1(f):
        out = dict(f)
        for p in live:
            out[p] = f[p].replace("FROM node:16-alpine", "FROM node:20-alpine")
        return out

    def s2(f):
        out = dict(f)
        for n in ("reports", "exporter"):
            p = f"services/{n}/Dockerfile"
            out[p] = f[p].replace("FROM node:20-alpine", "FROM node:16-alpine")
        return out
    c1 = r"""find services -name Dockerfile | grep -v /_base/ | xargs sed -i 's/^FROM node:16-alpine/FROM node:20-alpine/'"""
    c2 = r"""sed -i 's/^FROM node:20-alpine/FROM node:16-alpine/' services/reports/Dockerfile services/exporter/Dockerfile"""
    return chain(
        "cfg-9268", desc="Two turns: bumps the Node base image from 16 to 20 in five Dockerfiles without touching the shared base image or the look-alike nginx 1.16 stage, then pins two services back to node 16",
        task_type="edit_value", family="fam-cfg-b12k-nodebump-01", level="L3", files=files, check="grep -rn '^FROM' services",
        readme="services/README.md", readme_pin=("# Services", "_base is the shared base image"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: services/_base/Dockerfile stays on node:16-alpine. TR-DECOY: `FROM nginx:1.16-alpine` in reports ends in 16-alpine too (`s/16-alpine/20-alpine/` changes it); reports' stage is `FROM node:16-alpine AS build`.",
        turns=[dict(prompt="Bump the Node base image: in each service's Dockerfile under services, change FROM node:16-alpine to FROM node:20-alpine. services/README.md says what the sweep skips. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="api, web, reports, exporter, worker on node:20-alpine"),
               dict(prompt="reports and exporter use a native module that does not build on Node 20 yet. Pin those two back to node:16-alpine and leave the other services as they are now. Reply DONE when finished.",
                    cmd=c2, stage=s2, reply="reports and exporter back on node:16-alpine, api/web/worker on node:20-alpine")],
        alts=["Upgrade the services from node 16 to node 20, except the shared base, then reports and exporter go back to 16.", "node:16-alpine -> node:20-alpine in every service Dockerfile (not _base); afterwards revert two services.",
              "Switch all service images to Node 20, keep reports and exporter on 16.", "Move the Dockerfiles to node 20 apart from _base; pin reports/exporter to node 16 again.", "把各服务 Dockerfile 的 node 从 16 升到 20，再把 reports 和 exporter 钉回 16"])


def tab_9269():
    rng = Random(9269)
    cur = ["RMB", "RMB", "USD", "RMB-HK", "EUR"]

    def sheet(m):
        rows = ["日期,金额,币种"]
        for i in range(10):
            rows.append(f"2026-{m}-{rng.randint(1, 28):02d},{rng.randint(100, 9000)}.{rng.randint(0, 9)}0,{cur[(i + int(m)) % 5]}")
        return lines(rows)
    files = {f"财务/2026-{m}.csv": sheet(m) for m in ("07", "08", "09")}
    files["财务/对外报表.csv"] = lines(["日期,金额,币种", "2026-09-01,5000.00,RMB"])
    files["财务/模板.csv"] = lines(["日期,金额,币种", "2026-01-01,0.00,RMB"])
    files["财务/README.md"] = lines(["# 财务表", "", "币种代码统一从 RMB 改为 CNY。", "对外报表.csv 和 模板.csv 按外部系统要求保持 RMB；RMB-HK 是另一种币种，不改。"])
    live = [f"财务/2026-{m}.csv" for m in ("07", "08", "09")]

    def s1(f):
        return {p: ("".join((r[:-3] + "CNY" if r.endswith(",RMB") else r) + "\n" for r in t.splitlines()) if p in live else t) for p, t in f.items()}

    def s2(f):
        out = dict(f)
        for p in live[:2]:
            out[p] = "".join((r[:-3] + "RMB" if r.endswith(",CNY") else r) + "\n" for r in s1(files)[p].splitlines())
        return out
    c1 = r"""find 财务 -name '2026-*.csv' | xargs sed -i 's/,RMB$/,CNY/'"""
    c2 = r"""sed -i 's/,CNY$/,RMB/' 财务/2026-07.csv 财务/2026-08.csv"""
    return chain(
        "tab-9269", desc="Two turns: renames the currency code RMB to CNY in three monthly CSVs without touching the external report, the template or the RMB-HK code, then restores two months already submitted",
        task_type="filter_count", family="fam-tab-b12k-currencycode-01", level="L3", files=files, check="grep -rc CNY 财务",
        readme="财务/README.md", readme_pin=("# 财务表", "RMB-HK 是另一种币种"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 对外报表.csv and 模板.csv keep RMB. TR-DECOY: `RMB-HK` starts with RMB (a substring `s/RMB/CNY/` turns it into CNY-HK).",
        turns=[dict(prompt="币种代码统一：把 财务 下各月 CSV 里的币种 RMB 改成 CNY，哪些不能动看 财务/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="七月八月九月的 RMB 记录已改为 CNY"),
               dict(prompt="七月和八月的表已经按 RMB 报给税务系统了，这两个月改回 RMB，九月保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="七月八月又是 RMB，九月是 CNY")],
        alts=["各月流水里 RMB 换成 CNY（对外报表、模板、RMB-HK 不动），之后七八月还原", "把币种 RMB 批量改为 CNY，然后 07 和 08 两个月再改回去", "财务 CSV 的币种代码迁到 CNY，七月八月撤销",
              "RMB→CNY，只保留九月的修改", "Change RMB to CNY in the monthly sheets, then undo it for July and August."])


def cfg_9270():
    svcs = ["网关", "订单", "支付", "认证", "搜索"]
    files = {f"日志轮转/{n}.conf": lines([f"path /var/log/{n}/*.log", "rotate 7", "maxage 7", "compress"]) for n in svcs}
    files["日志轮转/_停用/旧任务.conf"] = lines(["path /var/log/旧任务/*.log", "rotate 7", "maxage 7", "compress"])
    files["日志轮转/README.md"] = lines(["# 日志轮转", "", "rotate 是保留的份数；maxage 是保留天数，由合规组管理，不随份数改动。", "_停用 里是已停用的任务，保持原样。"])
    live = [f"日志轮转/{n}.conf" for n in svcs]
    s1 = lambda f: rep(f, live, "rotate 7", "rotate 14")
    s2 = lambda f: rep(f, ["日志轮转/支付.conf", "日志轮转/认证.conf"], "rotate 14", "rotate 30")
    c1 = r"""find 日志轮转 -name '*.conf' | grep -v /_停用/ | xargs sed -i 's/^rotate 7$/rotate 14/'"""
    c2 = r"""sed -i 's/^rotate 14$/rotate 30/' 日志轮转/支付.conf 日志轮转/认证.conf"""
    return chain(
        "cfg-9270", desc="Two turns: raises the log rotation count from 7 to 14 in five service configs without touching maxage or the disabled folder, then raises two services to 30",
        task_type="edit_value", family="fam-cfg-b12k-rotatecount-01", level="L3", files=files, check="grep -rn '^rotate' 日志轮转",
        readme="日志轮转/README.md", readme_pin=("# 日志轮转", "maxage 是保留天数"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 日志轮转/_停用 stays. TR-DECOY: `maxage 7` also contains 7 (an unanchored `s/7/14/` changes it).",
        turns=[dict(prompt="日志要多留一阵：把 日志轮转 下各 .conf 里的 rotate 从 7 改成 14，哪些不能动看 日志轮转/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个服务 rotate 为 14"),
               dict(prompt="支付和认证按审计要求要保留更久，这两个服务的 rotate 改成 30，其他服务保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="支付、认证为 30，其余 14")],
        alts=["日志轮转份数从 7 提高到 14（maxage 和停用任务不动），支付和认证再提高到 30", "把 rotate 7 批量改成 rotate 14，之后支付、认证改成 30", "各服务日志多保留一倍的份数，其中支付与认证保留 30 份",
              "rotate 7→14，支付认证两个再调到 30", "Raise rotate from 7 to 14 in all active configs, then give payments and auth 30."])


def scr_9271():
    names = ["备份", "清理", "同步", "发布", "巡检"]
    files = {f"脚本集/{n}.sh": lines(["#!/bin/sh", f"# {n}任务", f'echo "{n} 开始"']) for n in names}
    files["脚本集/lib/log.sh"] = lines(["# 日志函数", "log() { echo \"$1\"; }"])
    files["脚本集/lib/net.sh"] = lines(["# 网络函数", "ping_host() { ping -c 1 \"$1\"; }"])
    files["脚本集/README.md"] = lines(["# 脚本集", "", "每个脚本的第二行统一写 set -eu。", "lib 里是被 source 的片段，不是独立脚本，不加。"])
    live = [f"脚本集/{n}.sh" for n in names]
    s1 = lambda f: add_second(f, live, "set -eu")
    s2 = lambda f: drop_second(f, ["脚本集/清理.sh", "脚本集/巡检.sh"], "set -eu")
    c1 = r"""find 脚本集 -name '*.sh' | grep -v /lib/ | xargs sed -i '1a set -eu'"""
    c2 = r"""sed -i '2{/^set -eu$/d}' 脚本集/清理.sh 脚本集/巡检.sh"""
    return chain(
        "scr-9271", desc="Two turns: adds set -eu as the second line of five shell scripts except sourced fragments, then removes it from two scripts whose commands may fail",
        task_type="fix_output", family="fam-scr-b12k-seteu-01", level="L3", files=files, check="head -n 3 脚本集/*.sh",
        readme="脚本集/README.md", readme_pin=("# 脚本集", "lib 里是被 source 的片段"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 脚本集/lib holds sourced fragments (no shebang) and gets no line. The line goes second, right after the shebang.",
        turns=[dict(prompt="给 脚本集 下的脚本加固：按 脚本集/README.md 的约定在每个脚本里加那一行，README 里说不加的不要动。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个脚本第二行是 set -eu，lib 未动"),
               dict(prompt="清理.sh 和 巡检.sh 里有些命令本来就允许失败，把这两个脚本里刚加的那一行去掉，其余脚本保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="清理、巡检没有 set -eu，其余三个有")],
        alts=["给脚本集里的脚本第二行统一加 set -eu（lib 除外），然后清理和巡检两个去掉", "按约定给脚本加严格模式那行，之后清理.sh、巡检.sh 里撤销", "批量在 shebang 下面插入 set -eu，清理与巡检不要",
              "给独立脚本加 set -eu，再把清理、巡检的那行删掉", "Add set -eu as line two of every standalone script, then remove it from the cleanup and inspection scripts."])


def code_9272():
    mods = {"api/handlers": "api", "db/session": "db", "cache/redis": "cache", "jobs/nightly": "nightly", "jobs/weekly": "weekly", "compat/shim": "shim"}
    files = {}
    for m, n in mods.items():
        rows = ["from app.logging import old_logger", "", f'old_logger.info("{n} start")']
        if m == "db/session":
            rows.append("from app.testing import old_logger_test_helper")
        files[f"app/{m}.py"] = lines(rows)
    files["app/README.md"] = lines(["# app", "", "old_logger is renamed to new_logger everywhere in app.", "app/compat re-exports the old name for plugins and must stay as it is.", "old_logger_test_helper is an unrelated test helper: do not rename it."])
    live = under(files, "app/", ".py", skip=["/compat/"])

    def s1(f):
        out = dict(f)
        for p in live:
            out[p] = "\n".join(r.replace("old_logger", "new_logger") if "old_logger_test_helper" not in r else r for r in f[p].split("\n"))
        return out

    def s2(f):
        out = dict(f)
        for p in ("app/jobs/nightly.py", "app/jobs/weekly.py"):
            out[p] = files[p]
        return out
    c1 = r"""find app -name '*.py' | grep -v /compat/ | xargs sed -i '/old_logger_test_helper/!s/old_logger/new_logger/g'"""
    c2 = r"""sed -i 's/new_logger/old_logger/g' app/jobs/nightly.py app/jobs/weekly.py"""
    return chain(
        "code-9272", desc="Two turns: renames an identifier across five Python modules without touching the compat layer or a look-alike helper name, then restores the old name in two job modules",
        task_type="fix_edge_case", family="fam-code-b12k-loggerrename-01", level="L3", files=files, check="grep -rn logger app",
        readme="app/README.md", readme_pin=("# app", "old_logger_test_helper is an unrelated test helper"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: app/compat/shim.py keeps old_logger. TR-DECOY: `old_logger_test_helper` (db/session.py) contains old_logger as a prefix and must not be renamed.",
        turns=[dict(prompt="Rename old_logger to new_logger in the Python modules under app. app/README.md says what must stay as it is. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="api, db, cache, nightly, weekly use new_logger"),
               dict(prompt="The nightly and weekly jobs run in a worker image that still ships the old package, so put old_logger back in those two files. Leave everything else as it is now. Reply DONE when finished.",
                    cmd=c2, stage=s2, reply="nightly and weekly use old_logger again, api/db/cache use new_logger")],
        alts=["Rename the logger identifier old_logger to new_logger across app (not compat, not the test helper), then revert the nightly and weekly jobs.", "Switch all modules to new_logger except the compat shim; the two job files go back to old_logger.",
              "old_logger -> new_logger everywhere in app except compat; then undo it in jobs/nightly.py and jobs/weekly.py.", "Replace the old logger name in the app modules, keeping old_logger_test_helper, then restore it in the jobs.", "把 app 里的 old_logger 改名为 new_logger，之后 nightly 和 weekly 两个任务改回去"])


# ---------------------------------------------------------------- edit, then a whole-tree question


def cfg_9273():
    svcs = {"订单": 1, "支付": 1, "库存": 1, "物流": 2, "通知": 1, "风控": 5, "搜索": 3}
    files = {f"微服务/{n}/conf.yaml": lines([f"name: {n}", f"retries: {r}", "timeout: 30"]) for n, r in svcs.items()}
    files["微服务/_样例/conf.yaml"] = lines(["name: 样例", "retries: 1", "timeout: 30"])
    files["微服务/README.md"] = lines(["# 微服务配置", "", "每个服务一个目录，配置在 conf.yaml。_样例 是新服务的复制模板，保持原样。"])
    live = [f"微服务/{n}/conf.yaml" for n, r in svcs.items() if r == 1]
    s1 = lambda f: rep(f, live, "retries: 1", "retries: 3")
    c1 = r"""find 微服务 -name conf.yaml | grep -v /_样例/ | xargs sed -i 's/^retries: 1$/retries: 3/'"""
    c2 = r"""grep -rL '^retries: 3$' 微服务 --include=conf.yaml"""
    names = ["物流", "风控", "_样例"]
    code = '''
want = sorted(p.split("/")[1] for p, t in state.items() if p.endswith("conf.yaml") and "retries: 3" not in t.splitlines())
assert want == ["_样例", "物流", "风控"], want
print(json.dumps({"expected_string": "风控"}, ensure_ascii=False))
'''
    return chain(
        "cfg-9273", desc="Two turns: sets retries from 1 to 3 in the service configs except the template, then lists the service directories whose conf.yaml still does not say retries 3",
        task_type="missing_keys", family="fam-cfg-b12k-retrieslist-01", level="L3", files=files, check="grep -rn '^retries' 微服务",
        readme="微服务/README.md", readme_pin=("# 微服务配置", "_样例 是新服务的复制模板"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 微服务/_样例 keeps retries: 1. TR-DECOY: 物流 (retries: 2) and 风控 (retries: 5) already differed before turn 1 and are not 1, so the edit leaves them; the turn-2 list is those two plus the template.",
        turns=[dict(prompt="把 微服务 下各服务 conf.yaml 里的 retries: 1 改成 retries: 3，哪些目录不能动看 微服务/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个服务 retries 为 3"),
               dict(prompt="以磁盘上现在的文件内容为准：微服务 下哪些服务目录里的 conf.yaml 的 retries 不是 3（连模板目录也算）？只回答目录名。",
                    cmd=c2, stage=None, reply="物流、风控、_样例")],
        alts=["改完之后，哪几个服务的重试次数不是 3？", "列出现在 retries 不等于 3 的服务目录", "还有哪些 conf.yaml 没有 retries: 3？只要目录名", "retries 不是 3 的服务有哪些（含模板目录）？", "Which service directories do not have retries 3 now?"],
        answer=dict(needles=names, code=code, expect={"output_contains": names, "max_output_chars": 600}))


def fs_9274():
    rng = Random(9274)
    files = {}
    for i in range(1, 9):
        files[f"incoming/report-{i:02d}.txt"] = lines([f"report {i} line {j}" for j in range(rng.randint(3, 9))])
    for i in range(1, 4):
        files[f"incoming/hold-{i:02d}.txt"] = lines([f"hold {i} line {j}" for j in range(rng.randint(2, 5))])
    for i in range(1, 6):
        files[f"done/old-{i:02d}.txt"] = lines([f"old {i} line {j}" for j in range(rng.randint(3, 9))])
    files["incoming/README.md"] = lines(["# Incoming", "", "Finished reports (report-*.txt) move to ../done. hold-*.txt are on hold and stay in incoming."])
    mv1 = [(p, "done/" + p[9:]) for p in files if p.startswith("incoming/report-")]
    s1 = lambda f: ren(f, mv1)
    final = s1(files)
    total = sum(len(t.splitlines()) for p, t in final.items() if p.startswith("done/"))
    c1 = r"""mv incoming/report-*.txt done/"""
    c2 = r"""cat done/* | wc -l"""
    code = '''
n = sum(len(t.splitlines()) for p, t in state.items() if p.startswith("done/"))
assert n == %d, n
print(json.dumps({"expected_number": n}))
''' % total
    return chain(
        "fs-9274", desc="Two turns: moves finished report files from an inbox folder to a done folder that already holds older files, then asks for the total line count of everything in done",
        task_type="count_by_type", family="fam-fs-b12k-donelines-01", level="L3", files=files, check="ls incoming done",
        readme="incoming/README.md", readme_pin=("# Incoming", "hold-*.txt are on hold"), traps=["TR-READONLY", "TR-MULTISRC"],
        trap_note="- TR-READONLY: hold-*.txt stay in incoming. TR-MULTISRC: done/ already held five older files, so the turn-2 total covers 13 files, not just the eight moved ones.",
        turns=[dict(prompt="Move the finished reports from incoming to done. incoming/README.md says which files are finished and which stay. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="eight report files are in done, hold files stay in incoming"),
               dict(prompt="How many lines do the files in done contain in total now?",
                    cmd=c2, stage=None, reply=f"{total} lines")],
        alts=["Total line count across everything in done after the move?", "How many lines are there in done in all?", "Sum the lines of every file now in the done folder.", "What is the combined number of lines of the files in done?", "现在 done 目录里所有文件一共有多少行？"],
        answer=dict(needles=[str(total)], code=code, expect={"output_contains": [str(total)], "output_contains_token": True, "max_output_chars": 600}))


def doc_9275():
    files = {"文档/入门.md": lines(["# 入门", "", "安装插件后重启应用。", "插件列表在设置里。"]),
             "文档/进阶.md": lines(["# 进阶", "", "编写插件需要实现两个接口。"]),
             "文档/FAQ.md": lines(["# FAQ", "", "问：插件装不上怎么办？", "答：检查版本。"]),
             "文档/发布.md": lines(["# 发布", "", "插件市场每周更新。"]),
             "文档/迁移.md": lines(["# 迁移", "", "旧版插件需要重新打包。"]),
             "文档/术语表.md": lines(["# 术语表", "", "插件：可独立安装的功能模块。"]),
             "文档/更新日志.md": lines(["# 更新日志", "", "1.0：首次支持插件。", "1.2：插件可以热更新。"]),
             "文档/README.md": lines(["# 文档说明", "", "文档里的「插件」统一改称「扩展」。", "术语表.md 是定义页，更新日志.md 是历史记录，两个都保持原词。"])}
    live = ["文档/入门.md", "文档/进阶.md", "文档/FAQ.md", "文档/发布.md", "文档/迁移.md"]

    def s1(f):
        out = dict(f)
        for p in live:
            out[p] = f[p].replace("插件", "扩展")
        return out
    c1 = r"""sed -i 's/插件/扩展/g' 文档/入门.md 文档/进阶.md 文档/FAQ.md 文档/发布.md 文档/迁移.md"""
    c2 = r"""grep -rl 插件 文档"""
    code = '''
want = sorted(p.split("/")[1][:-3] for p, t in state.items() if "插件" in t)
assert want == sorted(["README", "术语表", "更新日志"]), want
print(json.dumps({"expected_string": "术语表"}, ensure_ascii=False))
'''
    return chain(
        "doc-9275", desc="Two turns: replaces a product term in five doc pages except a glossary and a changelog, then lists which files in the doc folder still contain the old term",
        task_type="extract_items", family="fam-doc-b12k-termleft-01", level="L3", files=files, check="grep -rc 插件 文档",
        readme="文档/README.md", readme_pin=("# 文档说明", "更新日志.md 是历史记录"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: 术语表.md and 更新日志.md keep the old word. The README itself quotes 「插件」 in its text, so it also still contains the old term: the turn-2 list is 术语表, 更新日志 and README.",
        turns=[dict(prompt="文档用语统一：把 文档 下各页里的「插件」改成「扩展」，哪些文件要保留原词看 文档/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五页已改为扩展"),
               dict(prompt="以磁盘上现在的文件内容为准：文档 目录下还有哪些文件含有「插件」这个词？只回答文件名。",
                    cmd=c2, stage=None, reply="术语表、更新日志、README")],
        alts=["改完之后，哪些文件里还留着「插件」？", "文档里现在哪几份还含「插件」，列文件名", "列出仍然包含「插件」的文档文件", "还有哪些文档没换掉「插件」这个词？", "Which files under 文档 still contain 插件 now?"],
        answer=dict(needles=["术语表", "更新日志", "README"], code=code, expect={"output_contains": ["术语表", "更新日志", "README"], "max_output_chars": 600}))


def tab_9276():
    rng = Random(9276)
    units = ["件", "个", "箱", "件套", "个"]
    files = {}
    for m in ("07", "08", "09"):
        rows = ["货号,品名,数量,单位"]
        for i in range(rng.randint(9, 13)):
            rows.append(f"S{m}{i + 1:02d},货品{rng.randint(10, 99)},{rng.randint(1, 90)},{rng.choice(units)}")
        files[f"库存/2026-{m}.txt"] = lines(rows)
    files["库存/模板.txt"] = lines(["货号,品名,数量,单位", "示例,示例货品,0,件", "示例2,示例货品,0,个"])
    files["库存/README.md"] = lines(["# 库存表", "", "每月一个 txt，逗号分隔，最后一列是单位。", "模板.txt 是空白模板，保持原样。", "「件套」是另一种单位，不属于「件」。"])
    live = [f"库存/2026-{m}.txt" for m in ("07", "08", "09")]

    def s1(f):
        return {p: ("".join((r[:-1] + "个" if r.endswith(",件") else r) + "\n" for r in t.splitlines()) if p in live else t) for p, t in f.items()}
    n = sum(1 for p in live for r in s1(files)[p].splitlines() if r.endswith(",个"))
    c1 = r"""find 库存 -name '2026-*.txt' | xargs sed -i 's/,件$/,个/'"""
    c2 = r"""cat 库存/2026-*.txt | grep -c ',个$'"""
    code = '''
n = sum(1 for p, t in state.items() if p.startswith("库存/2026-") for r in t.splitlines() if r.endswith(",个"))
assert n == %d, n
print(json.dumps({"expected_contains_any": [str(n)]}))
''' % n
    return chain(
        "tab-9276", desc="Two turns: renames the unit 件 to 个 in three monthly stock files except the template and the look-alike 件套, then counts the rows whose unit is 个 across the three months",
        task_type="filter_count", family="fam-tab-b12k-unitcount-01", level="L3", files=files, check="grep -c ',个$' 库存/2026-07.txt 库存/2026-08.txt 库存/2026-09.txt",
        readme="库存/README.md", readme_pin=("# 库存表", "「件套」是另一种单位"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 库存/模板.txt keeps its units. TR-DECOY: 「件套」 starts with 件 (a substring `s/件/个/` also rewrites it). The turn-2 count includes rows that were 个 before turn 1.",
        turns=[dict(prompt="把 库存 下各月 txt 里单位为「件」的行改成「个」，哪些不能动看 库存/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="三个月的「件」已改为「个」"),
               dict(prompt="现在三个月的库存文件里，单位是「个」的记录一共有多少行？",
                    cmd=c2, stage=None, reply=f"{n} 行")],
        alts=["三个月合计，单位为个的有几行？", "统计 2026-07 到 2026-09 里单位列是「个」的行数", "改完以后「个」一共多少条记录（不含模板）？", "库存里单位等于个的记录总数是多少？", "How many rows have the unit 个 in the three monthly files now?"],
        answer=dict(needles=[str(n)], code=code, expect={"output_contains_any": [str(n)], "max_output_chars": 600}))


# ---------------------------------------------------------------- edit, refine, undo everything


def cfg_9277():
    svcs = ["订单", "支付", "对账", "搜索", "通知"]
    files = {f"部署/{n}.yaml": lines([f"name: {n}", f"image: registry.old.com/{n}:1.4", "# mirror: registry.old.com"]) for n in svcs}
    files["部署/_样例.yaml"] = lines(["name: 样例", "image: registry.old.com/sample:1.0", "# mirror: registry.old.com"])
    files["部署/README.md"] = lines(["# 部署清单", "", "每个服务一个 yaml；_样例.yaml 是复制模板，保持原样。", "image 行以外的注释（例如 mirror 行）不要改。"])
    live = [f"部署/{n}.yaml" for n in svcs]

    def s1(f):
        out = dict(f)
        for p in live:
            out[p] = f[p].replace("image: registry.old.com/", "image: registry.new.com/")
        return out

    def s2(f):
        out = dict(f)
        for n in ("支付", "对账"):
            out[f"部署/{n}.yaml"] = files[f"部署/{n}.yaml"]
        out["部署/搜索.yaml"] = f["部署/搜索.yaml"].replace("registry.new.com/", "registry.eu.com/")
        return out
    s3 = lambda f: files
    c1 = r"""find 部署 -name '*.yaml' | grep -v _样例 | xargs sed -i 's#^image: registry\.old\.com/#image: registry.new.com/#'"""
    c2 = r"""sed -i 's#^image: registry\.new\.com/#image: registry.old.com/#' 部署/支付.yaml 部署/对账.yaml && sed -i 's#^image: registry\.new\.com/#image: registry.eu.com/#' 部署/搜索.yaml"""
    c3 = r"""find 部署 -name '*.yaml' | grep -v _样例 | xargs sed -i -e 's#^image: registry\.new\.com/#image: registry.old.com/#' -e 's#^image: registry\.eu\.com/#image: registry.old.com/#'"""
    return chain(
        "cfg-9277", desc="Three turns: moves the image registry in five deployment manifests without touching the template or the mirror comments, keeps two on the old registry and sends one to a regional registry, then undoes the whole migration",
        task_type="edit_value", family="fam-cfg-b12k-registrymigrate-01", level="L3", files=files, check="grep -rn 'registry' 部署",
        readme="部署/README.md", readme_pin=("# 部署清单", "mirror 行"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 部署/_样例.yaml stays. TR-DECOY: `# mirror: registry.old.com` comment lines must keep the old host in every turn (a global `s/registry.old.com/registry.new.com/` changes them).\n- Turn 3 undoes both earlier turns: all five manifests end byte-identical to the fixture.",
        turns=[dict(prompt="镜像仓库迁移：把 部署 下各服务 yaml 里 image 行的 registry.old.com 换成 registry.new.com，哪些不能动看 部署/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="五个服务 image 指向 registry.new.com"),
               dict(prompt="支付和对账暂时还要用旧仓库，改回 registry.old.com；搜索服务走欧洲节点，改成 registry.eu.com。其余保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="支付、对账回旧仓库，搜索用 eu，订单通知用新仓库"),
               dict(prompt="迁移计划取消了：把 部署 下所有服务的 image 都恢复成最开始的样子（全部用 registry.old.com），模板和注释保持不动。改完回复 DONE。",
                    cmd=c3, stage=s3, reply="五个服务 image 都回到 registry.old.com")],
        alts=["仓库迁到 registry.new.com，支付对账回退、搜索改欧洲节点，最后整个迁移取消", "image 行换仓库（模板与 mirror 注释除外），局部调整后全部还原成 registry.old.com", "先迁移镜像仓库，再让两个服务回旧仓库、一个用 eu，最后统一退回最初状态",
              "registry.old.com→registry.new.com，随后支付、对账还原，搜索 eu，最后全部恢复", "Migrate the image registry, keep two services on the old one and one on eu, then cancel everything and restore the original registry."])


def fs_9278():
    files = {"etc/app.cfg": "app settings\n", "etc/db.cfg": "db settings\n", "etc/cache.cfg": "cache settings\n",
             "etc/net/proxy.cfg": "proxy settings\n", "etc/net/dns.cfg": "dns settings\n",
             "etc/legacy/mailer.cfg": "mailer settings\n", "etc/legacy/ftp.cfg": "ftp settings\n",
             "etc/readonly/base.cfg": "base settings\n", "etc/readonly/os.cfg": "os settings\n", "etc/old.cfg.bak": "old backup\n",
             "etc/README.md": lines(["# etc", "", "Config files are being renamed from .cfg to .conf.", "etc/readonly is mounted from the image: its names must not change."])}
    mv1 = [(p, p[:-4] + ".conf") for p in files if p.endswith(".cfg") and "/readonly/" not in p]
    mv2 = [("etc/legacy/mailer.conf", "etc/legacy/mailer.cfg"), ("etc/legacy/ftp.conf", "etc/legacy/ftp.cfg")]
    c1 = r"""for f in $(find etc -name '*.cfg' | grep -v /readonly/); do mv "$f" "${f%.cfg}.conf"; done"""
    c2 = r"""for f in etc/legacy/*.conf; do mv "$f" "${f%.conf}.cfg"; done"""
    c3 = r"""for f in $(find etc -name '*.conf'); do mv "$f" "${f%.conf}.cfg"; done"""
    return chain(
        "fs-9278", desc="Three turns: renames .cfg files to .conf except a read-only folder, restores the legacy ones, then undoes the whole rename",
        task_type="bulk_edit", family="fam-fs-b12k-cfgconf-01", level="L3", files=files, check="find etc -type f",
        readme="etc/README.md", readme_pin=("# etc", "etc/readonly is mounted from the image"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: etc/readonly keeps .cfg throughout. TR-DECOY: old.cfg.bak is a backup, not a .cfg file.\n- Turn 3 undoes both earlier turns: no .conf file remains and every original .cfg path is back with its content.",
        turns=[dict(prompt="Rename the config files under etc from .cfg to .conf. etc/README.md says what must not be renamed. Reply DONE when finished.",
                    cmd=c1, stage=lambda f: ren(f, mv1), reply="seven files renamed to .conf, readonly untouched"),
               dict(prompt="The legacy tools still look for .cfg, so rename the two files in etc/legacy back to .cfg. Everything else stays as it is now. Reply DONE when finished.",
                    cmd=c2, stage=lambda f: ren(f, mv2), reply="legacy files are .cfg again"),
               dict(prompt="We are cancelling the rename: put every file under etc back to the .cfg name it had at the start, nothing should end in .conf. Reply DONE when finished.",
                    cmd=c3, stage=lambda f: files, reply="all files are .cfg again")],
        alts=["Rename .cfg to .conf under etc (not readonly), restore legacy, then roll back the entire rename.", "Change the config extension to .conf, put legacy back to .cfg, finally cancel the change completely.", ".cfg -> .conf except readonly; legacy returns; then everything goes back to .cfg.",
              "Do the extension migration, partially revert legacy, then undo the rest as well.", "把 etc 里的 .cfg 改成 .conf，legacy 改回去，最后整体撤销，全部恢复 .cfg"])


def doc_9279():
    foot = "-- reviewed 2026"
    names = ["intro", "setup", "api", "faq", "legal/terms", "legal/privacy", "drafts/ideas", "drafts/todo"]
    files = {f"docs/{n}.md": lines([f"# {n.split('/')[-1]}", "", f"Text of {n}."]) for n in names}
    files["docs/README.md"] = lines(["# Docs", "", f"Reviewed pages end with the line {foot}", "docs/drafts holds unreviewed pages and never gets it. README.md is not a page."])
    live = under(files, "docs/", ".md", skip=["/drafts/", "README.md"])
    s1 = lambda f: add_last(f, live, foot)
    s2 = lambda f: drop_last(f, ["docs/legal/terms.md", "docs/legal/privacy.md"], foot)
    s3 = lambda f: files
    c1 = f"""find docs -name '*.md' | grep -v '/drafts/\\|README' | xargs sed -i '$a {foot}'"""
    c2 = r"""sed -i '/^-- reviewed 2026$/d' docs/legal/terms.md docs/legal/privacy.md"""
    c3 = r"""find docs -name '*.md' | xargs sed -i '/^-- reviewed 2026$/d'"""
    return chain(
        "doc-9279", desc="Three turns: appends a reviewed footer line to six doc pages except drafts and README, removes it from the two legal pages, then removes it from everything",
        task_type="write_structured", family="fam-doc-b12k-footerline-01", level="L3", files=files, check="tail -n 1 -q docs/*.md docs/*/*.md",
        readme="docs/README.md", readme_pin=("# Docs", "docs/drafts holds unreviewed pages"), traps=["TR-READONLY"],
        trap_note="- TR-READONLY: docs/drafts and README.md never get the footer. Every append goes on its own last line and every removal restores the original bytes (files end with one newline).\n- Turn 3 undoes both earlier turns: all files are byte-identical to the fixture.",
        turns=[dict(prompt="Mark the reviewed pages: append the footer line described in docs/README.md as the last line of each page under docs. The README also says what must be left alone. Reply DONE when finished.",
                    cmd=c1, stage=s1, reply="six pages end with the reviewed line"),
               dict(prompt="Legal has not signed off yet, so remove that footer line again from the two pages in docs/legal. Everything else stays as it is now. Reply DONE when finished.",
                    cmd=c2, stage=s2, reply="legal pages have no footer, intro/setup/api/faq keep it"),
               dict(prompt="The review process was dropped: remove the footer line from every page that still has it, so the docs look exactly as they did at the start. Reply DONE when finished.",
                    cmd=c3, stage=s3, reply="no page has the footer")],
        alts=["Append the reviewed footer to the live pages, take it off the legal ones, then remove it everywhere.", "Add the review stamp at the bottom of docs pages (not drafts or README), undo for legal, finally strip all stamps.", "Footer line on pages except drafts; legal pages without; then no footers at all.",
              "Stamp the docs as reviewed, un-stamp legal, finally revert the entire change.", "给 docs 页面末尾加 reviewed 页脚，legal 两页去掉，最后全部撤销"])


def tab_9280():
    rng = Random(9280)
    files = {}
    for d in ("华北", "华东", "华南", "西南"):
        rows = ["姓名,手机,备用手机,城市"]
        for i in range(6):
            rows.append(f"客户{rng.randint(10, 99)},1380000{rng.randint(1000, 9999)},1390000{rng.randint(1000, 9999)},{d}")
        files[f"客户/{d}.csv"] = lines(rows)
    files["客户/导出模板.csv"] = lines(["姓名,手机,备用手机,城市", "示例,13800000000,13900000000,示例"])
    files["客户/README.md"] = lines(["# 客户表", "", "表头「手机」统一改称「手机号」。", "导出模板.csv 是外部系统的导入模板，保持原样；「备用手机」是另一列，表头不改。"])
    live = [f"客户/{d}.csv" for d in ("华北", "华东", "华南", "西南")]

    def head(f, paths, old, new):
        out = dict(f)
        for p in paths:
            first, rest = f[p].split("\n", 1)
            assert first == old, p
            out[p] = new + "\n" + rest
        return out
    h0, h1 = "姓名,手机,备用手机,城市", "姓名,手机号,备用手机,城市"
    s1 = lambda f: head(f, live, h0, h1)
    s2 = lambda f: head(f, ["客户/华东.csv", "客户/西南.csv"], h1, h0)
    s3 = lambda f: files
    c1 = r"""find 客户 -name '*.csv' | grep -v 导出模板 | xargs sed -i '1s/,手机,/,手机号,/'"""
    c2 = r"""sed -i '1s/,手机号,/,手机,/' 客户/华东.csv 客户/西南.csv"""
    c3 = r"""find 客户 -name '*.csv' | xargs sed -i '1s/,手机号,/,手机,/'"""
    return chain(
        "tab-9280", desc="Three turns: renames the phone column header in four customer CSVs except the import template, reverts two of them, then restores every header",
        task_type="filter_count", family="fam-tab-b12k-phoneheader-01", level="L3", files=files, check="head -n 1 -q 客户/*.csv",
        readme="客户/README.md", readme_pin=("# 客户表", "「备用手机」是另一列"), traps=["TR-READONLY", "TR-DECOY"],
        trap_note="- TR-READONLY: 客户/导出模板.csv keeps its header. TR-DECOY: the header 「备用手机」 contains 手机 (a global `s/手机/手机号/` renames it too); only the header line changes, never the data rows.\n- Turn 3 undoes both earlier turns: all headers end as in the fixture.",
        turns=[dict(prompt="表头统一：把 客户 下各 CSV 第一行里的「手机」改成「手机号」，哪些不能动看 客户/README.md。改完回复 DONE。",
                    cmd=c1, stage=s1, reply="四个区域表的表头是手机号"),
               dict(prompt="华东和西南的两个文件还要被旧报表读取，表头改回「手机」，其余文件保持现在的样子。改完回复 DONE。",
                    cmd=c2, stage=s2, reply="华东、西南回到手机，华北、华南是手机号"),
               dict(prompt="这次改名整体撤销：客户 下所有 CSV 的表头都恢复成最开始的样子，数据行不要动。改完回复 DONE。",
                    cmd=c3, stage=s3, reply="所有表头都是手机")],
        alts=["把各区域客户表的表头手机改为手机号，华东西南改回，最后全部撤销", "表头「手机」→「手机号」（模板和备用手机除外），局部还原后整体恢复", "先统一改表头，再让华东西南回旧表头，最后所有文件回到初始表头",
              "客户 CSV 表头改名，两个文件还原，再把剩下的也还原", "Rename the phone header in the customer sheets, restore two, then restore all headers to the originals."])


BUILDERS += [cfg_9261, cfg_9262, fs_9263, fs_9264, doc_9265, doc_9266, cfg_9267, cfg_9268, tab_9269, cfg_9270, scr_9271, code_9272,
             cfg_9273, fs_9274, doc_9275, tab_9276, cfg_9277, fs_9278, doc_9279, tab_9280]


SPEC = {
    "cfg-9261": dict(kind="bash_edit", sub="M9b", targets=["数据源"]),
    "cfg-9262": dict(kind="bash_edit", sub="M9b", targets=["config"]),
    "fs-9263": dict(kind="bash_edit", sub="M9b", targets=["文档站"]),
    "fs-9264": dict(kind="bash_edit", sub="M9b", targets=["pipelines"]),
    "doc-9265": dict(kind="bash_edit", sub="M9b", targets=["lib"]),
    "doc-9266": dict(kind="bash_edit", sub="M9b", targets=["wiki"]),
    "cfg-9267": dict(kind="bash_edit", sub="M9b", targets=["项目"]),
    "cfg-9268": dict(kind="bash_edit", sub="M9b", targets=["services"]),
    "tab-9269": dict(kind="bash_edit", sub="M9b", targets=["财务"]),
    "cfg-9270": dict(kind="bash_edit", sub="M9b", targets=["日志轮转"]),
    "scr-9271": dict(kind="bash_edit", sub="M9b", targets=["脚本集"]),
    "code-9272": dict(kind="bash_edit", sub="M9b", targets=["app"]),
    "cfg-9273": dict(kind="bash_aggregate", sub="M9a"),
    "fs-9274": dict(kind="bash_aggregate", sub="M9a"),
    "doc-9275": dict(kind="bash_aggregate", sub="M9a"),
    "tab-9276": dict(kind="bash_aggregate", sub="M9a"),
    "cfg-9277": dict(kind="bash_edit", sub="M9b", targets=["部署"]),
    "fs-9278": dict(kind="bash_edit", sub="M9b", targets=["etc"]),
    "doc-9279": dict(kind="bash_edit", sub="M9b", targets=["docs"]),
    "tab-9280": dict(kind="bash_edit", sub="M9b", targets=["客户"]),
}
