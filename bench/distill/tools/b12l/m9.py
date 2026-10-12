"""M9 (bash) batch b12l of v1.41: ids 9301-9320. All M9b single-turn bulk edits across 3+ files in domains not used
before: compose ports/tags, .gitignore, ini, logrotate, locale files, markdown links, SQL migrations, shell scripts,
CSS/HTML. Every case has a README-protected file and a look-alike decoy."""
import json
import os
from random import Random

from common import lines
from common import write_case as _write_case

REFS = {}
SPEC = {
    "cfg-9301": dict(kind="bash_edit", sub="M9b", targets=["栈"]),
    "cfg-9302": dict(kind="bash_edit", sub="M9b", targets=["基础设施"]),
    "cfg-9303": dict(kind="bash_edit", sub="M9b", targets=["packages"]),
    "cfg-9304": dict(kind="bash_edit", sub="M9b", targets=["项目"]),
    "cfg-9305": dict(kind="bash_edit", sub="M9b", targets=["php"]),
    "cfg-9306": dict(kind="bash_edit", sub="M9b", targets=["轮转"]),
    "cfg-9307": dict(kind="bash_edit", sub="M9b", targets=["logrotate.d"]),
    "fs-9308": dict(kind="bash_edit", sub="M9b", targets=["语言包"]),
    "fs-9309": dict(kind="bash_edit", sub="M9b", targets=["i18n"]),
    "fs-9310": dict(kind="bash_edit", sub="M9b", targets=["db/migrations"]),
    "fs-9311": dict(kind="bash_edit", sub="M9b", targets=["数据库"]),
    "fs-9312": dict(kind="bash_edit", sub="M9b", targets=["web"]),
    "fs-9313": dict(kind="bash_edit", sub="M9b", targets=["站点"]),
    "doc-9314": dict(kind="bash_edit", sub="M9b", targets=["文档"]),
    "doc-9315": dict(kind="bash_edit", sub="M9b", targets=["说明"]),
    "doc-9316": dict(kind="bash_edit", sub="M9b", targets=["手册"]),
    "doc-9317": dict(kind="bash_edit", sub="M9b", targets=["posts"]),
    "scr-9318": dict(kind="bash_edit", sub="M9b", targets=["脚本"]),
    "scr-9319": dict(kind="bash_edit", sub="M9b", targets=["bin"]),
    "scr-9320": dict(kind="bash_edit", sub="M9b", targets=["ops"]),
}


def write_case(cid, *, files, verify, **kw):
    if "LINES = " not in verify:
        guard = "LINES = %r\nfor _p, _n in LINES.items():\n    assert len(case[\"files\"][_p].splitlines()) == _n, _p\n" % {p: len(t.splitlines()) for p, t in files.items()}
        verify = verify.replace('case = json.load(open("case.json"))\n', 'case = json.load(open("case.json"))\n' + guard, 1)
    return _write_case(cid, files=files, verify=verify, **kw)


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def files_check(rules, originals):
    def check(_out, root):
        for path, rule in rules.items():
            full = os.path.join(root, path)
            if not os.path.exists(full):
                return "%s missing" % path
            want = rule["equals"] if "equals" in rule else originals[path]
            text = open(full, encoding="utf-8").read()
            if text != want:
                return "%s = %r" % (path, text[:200])
        return None
    return check


def rules_for(files, final):
    return {p: ({"unchanged": True} if final[p] == t else {"equals": final[p]}) for p, t in files.items()}


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
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == __K__
print(json.dumps({"files": changed}))
'''


def edit_case(cid, *, topic, desc, prompt, files, rewrite_src, readme, cmd, check, target, traps, decoys, alts, why,
              task_type="bulk_edit", level="L2"):
    ns = {}
    exec(rewrite_src, ns)
    rewrite = ns["rewrite"]
    final, changed = {}, 0
    for path, text in files.items():
        new = rewrite(path, text)
        if new is None:
            final[path] = text
        else:
            assert new != text, path
            final[path] = new
            changed += 1
    assert changed >= 3, cid
    rules = rules_for(files, final)
    head = files[readme].split("\n")[0]
    verify = (EDIT_VERIFY.replace("__LINES__", repr({p: len(t.splitlines()) for p, t in files.items()}))
              .replace("__README__", repr(readme)).replace("__HEAD__", repr(head))
              .replace("__SRC__", rewrite_src.strip("\n")).replace("__K__", str(changed)))
    trap_lines = "\n".join(f"- {k}: {v}" for k, v in traps.items())
    notes = f"""## Traps
{trap_lines}

## Reference solution
1. bash: `{cmd}`
2. bash: `{check}` to confirm the target files changed and the protected ones did not.
Final answer: DONE ({why}).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical ({changed} files change).
""" + phrasings(*alts)
    REFS[cid] = (files, [cmd, check], files_check(rules, files))
    assert SPEC[cid]["targets"] == [target], cid
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12l-{topic}-01", level=level, ref_calls=2,
        traps=list(traps), decoys=decoys, axes=["CON", "OBS"], files=files, verify=verify, notes=notes,
        case_expect={"files": rules},
        turns=[{"prompt": prompt, "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


# ------------------------------------------------------------------ cfg


def cfg_9301():
    rng = Random(9301)
    files = {}
    for svc, inner in [("接口", 80), ("前台", 3000), ("后台", 8000), ("文档", 80), ("旧版", 80)]:
        files[f"栈/{svc}/docker-compose.yml"] = lines([
            "services:", "  app:", f"    image: corp/{svc}-app:{rng.randint(2, 5)}.{rng.randint(0, 9)}", "    ports:",
            f'      - "8080:{inner}"', '      - "18080:8080"', "    restart: always"])
    files["栈/说明.md"] = lines(["# 编排说明", "", "旧版 目录是给老客户保留的，对外端口约定 8080，保持原样。",
                               "18080 是监控端口，是另一个映射，不属于这次调整。"])
    src = '''
def rewrite(path, text):
    if not path.endswith("/docker-compose.yml") or "/旧版/" in path:
        return None
    new = text.replace('- "8080:', '- "8090:')
    return new if new != text else None
'''
    return edit_case(
        "cfg-9301", topic="composeport", desc="Moves the published host port 8080 to 8090 in four compose files while a legacy stack and the look-alike 18080 monitoring mapping stay",
        prompt="宿主机的 8080 端口被占用了，把 栈 目录下各服务 docker-compose.yml 里对外映射的 8080 改成 8090（容器内端口不变）。哪些不能动看 栈/说明.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="栈/说明.md",
        cmd=r"""find 栈 -name docker-compose.yml | grep -v /旧版/ | xargs sed -i 's/- "8080:/- "8090:/'""",
        check="grep -rn '8080\\|8090' 栈", target="栈",
        traps={"TR-READONLY": "栈/旧版 keeps its 8080 mapping (栈/说明.md).",
               "TR-DECOY": '"18080:8080" is the monitoring mapping and contains 8080 twice; only the leading host port 8080 of the main mapping changes.'},
        decoys={"TR-READONLY": None, "TR-DECOY": "18080:8080"},
        alts=["栈 里各服务 compose 文件的宿主机端口 8080 换成 8090，旧版目录和监控端口别动。", "docker-compose.yml 里对外的 8080 全部改成 8090，说明.md 里点名的不要改，完成回复 DONE。",
              "把 栈 下四个服务的 ports 映射从 8080:xx 调整为 8090:xx，容器端口保持，监控的 18080 不变。", "栈目录里的端口 8080 要让出来，改为 8090（只改左边的宿主机端口），改完回复 DONE。",
              "Change the published host port 8080 to 8090 in the compose files under 栈, leave what the README protects, reply DONE."],
        why="the four live stacks publish 8090; 旧版 and the 18080 mappings are unchanged", task_type="edit_value")


def cfg_9302():
    rng = Random(9302)
    files = {}
    for svc in ["缓存", "会话", "队列", "限流", "测试旧环境"]:
        files[f"基础设施/{svc}/compose.yaml"] = lines([
            "services:", "  redis:", "    image: redis:6.2-alpine", f"    container_name: {svc}-redis",
            "  proxy:", "    image: corp/redis-proxy:6.2-alpine", f"    mem_limit: {rng.choice([256, 512, 1024])}m"])
    files["基础设施/README.md"] = lines(["# 基础设施", "", "redis 官方镜像统一升到 7.2；测试旧环境 专门验证 6.2 的兼容性，必须继续用 6.2。",
                                      "redis-proxy 是自研镜像，版本号单独管理。"])
    src = '''
def rewrite(path, text):
    if not path.endswith("/compose.yaml") or "/测试旧环境/" in path:
        return None
    new = text.replace("image: redis:6.2-alpine", "image: redis:7.2-alpine")
    return new if new != text else None
'''
    return edit_case(
        "cfg-9302", topic="redisbump", desc="Bumps the official redis image tag from 6.2 to 7.2 in four compose files while a compatibility environment and a look-alike proxy image keep 6.2",
        prompt="redis 官方镜像要从 6.2-alpine 升级到 7.2-alpine，改 基础设施 下各 compose.yaml。例外和别的镜像看 基础设施/README.md。改完回复 DONE。",
        files=files, rewrite_src=src, readme="基础设施/README.md",
        cmd=r"""find 基础设施 -name compose.yaml | grep -v /测试旧环境/ | xargs sed -i 's#image: redis:6.2-alpine#image: redis:7.2-alpine#'""",
        check="grep -rn 'image:' 基础设施", target="基础设施",
        traps={"TR-READONLY": "基础设施/测试旧环境 must stay on redis:6.2-alpine (README).",
               "TR-DECOY": "corp/redis-proxy:6.2-alpine also ends in 6.2-alpine; a bare `s/6.2-alpine/7.2-alpine/` would break it."},
        decoys={"TR-READONLY": None, "TR-DECOY": "corp/redis-proxy:6.2-alpine"},
        alts=["把各服务 compose 里的 redis 镜像升级到 7.2-alpine，兼容性测试环境保持 6.2。", "基础设施下 redis:6.2-alpine → redis:7.2-alpine，redis-proxy 不属于这次升级。",
              "升级 redis 镜像标签 6.2 到 7.2（四个服务），测试旧环境不要动，改完回复 DONE。", "对 基础设施 里的 compose.yaml 批量把 redis 版本换成 7.2-alpine，README 里说的例外照办。",
              "Bump the official redis image to 7.2-alpine in every compose.yaml under 基础设施 except the one the README pins, reply DONE."],
        why="缓存, 会话, 队列 and 限流 use redis:7.2-alpine; 测试旧环境 and the redis-proxy images are unchanged", task_type="edit_value")


def cfg_9303():
    rng = Random(9303)
    files = {}
    for pkg in ["core", "web", "cli", "docs", "vendor-fork"]:
        rows = ["node_modules/", "dist/", rng.choice(["*.log", "coverage/", ".cache/"])]
        if pkg == "web":
            rows.append(".env")
        files[f"packages/{pkg}/.gitignore"] = lines(rows)
    files["packages/NOTES.md"] = lines(["# Packages", "", "vendor-fork is synced from upstream and its .gitignore must stay byte-identical.",
                                         ".env is the committed-template env file; .env.local is the personal override that must be ignored."])
    src = '''
def rewrite(path, text):
    if not path.endswith("/.gitignore") or "/vendor-fork/" in path:
        return None
    return text + ".env.local\\n"
'''
    return edit_case(
        "cfg-9303", topic="gitignoreenv", desc="Appends .env.local to the .gitignore of four packages while a synced vendor fork keeps its file and an existing .env line is not the same entry",
        prompt="Add a new line `.env.local` at the end of every package's .gitignore under packages. packages/NOTES.md says which one must stay as it is. Reply DONE when finished.",
        files=files, rewrite_src=src, readme="packages/NOTES.md",
        cmd=r"""for f in $(find packages -name .gitignore | grep -v /vendor-fork/); do echo .env.local >> "$f"; done""",
        check="tail -n 2 packages/*/.gitignore", target="packages",
        traps={"TR-READONLY": "packages/vendor-fork/.gitignore is synced from upstream (NOTES.md); web's existing `.env` line is a different entry and the new line is still appended."},
        decoys={"TR-READONLY": None},
        alts=["Append .env.local to each .gitignore in packages, except the one NOTES.md protects.", "Every packages/*/.gitignore should end with a .env.local line; leave the upstream-synced one alone. Reply DONE.",
              "packages 下各包的 .gitignore 末尾加一行 .env.local，NOTES.md 里点名的不改，完成后回复 DONE。", "Make the four package .gitignore files ignore .env.local by adding it as the last line, skip the vendor fork, say DONE.",
              "给 packages 里的 .gitignore 都追加 .env.local（vendor-fork 除外），改完回复 DONE。"],
        why="core, web, cli and docs end with .env.local; vendor-fork is unchanged", task_type="edit_value")


def cfg_9304():
    files = {}
    for name in ["订单", "会员", "报表", "推送"]:
        files[f"项目/{name}/.gitignore"] = lines(["node_modules/", "build/", "docs/build/", "rebuild/", "*.log"])
    files["项目/归档2023/.gitignore"] = lines(["node_modules/", "build/", "*.log"])
    files["项目/README.md"] = lines(["# 项目约定", "", "构建产物目录从 build/ 改名为 out/。归档2023 是冻结的历史仓库，不再改动。",
                                  "docs/build/ 是文档站的独立目录，rebuild/ 是另一个目录，和构建产物目录无关。"])
    src = '''
def rewrite(path, text):
    if not path.endswith("/.gitignore") or "/归档2023/" in path:
        return None
    new = "\\n".join("out/" if r == "build/" else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "cfg-9304", topic="gitignorebuild", desc="Renames the build/ ignore entry to out/ in four project gitignore files while a frozen archive and look-alike docs/build/ and rebuild/ entries stay",
        prompt="构建产物目录从 build 改名叫 out 了，把 项目 下各 .gitignore 里的 build/ 条目改成 out/。哪些不能动看 项目/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="项目/README.md",
        cmd=r"""find 项目 -name .gitignore | grep -v /归档2023/ | xargs sed -i 's#^build/$#out/#'""",
        check="grep -rn 'build\\|out' 项目", target="项目",
        traps={"TR-READONLY": "项目/归档2023 is frozen (README); docs/build/ and rebuild/ contain build/ as a substring, only the whole line `build/` changes."},
        decoys={"TR-READONLY": None},
        alts=["项目里的 .gitignore，把 build/ 这一条换成 out/，历史归档仓库除外。", "构建目录改名为 out，请同步各项目的 gitignore（只改整行 build/），README 里点名的别动。",
              "批量把 .gitignore 中的 build/ 替换成 out/，文档站的 docs/build/ 不改，改完回复 DONE。", "项目下四个仓库的忽略规则 build/ 要改为 out/，归档2023 保持原样。",
              "Rename the ignored build/ entry to out/ in the project .gitignore files, skipping the frozen archive, reply DONE."],
        why="订单, 会员, 报表 and 推送 ignore out/; 归档2023 and the docs/build/ and rebuild/ lines are unchanged", task_type="edit_value")


def cfg_9305():
    rng = Random(9305)
    files = {}
    for name in ["fpm", "web", "admin", "cron", "cli"]:
        files[f"php/{name}.ini"] = lines([
            "[PHP]", "memory_limit = 128M", ";memory_limit = 128M", f"max_execution_time = {rng.choice([30, 60, 120])}",
            "opcache.memory_consumption = 128", f"post_max_size = {rng.choice([8, 16, 32])}M"])
    files["php/README.md"] = lines(["# PHP 配置", "", "命令行用的 cli.ini 要保持 128M，别人的脚本是按它测的。",
                                 "以分号开头的是注释，opcache.memory_consumption 是另一个参数，都不用改。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".ini") or path.endswith("/cli.ini"):
        return None
    new = "\\n".join("memory_limit = 256M" if r == "memory_limit = 128M" else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "cfg-9305", topic="memlimit", desc="Raises memory_limit from 128M to 256M in four php ini files while the CLI ini, a commented-out copy and the opcache setting stay",
        prompt="线上 PHP 内存不够，把 php 目录下各 .ini 里的 memory_limit 从 128M 调到 256M。注意事项在 php/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="php/README.md",
        cmd=r"""find php -name '*.ini' | grep -v cli.ini | xargs sed -i 's/^memory_limit = 128M$/memory_limit = 256M/'""",
        check="grep -rn 'memory' php", target="php",
        traps={"TR-READONLY": "php/cli.ini keeps 128M (README).",
               "TR-DECOY": ";memory_limit = 128M is a commented copy and opcache.memory_consumption = 128 is another setting."},
        decoys={"TR-READONLY": None, "TR-DECOY": ";memory_limit"},
        alts=["php 里 fpm、web、admin、cron 的 ini，memory_limit 改成 256M，cli 不动。", "把 128M 的 memory_limit 全部提高到 256M（只改生效的那行），README 里说保留的保留。",
              "php/*.ini 批量调整内存上限为 256M，注释行和 opcache 的值别碰，完成回复 DONE。", "PHP 的 memory_limit 从 128M 升到 256M，cli.ini 例外，改完回复 DONE。",
              "Raise the active memory_limit from 128M to 256M in the php ini files except the CLI one, reply DONE."],
        why="fpm, web, admin and cron have memory_limit = 256M; cli.ini, the commented line and opcache are unchanged", task_type="edit_value")


def logrotate_body(path, kind, rng):
    return lines([f"{path} {{", f"    {kind}", f"    rotate {rng.choice([7, 14, 30])}", "    compress", "    missingok", "    notifempty", "}"])


def cfg_9306():
    rng = Random(9306)
    files = {}
    for name, path in [("nginx", "/var/log/nginx/*.log"), ("应用", "/var/log/app/*.log"), ("任务", "/var/log/job/*.log"), ("邮件", "/var/log/mailer/*.log"), ("审计", "/var/log/audit/*.log")]:
        files[f"轮转/{name}"] = logrotate_body(path, "daily", rng)
    files["轮转/说明.txt"] = lines(["日志轮转说明", "", "磁盘宽裕后普通日志改为每周轮转一次。", "审计 日志按合规要求必须每天轮转，保持原样。",
                                 "rotate 后面的保留份数不属于这次调整。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("轮转/") or path.endswith("说明.txt") or path.endswith("/审计"):
        return None
    new = "\\n".join("    weekly" if r == "    daily" else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "cfg-9306", topic="rotateweekly", desc="Switches logrotate frequency from daily to weekly in four configs while the compliance audit config stays daily",
        prompt="磁盘够用了，轮转 目录下各个 logrotate 配置的轮转频率从 daily 改成 weekly。哪个不能改看 轮转/说明.txt，改完回复 DONE。",
        files=files, rewrite_src=src, readme="轮转/说明.txt",
        cmd=r"""ls 轮转/* | grep -v 审计 | grep -v 说明 | xargs sed -i 's/^    daily$/    weekly/'""",
        check="grep -rn 'daily\\|weekly' 轮转", target="轮转",
        traps={"TR-READONLY": "轮转/审计 must stay daily (说明.txt, compliance).",
               "TR-DECOY": "轮转/说明.txt itself talks about rotation; it is a note, not a config."},
        decoys={"TR-READONLY": None, "TR-DECOY": "说明.txt"},
        alts=["轮转配置里的 daily 全部换成 weekly，审计的保持每天。", "把 logrotate 的 daily 改为 weekly（nginx、应用、任务、邮件），合规那份别动。",
              "轮转目录下除审计外，频率统一调成每周，改完回复 DONE。", "logrotate 文件里 `daily` → `weekly`，审计和说明文件不改，完成后回复 DONE。",
              "Change the rotation frequency from daily to weekly in the logrotate configs except the audit one, reply DONE."],
        why="nginx, 应用, 任务 and 邮件 rotate weekly; 审计 stays daily and the note is unchanged", task_type="edit_value")


def cfg_9307():
    rng = Random(9307)
    files = {}
    for name, path in [("web日志", "/var/log/web/*.log"), ("支付日志", "/var/log/pay/*.log"), ("搜索日志", "/var/log/search/*.log"), ("网关日志", "/var/log/gw/*.log"), ("遗留日志", "/var/log/old/*.log")]:
        body = logrotate_body(path, "weekly", rng).replace("    notifempty\n", "    notifempty\n    compresscmd /usr/bin/zstd\n" if name == "网关日志" else "    notifempty\n")
        files[f"logrotate.d/{name}.conf"] = body
    files["logrotate.d/README.md"] = lines(["# logrotate.d", "", "为了让进程先释放文件句柄，压缩要延迟一个周期：在 compress 下面加一行 delaycompress。",
                                         "遗留日志.conf 由老系统生成，别手改。compresscmd 是指定压缩程序的另一个指令，不用管。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".conf") or path.endswith("/遗留日志.conf"):
        return None
    new = text.replace("    compress\\n", "    compress\\n    delaycompress\\n")
    return new if new != text else None
'''
    return edit_case(
        "cfg-9307", topic="delaycompress", desc="Inserts delaycompress below compress in four logrotate configs while the legacy generated config stays and a compresscmd line is left alone",
        prompt="logrotate.d 下的配置要加延迟压缩：在 compress 那行的下面插入一行 delaycompress。例外看 logrotate.d/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="logrotate.d/README.md",
        cmd=r"""find logrotate.d -name '*.conf' | grep -v 遗留日志 | xargs sed -i 's/^    compress$/    compress\n    delaycompress/'""",
        check="grep -rn -A1 'compress' logrotate.d", target="logrotate.d",
        traps={"TR-READONLY": "logrotate.d/遗留日志.conf is generated by the old system (README).",
               "TR-DECOY": "网关日志.conf has a compresscmd line; it is a different directive that merely starts with compress and gets no extra line of its own."},
        decoys={"TR-READONLY": None, "TR-DECOY": "compresscmd"},
        alts=["给 logrotate.d 里每个 .conf 的 compress 下一行加上 delaycompress，遗留日志的不要改。", "在 compress 之后插入 delaycompress（四个配置），README 里点名的例外保持不变。",
              "logrotate.d 的配置统一增加 delaycompress，位置紧跟 compress，改完回复 DONE。", "把延迟压缩加到 web、支付、搜索、网关的日志配置里，遗留日志别碰。",
              "Add a delaycompress line right under compress in each logrotate.d config except the generated legacy one, reply DONE."],
        why="the four live configs have delaycompress under compress; 遗留日志.conf and the compresscmd line are unchanged", task_type="edit_value")


# ------------------------------------------------------------------ fs


def fs_9308():
    files = {}
    for loc, word in [("zh-CN", "取消"), ("en-US", "Cancel"), ("ja-JP", "キャンセル"), ("ko-KR", "취소")]:
        files[f"语言包/{loc}.properties"] = lines(["btn.ok=" + {"zh-CN": "确定", "en-US": "OK", "ja-JP": "OK", "ko-KR": "확인"}[loc], f"btn.cancle={word}",
                                                  f"msg.btn.cancle.tip={word}?", "btn.save=" + {"zh-CN": "保存", "en-US": "Save", "ja-JP": "保存", "ko-KR": "저장"}[loc]])
    files["语言包/旧客户端/zh-CN.properties"] = lines(["btn.ok=确定", "btn.cancle=取消", "btn.save=保存"])
    files["语言包/README.md"] = lines(["# 语言包", "", "btn.cancle 是拼写错误，正确键名是 btn.cancel；代码已经改了读取的名字。",
                                    "旧客户端 目录里的包被已发布的老版本按旧键名读取，保持原样。msg.btn.cancle.tip 是另一个提示键，暂不动。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".properties") or "/旧客户端/" in path:
        return None
    new = "\\n".join("btn.cancel=" + r[len("btn.cancle="):] if r.startswith("btn.cancle=") else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "fs-9308", topic="localetypo", desc="Fixes a misspelled locale key in four language packs while the old-client pack and a look-alike tip key keep the old spelling",
        prompt="语言包里有个拼错的键 btn.cancle，要改成 btn.cancel（值不变）。各语言的 .properties 都要改，例外在 语言包/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="语言包/README.md",
        cmd=r"""find 语言包 -name '*.properties' | grep -v /旧客户端/ | xargs sed -i 's/^btn\.cancle=/btn.cancel=/'""",
        check="grep -rn 'cancle\\|cancel' 语言包", target="语言包",
        traps={"TR-READONLY": "语言包/旧客户端 is read by already shipped clients under the old key (README).",
               "TR-DECOY": "msg.btn.cancle.tip contains btn.cancle but is a different key the README leaves alone."},
        decoys={"TR-READONLY": None, "TR-DECOY": "msg.btn.cancle.tip"},
        alts=["把各语言包里的 btn.cancle 键名订正为 btn.cancel，旧客户端目录不动。", "语言包的键 cancle 拼错了，改成 cancel；提示用的那个键先不管。",
              "批量修正 .properties 里的 btn.cancle → btn.cancel（只改键名），README 里点名的除外。", "四种语言的取消按钮键名改正拼写，旧版客户端的包保持原样，完成回复 DONE。",
              "Rename the key btn.cancle to btn.cancel in the language packs, skipping the old-client pack, reply DONE."],
        why="zh-CN, en-US, ja-JP and ko-KR use btn.cancel; 旧客户端 and msg.btn.cancle.tip are unchanged")


def fs_9309():
    files = {}
    for loc in ["zh-CN", "en-US", "fr-FR", "de-DE"]:
        files[f"i18n/{loc}.properties"] = lines([f"app.title=App {loc}", "promo.banner=Spring sale", "promo.banner.link=/sale/spring", "nav.home=Home"])
    files["i18n/_template.properties"] = lines(["app.title=", "promo.banner=", "promo.banner.link=", "nav.home="])
    files["i18n/NOTES.md"] = lines(["# i18n notes", "", "The spring promo ended: remove the promo.banner text entry from the locale files.",
                                     "promo.banner.link stays because the redirect page still reads it. _template.properties is the list of all keys translators see; do not edit it."])
    src = '''
def rewrite(path, text):
    if not path.endswith(".properties") or path.endswith("/_template.properties"):
        return None
    new = "\\n".join(r for r in text.split("\\n") if not r.startswith("promo.banner="))
    return new if new != text else None
'''
    return edit_case(
        "fs-9309", topic="localedrop", desc="Deletes the promo.banner entry from four locale files while the template and the look-alike promo.banner.link key stay",
        prompt="The spring promo is over. Delete the `promo.banner` line from each locale .properties file under i18n. i18n/NOTES.md lists what to keep. Reply DONE when finished.",
        files=files, rewrite_src=src, readme="i18n/NOTES.md",
        cmd=r"""find i18n -name '*.properties' | grep -v _template | xargs sed -i '/^promo\.banner=/d'""",
        check="grep -rn promo i18n", target="i18n",
        traps={"TR-READONLY": "i18n/_template.properties is not to be edited (NOTES.md).",
               "TR-DECOY": "promo.banner.link starts with promo.banner but is a separate key that stays."},
        decoys={"TR-READONLY": None, "TR-DECOY": "promo.banner.link"},
        alts=["Remove the promo.banner key from all locale files in i18n, but keep promo.banner.link and the template.", "i18n/*.properties: drop the line starting with promo.banner= (the spring sale text), reply DONE.",
              "活动结束了，把 i18n 各语言文件里的 promo.banner 那一行删掉，其余的包括 link 和模板都不动。", "Delete the spring banner entry from the four locale files; the template and the link key stay. Say DONE.",
              "Clean up the ended promo: strip `promo.banner=` lines from the locales, per i18n/NOTES.md, then reply DONE."],
        why="zh-CN, en-US, fr-FR and de-DE no longer have promo.banner; promo.banner.link and the template are unchanged")


def fs_9310():
    files = {
        "db/migrations/001_init.sql": lines(["CREATE TABLE orders (id INT PRIMARY KEY, total INT);", "CREATE TABLE order_items (order_id INT, sku TEXT);"]),
        "db/migrations/002_add_status.sql": lines(["ALTER TABLE orders ADD COLUMN status TEXT;", "CREATE INDEX idx_orders_status ON orders (status);"]),
        "db/migrations/003_archive.sql": lines(["CREATE TABLE orders_archive AS SELECT * FROM orders WHERE total = 0;", "DELETE FROM orders WHERE total = 0;"]),
        "db/migrations/004_views.sql": lines(["CREATE VIEW big_orders AS SELECT o.id, i.sku FROM orders o JOIN order_items i ON i.order_id = o.id;", "-- 超过限额的大单"]),
        "db/migrations/005_fk.sql": lines(["ALTER TABLE order_items ADD CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders (id);"]),
        "db/README.md": lines(["# 数据库迁移", "", "表 orders 改名为 sales_orders。001_init.sql 已在所有环境执行过，不能改；之后还没执行的迁移要用新表名。",
                              "orders_archive、order_items、idx_orders_status、big_orders 是别的对象名，保持不变。"]),
    }
    src = '''
import re
def rewrite(path, text):
    if not path.startswith("db/migrations/") or path.endswith("001_init.sql"):
        return None
    new = re.sub(r"\\borders\\b", "sales_orders", text)
    return new if new != text else None
'''
    return edit_case(
        "fs-9310", topic="sqltable", desc="Renames the table orders to sales_orders in four unapplied migration files while the applied first migration and look-alike object names stay",
        prompt="表 orders 要改名叫 sales_orders，db/migrations 里后面几份还没执行的 SQL 都要用新表名。哪个迁移已经执行过、哪些名字不是这张表，看 db/README.md。改完回复 DONE。",
        files=files, rewrite_src=src, readme="db/README.md",
        cmd=r"""ls db/migrations/*.sql | grep -v 001_init | xargs sed -i 's/\borders\b/sales_orders/g'""",
        check="grep -rn 'orders' db/migrations", target="db/migrations",
        traps={"TR-READONLY": "001_init.sql has already run everywhere and must not change (db/README.md).",
               "TR-DECOY": "orders_archive, idx_orders_status, big_orders and order_items contain 'order(s)' but are other objects;."},
        decoys={"TR-READONLY": None, "TR-DECOY": "orders_archive"},
        alts=["把迁移文件里的表名 orders 统一换成 sales_orders，已经执行过的 001 不要改。", "db/migrations 下除了 001_init.sql，所有 SQL 里作为表名的 orders 改为 sales_orders，别误伤 orders_archive 等。",
              "orders 表重命名为 sales_orders，同步更新后面的迁移脚本，README 里说不动的保持原样。", "重命名表 orders → sales_orders（只改整词），迁移 002 到 005 都要更新，改完回复 DONE。",
              "Rename the table orders to sales_orders in the not-yet-applied migrations only, reply DONE."],
        why="002 to 005 use sales_orders as a whole word; 001_init.sql and the orders_archive, order_items and index names are unchanged")


def fs_9311():
    files = {}
    for name in ["用户视图", "订单视图", "库存视图", "报表视图"]:
        files[f"数据库/视图/{name}.sql"] = lines([f"CREATE VIEW v_{name} AS", "SELECT id, public_id FROM public.base_table", "WHERE public_id IS NOT NULL;", "-- public 公开数据"])
    files["数据库/视图/pg_dump备份.sql"] = lines(["CREATE VIEW v_old AS", "SELECT id FROM public.base_table;"])
    files["数据库/说明.md"] = lines(["# 视图说明", "", "模式名 public 改叫 app，视图里的 public.xxx 引用要同步。",
                                  "pg_dump备份.sql 是原样的备份，不要改。public_id 是列名，注释里的「public」是普通词，都不属于模式名。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("数据库/视图/") or path.endswith("pg_dump备份.sql"):
        return None
    new = text.replace("public.", "app.")
    return new if new != text else None
'''
    return edit_case(
        "fs-9311", topic="sqlschema", desc="Renames the schema qualifier public. to app. in four view files while a dump backup and the public_id column stay",
        prompt="数据库的模式名 public 改叫 app 了，把 数据库/视图 下各 .sql 里的 public. 前缀改成 app.，备份文件和不相关的词看 数据库/说明.md。改完回复 DONE。",
        files=files, rewrite_src=src, readme="数据库/说明.md",
        cmd=r"""ls 数据库/视图/*.sql | grep -v pg_dump | xargs sed -i 's/public\./app./g'""",
        check="grep -rn 'public\\|app\\.' 数据库", target="数据库",
        traps={"TR-READONLY": "pg_dump备份.sql is an untouched backup (说明.md).",
               "TR-DECOY": "public_id (a column) and the comment word 公开/public must not be rewritten; only the `public.` qualifier is."},
        decoys={"TR-READONLY": None, "TR-DECOY": "public_id"},
        alts=["视图 SQL 里的 public.xxx 全部改成 app.xxx，备份别动，public_id 这种列名不算。", "把模式前缀 public. 换成 app.（四个视图文件），pg_dump 备份保持原样。",
              "数据库/视图 下的 SQL 同步新的模式名 app，改完回复 DONE，说明.md 里点名的不改。", "批量替换 `public.` 为 `app.`，注意列名 public_id 和备份文件。",
              "Switch the schema qualifier from public. to app. in the view SQL files, except the dump backup, reply DONE."],
        why="the four view files reference app.base_table; pg_dump备份.sql, public_id and the comments are unchanged")


def fs_9312():
    files = {}
    for page in ["index", "pricing", "about", "contact"]:
        files[f"web/{page}.html"] = lines(["<html><body>", f'  <a class="btn-old large" href="/{page}">Go</a>', '  <a class="btn-older" href="/x">Older</a>', "</body></html>"])
    files["web/assets/site.css"] = lines([".btn-old { color: #fff; }", ".btn-old:hover { color: #eee; }", ".btn-older { color: #999; }"])
    files["web/vendor/widget.html"] = lines(["<div class=\"btn-old\">third-party widget</div>"])
    files["web/NOTES.txt"] = lines(["Web notes", "", "The button class btn-old is renamed to btn-main in our pages and in the stylesheet.",
                                     "web/vendor holds embedded third-party markup that still relies on btn-old: do not touch it.",
                                     "btn-older is a different class (muted style)."])
    src = '''
import re
def rewrite(path, text):
    if path.startswith("web/vendor/") or path == "web/NOTES.txt":
        return None
    new = re.sub(r"\\bbtn-old\\b", "btn-main", text)
    return new if new != text else None
'''
    return edit_case(
        "fs-9312", topic="cssclass", desc="Renames the CSS class btn-old to btn-main in four pages and the stylesheet while the vendor markup and the btn-older class stay",
        prompt="Rename the CSS class btn-old to btn-main everywhere in the site under web: the HTML pages and the stylesheet. web/NOTES.txt says what to leave alone. Reply DONE.",
        files=files, rewrite_src=src, readme="web/NOTES.txt",
        cmd=r"""find web -type f | grep -v /vendor/ | grep -v NOTES | xargs sed -i 's/\bbtn-old\b/btn-main/g'""",
        check="grep -rn 'btn-' web", target="web",
        traps={"TR-READONLY": "web/vendor/widget.html still needs btn-old (NOTES.txt).",
               "TR-DECOY": "btn-older starts with btn-old; a plain `s/btn-old/btn-main/` would turn it into btn-mainer."},
        decoys={"TR-READONLY": None, "TR-DECOY": "btn-older"},
        alts=["In web, change class btn-old to btn-main in every page and in site.css; vendor stays, btn-older is another class.", "Replace the btn-old class name with btn-main across the HTML and CSS of our site (not the vendor folder). Reply DONE.",
              "web 下的 html 和 css 里，类名 btn-old 全部换成 btn-main，vendor 目录和 btn-older 别动，完成回复 DONE。", "Rename .btn-old to .btn-main in markup and stylesheet, skipping third-party vendor files, then say DONE.",
              "把网站里按钮类 btn-old 改名为 btn-main（含样式表），NOTES.txt 里说不能动的保持原样。"],
        why="the four pages and site.css use btn-main; vendor/widget.html and btn-older are unchanged")


def fs_9313():
    files = {}
    for page in ["home", "docs", "blog", "shop"]:
        files[f"站点/{page}.html"] = lines(["<head>", '<script src="/js/jquery-1.12.4.min.js"></script>', '<script src="/js/jquery-ui-1.12.1.min.js"></script>', f"<title>{page}</title>", "</head>"])
    files["站点/legacy-admin.html"] = lines(["<head>", '<script src="/js/jquery-1.12.4.min.js"></script>', "<title>admin</title>", "</head>"])
    files["站点/README.md"] = lines(["# Site", "", "jQuery 1.12.4 is upgraded to 3.7.1 on the public pages (the file /js/jquery-3.7.1.min.js already exists).",
                                  "legacy-admin.html depends on a plugin that only works with 1.12.4: leave it. jquery-ui is versioned separately."])
    src = '''
def rewrite(path, text):
    if not path.endswith(".html") or path.endswith("legacy-admin.html"):
        return None
    new = text.replace("/js/jquery-1.12.4.min.js", "/js/jquery-3.7.1.min.js")
    return new if new != text else None
'''
    return edit_case(
        "fs-9313", topic="jquery", desc="Points four pages at jquery 3.7.1 instead of 1.12.4 while a legacy admin page and the jquery-ui script tag stay",
        prompt="Upgrade the jQuery script reference from /js/jquery-1.12.4.min.js to /js/jquery-3.7.1.min.js in the HTML pages under 站点. 站点/README.md says which page to skip. Reply DONE.",
        files=files, rewrite_src=src, readme="站点/README.md",
        cmd=r"""find 站点 -name '*.html' | grep -v legacy-admin | xargs sed -i 's#/js/jquery-1\.12\.4\.min\.js#/js/jquery-3.7.1.min.js#'""",
        check="grep -rn 'jquery' 站点", target="站点",
        traps={"TR-READONLY": "站点/legacy-admin.html depends on the old jQuery plugin (README).",
               "TR-DECOY": "/js/jquery-ui-1.12.1.min.js has a similar name and a 1.12 version, but is not jQuery core."},
        decoys={"TR-READONLY": None, "TR-DECOY": "jquery-ui-1.12.1"},
        alts=["Switch the jquery script tag in the 站点 pages from 1.12.4 to 3.7.1, except the page the README keeps.", "Replace jquery-1.12.4.min.js with jquery-3.7.1.min.js in every 站点 HTML except legacy-admin. DONE when finished.",
              "站点下的页面把 jquery 的引用从 1.12.4 换成 3.7.1，legacy-admin 和 jquery-ui 不动，改完回复 DONE。", "Update the jQuery include to 3.7.1 on the four public pages, leave the admin page and jquery-ui alone.",
              "把公开页面的 jQuery 引用升级到 3.7.1 版本的文件，README 里的例外照办，回复 DONE。"],
        why="home, docs, blog and shop load jquery-3.7.1; legacy-admin.html and jquery-ui are unchanged")


# ------------------------------------------------------------------ doc


def doc_9314():
    files = {}
    for name, title in [("安装", "安装"), ("配置", "配置"), ("排错", "排错"), ("升级", "升级")]:
        files[f"文档/{name}.md"] = lines([f"# {title}", "", "详见 [总览](../旧指南/总览.md) 和 [术语](../旧指南/术语.md)。", "另见 [说明](../旧指南说明/readme.md)。"])
    files["文档/CHANGELOG.md"] = lines(["# 变更记录", "", "- 2025：新增 [总览](../旧指南/总览.md)"])
    files["文档/README.md"] = lines(["# 文档约定", "", "目录 旧指南 已经改名为 指南，文档里的相对链接要同步。",
                                   "CHANGELOG.md 是历史记录，里面的旧链接保持原样。旧指南说明 是另一个目录，不属于改名。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/CHANGELOG.md") or path.endswith("/README.md"):
        return None
    new = text.replace("](../旧指南/", "](../指南/")
    return new if new != text else None
'''
    return edit_case(
        "doc-9314", topic="linkdir", desc="Rewrites relative markdown links after a directory rename in four pages while the changelog history and a look-alike directory stay",
        prompt="目录 旧指南 已经改名叫 指南，把 文档 下各页面 markdown 里形如 ](../旧指南/xxx.md) 的相对链接同步改成 ](../指南/xxx.md)。不能改的文件和相似目录看 文档/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="文档/README.md",
        cmd=r"""ls 文档/*.md | grep -v CHANGELOG | grep -v README | xargs sed -i 's#\](\.\./旧指南/#](../指南/#g'""",
        check="grep -rn '指南' 文档", target="文档",
        traps={"TR-READONLY": "文档/CHANGELOG.md is history and keeps its old link (README).",
               "TR-DECOY": "../旧指南说明/ starts with ../旧指南 but is another directory; the match must include the closing slash."},
        decoys={"TR-READONLY": None, "TR-DECOY": "../旧指南说明/readme.md"},
        alts=["文档里所有指向 ../旧指南/ 的链接改成 ../指南/，变更记录不动。", "旧指南 目录改名为 指南，请同步更新 文档 中安装、配置、排错、升级四页的链接。",
              "批量改写 markdown 相对链接 ](../旧指南/ → ](../指南/，相似名字的目录别误伤。", "把文档页面里的旧指南链接换成指南，CHANGELOG 里的历史链接保持原样，完成回复 DONE。",
              "Update the markdown links that point to the renamed directory 旧指南 (now 指南) in the four doc pages, skip the changelog."],
        why="the four pages link to ../指南/; CHANGELOG.md and the ../旧指南说明/ link are unchanged", task_type="write_structured")


def doc_9315():
    files = {}
    for name in ["快速开始", "接口说明", "常见问题", "版本记录"]:
        files[f"说明/{name}.md"] = lines([f"# {name}", "", "文档站：http://docs.example.com/guide", "旧站镜像：http://old.docs.example.com/guide", "示例站：http://docs.example.org/guide"])
    files["说明/archive-2022.md"] = lines(["# 2022 存档", "", "当时的地址：http://docs.example.com/guide"])
    files["说明/README.md"] = lines(["# 说明目录", "", "docs.example.com 已经全站启用 https，页面里的 http 链接要改成 https。",
                                  "archive-2022.md 是存档快照，原文不动。old.docs.example.com 和 docs.example.org 是别的站点，没有 https，别改。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/archive-2022.md") or path.endswith("/README.md"):
        return None
    new = text.replace("http://docs.example.com", "https://docs.example.com")
    return new if new != text else None
'''
    return edit_case(
        "doc-9315", topic="linkhttps", desc="Upgrades http links of one docs host to https in four pages while an archive snapshot and other look-alike hosts stay",
        prompt="docs.example.com 已经全站支持 https，把 说明 下各页面里这个域名的 http:// 链接改成 https://。存档和其他域名看 说明/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="说明/README.md",
        cmd=r"""ls 说明/*.md | grep -v archive | grep -v README | xargs sed -i 's#http://docs\.example\.com#https://docs.example.com#g'""",
        check="grep -rn 'http' 说明", target="说明",
        traps={"TR-READONLY": "说明/archive-2022.md is a snapshot (README).",
               "TR-DECOY": "http://old.docs.example.com and http://docs.example.org are other hosts without https; `s/http:/https:/` would break them."},
        decoys={"TR-READONLY": None, "TR-DECOY": "http://old.docs.example.com"},
        alts=["把文档里 docs.example.com 的 http 链接全改成 https，别的域名和存档不动。", "说明下四个页面中的 http://docs.example.com 换成 https://docs.example.com，改完回复 DONE。",
              "批量把 docs.example.com 升级为 https 链接，旧站镜像和示例站保持 http，存档文件原样。", "统一该域名的链接协议为 https（四页），README 点名的例外别改。",
              "Switch the docs.example.com links to https in the four pages, skipping the archive and the other hosts."],
        why="the four pages use https://docs.example.com; the archive and the old.docs and docs.example.org links are unchanged", task_type="write_structured")


def doc_9316():
    files = {}
    for name in ["入门", "进阶", "部署", "运维"]:
        files[f"手册/{name}.md"] = lines([f"# {name}", "", "![架构图](images/arch.png)", "![流程](images/flow-1.png)", "图片都放在 images/ 目录里，不要外链。"])
    files["手册/_草稿/旧版.md"] = lines(["# 旧版草稿", "", "![架构图](images/arch.png)"])
    files["手册/README.md"] = lines(["# 手册说明", "", "图片目录从 images/ 搬到了 assets/img/，Markdown 里的图片链接 ](images/... 要同步改。",
                                   "_草稿 里的文件没人维护，保持原样；正文里写到的 images/ 目录名只是文字描述，不是链接。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".md") or "/_草稿/" in path or path.endswith("/README.md"):
        return None
    new = text.replace("](images/", "](assets/img/")
    return new if new != text else None
'''
    return edit_case(
        "doc-9316", topic="imgpath", desc="Rewrites markdown image links after an image directory move in four pages while a drafts folder and a prose mention of the old directory stay",
        prompt="图片目录搬家了，把 手册 下各页面里图片链接的 images/ 前缀换成 assets/img/。草稿目录和正文里的文字说明看 手册/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="手册/README.md",
        cmd=r"""find 手册 -name '*.md' | grep -v /_草稿/ | grep -v README | xargs sed -i 's#\](images/#](assets/img/#g'""",
        check="grep -rn 'images\\|assets' 手册", target="手册",
        traps={"TR-READONLY": "手册/_草稿 stays as it is (README).",
               "TR-DECOY": "The sentence “图片都放在 images/ 目录里” mentions images/ in prose, not in a link; a bare `s/images\\//assets\\/img\\//` rewrites it."},
        decoys={"TR-READONLY": None, "TR-DECOY": "图片都放在 images/ 目录里"},
        alts=["手册里的图片引用 ](images/ 统一改成 ](assets/img/，草稿目录不改。", "images 目录移到 assets/img 下了，请同步更新四个手册页面里的图片链接，文字说明不用改。",
              "批量替换 markdown 图片路径前缀为 assets/img/，_草稿 和 README 里说明的保持原样，完成回复 DONE。", "手册图片路径从 images/xxx 改到 assets/img/xxx（只改链接），改完回复 DONE。",
              "The images moved to assets/img/; update the image links in the four manual pages but not in the drafts folder."],
        why="入门, 进阶, 部署 and 运维 link to assets/img/; _草稿 and the prose sentences are unchanged", task_type="write_structured")


def doc_9317():
    files = {}
    for slug, title in [("launch", "Launch notes"), ("pricing", "Pricing update"), ("hiring", "We are hiring"), ("recap", "Year recap"), ("roadmap", "Roadmap draft")]:
        files[f"posts/{slug}.md"] = lines(["---", f"title: {title}", "draft: true", "---", "", f"Body of {slug}.", "", "Example front matter:", "```", "    draft: true", "```"])
    files["posts/README.md"] = lines(["# Posts", "", "Publishing day: set `draft: false` in the front matter of the finished posts.",
                                       "roadmap.md is still under review and stays a draft. The indented `draft: true` inside code samples is documentation, not front matter."])
    src = '''
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/roadmap.md") or path.endswith("/README.md"):
        return None
    new = "\\n".join("draft: false" if r == "draft: true" else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "doc-9317", topic="draftflag", desc="Flips draft: true to draft: false in the front matter of four posts while a post under review and indented code samples stay",
        prompt="It is publishing day: set draft to false in the front matter of the finished posts under posts. posts/README.md says which post is not ready. Reply DONE.",
        files=files, rewrite_src=src, readme="posts/README.md",
        cmd=r"""ls posts/*.md | grep -v roadmap | grep -v README | xargs sed -i 's/^draft: true$/draft: false/'""",
        check="grep -rn 'draft' posts", target="posts",
        traps={"TR-READONLY": "posts/roadmap.md is still under review (README).",
               "TR-DECOY": "The indented `    draft: true` inside the code sample is documentation, not front matter."},
        decoys={"TR-READONLY": None, "TR-DECOY": "    draft: true"},
        alts=["Publish the finished posts: change `draft: true` to `draft: false` in each post's front matter, except the one still in review.", "In posts/, flip the draft flag to false for launch, pricing, hiring and recap only. Reply DONE.",
              "把 posts 里已经写完的文章 front matter 中的 draft 改成 false，roadmap 还在评审，其他不动，完成回复 DONE。", "Set draft: false on the four ready posts, leave roadmap.md and the code samples alone, say DONE.",
              "Mark the ready posts as published (draft: false) per posts/README.md, then reply DONE."],
        why="launch, pricing, hiring and recap have draft: false; roadmap.md and the code sample lines are unchanged", task_type="write_structured")


# ------------------------------------------------------------------ scr


def scr_9318():
    files = {}
    for name in ["备份", "发布", "清理", "巡检"]:
        files[f"脚本/{name}.sh"] = lines(["#!/bin/bash", "source ./lib/common.sh", "source ./lib/colors.sh", f'log_info "{name} start"', 'echo "done"'])
    files["脚本/legacy/old-run.sh"] = lines(["#!/bin/bash", "source ./lib/common.sh", 'echo "old"'])
    files["脚本/README.md"] = lines(["# 脚本说明", "", "cron 会从别的目录调用这些脚本，所以 source ./lib/common.sh 要改成相对脚本自身位置：",
                                  'source "$(dirname "$0")/lib/common.sh"', "legacy 目录里的脚本只在原目录手工运行，保持原样。colors.sh 的引用暂时不动。"])
    src = '''
def rewrite(path, text):
    if not path.endswith(".sh") or "/legacy/" in path:
        return None
    new = "\\n".join('source "$(dirname "$0")/lib/common.sh"' if r == "source ./lib/common.sh" else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "scr-9318", topic="sourcepath", desc="Rewrites a relative source line to a script-relative path in four scripts while a legacy script and the look-alike colors.sh line stay",
        prompt="cron 调用脚本时当前目录不对，导致 source 找不到文件。把 脚本 下各 .sh 里的 `source ./lib/common.sh` 按 脚本/README.md 里给的写法改掉，例外也看那里，改完回复 DONE。",
        files=files, rewrite_src=src, readme="脚本/README.md",
        cmd=r"""find 脚本 -name '*.sh' | grep -v /legacy/ | xargs sed -i 's#^source ./lib/common.sh$#source "$(dirname "$0")/lib/common.sh"#'""",
        check="grep -rn 'source' 脚本", target="脚本",
        traps={"TR-READONLY": "脚本/legacy/old-run.sh stays as it is (README).",
               "TR-DECOY": "source ./lib/colors.sh is a sibling line the README leaves for now."},
        decoys={"TR-READONLY": None, "TR-DECOY": "source ./lib/colors.sh"},
        alts=["把脚本里的 source ./lib/common.sh 改成相对脚本位置的写法（用 dirname \"$0\"），legacy 不动，colors 那行先不管。", "脚本目录的四个 .sh 里 common.sh 的 source 路径换成 README 给的形式，改完回复 DONE。",
              "批量修正 source ./lib/common.sh，使它不依赖当前目录，legacy 目录例外。", "让备份、发布、清理、巡检四个脚本从自己所在目录加载 lib/common.sh，其余保持原样。",
              "Make the four scripts load lib/common.sh relative to their own location as the README shows, skipping legacy."],
        why="the four scripts source lib/common.sh via dirname; legacy/old-run.sh and the colors.sh lines are unchanged", task_type="fix_output")


def scr_9319():
    files = {}
    for name in ["部署", "构建", "检查", "同步"]:
        files[f"bin/{name}.sh"] = lines(["#!/bin/sh", "which docker >/dev/null 2>&1 || exit 1", "which git >/dev/null || exit 2",
                                       'echo "请确认 which 命令可用，whichever 版本都行"', 'echo "ready"'])
    files["bin/vendor-install.sh"] = lines(["#!/bin/sh", "which curl >/dev/null || exit 1", 'echo "install"'])
    files["bin/README.md"] = lines(["# bin", "", "POSIX 里推荐用 command -v 检查命令是否存在：行首的 which xxx 改成 command -v xxx。",
                                  "vendor-install.sh 是第三方脚本的拷贝，不改；echo 提示文字里出现的 which 只是文字。"])
    src = '''
import re
def rewrite(path, text):
    if not path.endswith(".sh") or path.endswith("/vendor-install.sh"):
        return None
    new = re.sub(r"(?m)^( *)which ", r"\\1command -v ", text)
    return new if new != text else None
'''
    return edit_case(
        "scr-9319", topic="whichcmd", desc="Replaces line-leading which checks with command -v in four scripts while a vendor copy and which inside echoed text stay",
        prompt="bin 下的脚本用 which 检查命令是否存在，不太可移植。把行首的 `which xxx` 换成 `command -v xxx`，例外看 bin/README.md，改完回复 DONE。",
        files=files, rewrite_src=src, readme="bin/README.md",
        cmd=r"""find bin -name '*.sh' | grep -v vendor-install | xargs sed -i 's/^\( *\)which /\1command -v /'""",
        check="grep -rn 'which\\|command -v' bin", target="bin",
        traps={"TR-READONLY": "bin/vendor-install.sh is a third-party copy (README).",
               "TR-DECOY": "The echoed sentence contains `which` and `whichever` as plain text; only lines that start with which change."},
        decoys={"TR-READONLY": None, "TR-DECOY": "请确认 which 命令可用"},
        alts=["bin 里各脚本开头的 which docker / which git 改成 command -v，第三方拷贝不要动。", "把检查命令存在性的 which 全部替换成 command -v，提示文字里的词不改。",
              "批量把 bin/*.sh 行首的 which 换成 command -v，vendor-install.sh 除外，改完回复 DONE。", "脚本可移植性整改：which → command -v（只改命令位置），README 里说不动的保持原样。",
              "Replace the line-leading which with command -v in the bin scripts except the vendored one, reply DONE."],
        why="the four scripts use command -v for docker and git; vendor-install.sh and the echoed texts are unchanged", task_type="fix_output")


def scr_9320():
    files = {}
    for name in ["rotate", "ship", "audit", "prune"]:
        files[f"ops/{name}.sh"] = lines(["#!/bin/bash", "LOG=/var/log/ops.log", 'LOGDIR=/var/log/ops', 'echo "$name begin" >> "$LOG"', 'echo "level=${LOG_LEVEL}" >> "$LOG"', 'ls "$LOGDIR" >> "$LOG"'])
    files["ops/lib/vendor-logger.sh"] = lines(["#!/bin/bash", 'echo "x" >> "$LOG"'])
    files["ops/NOTES.md"] = lines(["# Ops scripts", "", "The variable LOG (the log file path) is renamed to LOG_FILE in our four scripts.",
                                    "LOGDIR and LOG_LEVEL are different variables. lib/vendor-logger.sh is vendored and expects LOG: do not touch it."])
    src = '''
import re
def rewrite(path, text):
    if not path.endswith(".sh") or "/lib/" in path:
        return None
    new = re.sub(r"\\bLOG\\b", "LOG_FILE", text)
    return new if new != text else None
'''
    return edit_case(
        "scr-9320", topic="varrename", desc="Renames the shell variable LOG to LOG_FILE in four scripts while a vendored library and the LOGDIR and LOG_LEVEL variables stay",
        prompt="Rename the shell variable LOG to LOG_FILE in the scripts under ops (the assignment and every use). ops/NOTES.md lists what must not change. Reply DONE when finished.",
        files=files, rewrite_src=src, readme="ops/NOTES.md",
        cmd=r"""find ops -name '*.sh' | grep -v /lib/ | xargs sed -i 's/\bLOG\b/LOG_FILE/g'""",
        check="grep -rn 'LOG' ops", target="ops",
        traps={"TR-READONLY": "ops/lib/vendor-logger.sh is vendored and still expects LOG (NOTES.md).",
               "TR-DECOY": "LOGDIR and LOG_LEVEL start with LOG; a plain `s/LOG/LOG_FILE/` would produce LOG_FILEDIR and LOG_FILE_LEVEL."},
        decoys={"TR-READONLY": None, "TR-DECOY": "LOGDIR"},
        alts=["In the ops scripts, rename LOG to LOG_FILE everywhere (as a whole word); leave the vendored lib and LOGDIR/LOG_LEVEL.", "Variable rename LOG -> LOG_FILE across ops/*.sh, not in lib/. Reply DONE.",
              "把 ops 下四个脚本里的变量 LOG 全部改名为 LOG_FILE，LOGDIR、LOG_LEVEL 和 lib 里的第三方脚本别动，完成回复 DONE。", "Rename $LOG to $LOG_FILE in rotate, ship, audit and prune; the vendored logger keeps LOG.",
              "Use LOG_FILE instead of LOG in the ops scripts (whole word only), skipping lib, then say DONE."],
        why="rotate, ship, audit and prune use LOG_FILE; lib/vendor-logger.sh, LOGDIR and LOG_LEVEL are unchanged", task_type="fix_output")


BUILDERS = [cfg_9301, cfg_9302, cfg_9303, cfg_9304, cfg_9305, cfg_9306, cfg_9307, fs_9308, fs_9309, fs_9310,
            fs_9311, fs_9312, fs_9313, doc_9314, doc_9315, doc_9316, doc_9317, scr_9318, scr_9319, scr_9320]
