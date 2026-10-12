"""M9 (bash) breadth batch b12g of v1.41: ids 9161-9180.

M9b bulk edits (6, each with a protected look-alike), M9a aggregations (5, exact-match decoy),
M9d missing-command recovery (4: python3, bc, sqlite3, perl are absent in the sandbox),
M9e bash offered but not the right tool (5). One scalar or one bounded edit per question; the
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
    if "LINES = " not in verify:
        guard = "LINES = %r\nfor _p, _n in LINES.items():\n    assert len(case[\"files\"][_p].splitlines()) == _n, _p\n" % {p: len(t.splitlines()) for p, t in files.items()}
        verify = verify.replace('case = json.load(open("case.json"))\n', 'case = json.load(open("case.json"))\n' + guard, 1)
    return _write_case(cid, files=files, verify=verify, **kw)


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


def thousands(value):
    whole, _, frac = value.partition(".")
    grouped = f"{int(whole):,}" + ("." + frac if frac else "")
    return [value] if grouped == value else [value, grouped]


def literal_free(files, value):
    return not any(str(value) in text for text in files.values())


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
            text = open(full, encoding="utf-8").read()
            if text != want:
                return "%s = %r" % (path, text[:200])
        return None
    return check


def rules_for(files, final):
    out = {}
    for path, text in files.items():
        out[path] = {"unchanged": True} if final[path] == text else {"equals": final[path]}
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
Only the files and lines the README allows change, every other byte stays identical.
""" + phrasings(*alts)
    REFS[cid] = (files, [cmd, check], files_check(rules, files))
    _SPEC[cid] = dict(kind="bash_edit", sub="M9b", targets=[target])
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12g-{topic}-01", level=level, ref_calls=2,
        traps=list(traps), decoys=decoys, axes=["CON", "OBS"], files=files, verify=verify, notes=notes,
        case_expect={"files": rules},
        turns=[{"prompt": prompt, "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


# ------------------------------------------------------------------ M9b bulk edits


def cfg_9161():
    rng = Random(9161)
    files = {}
    for svc in ["api", "web", "worker", "cron", "mailer"]:
        rows = ["[server]", f"port = {rng.choice([8080, 8081, 9000, 9100, 7000])}", f"timeout = {rng.choice([15, 20, 30, 45, 60])}",
                f"connect_timeout = {rng.choice([2, 3, 5])}"]
        if svc in ("web", "cron"):
            rows.append("timeout_retries = 3")
        rows += ["[log]", "level = info"]
        files[f"conf/{svc}.ini"] = lines(rows)
    files["conf/local.ini"] = lines(["[server]", "port = 8999", "timeout = 90", "connect_timeout = 10", "[log]", "level = debug"])
    files["conf/README.md"] = lines(["# 配置说明", "", "每个服务一个 .ini。local.ini 是开发者个人的覆盖配置，不共享，保持原样。",
                                      "connect_timeout 和 timeout_retries 是另外的配置项，不属于这次改名。"])
    src = '''
def rewrite(path, text):
    if not path.startswith("conf/") or not path.endswith(".ini") or path == "conf/local.ini":
        return None
    new = "\\n".join("request_timeout = " + r[len("timeout = "):] if r.startswith("timeout = ") else r for r in text.split("\\n"))
    return new if new != text else None
'''
    return edit_case(
        "cfg-9161", topic="timeoutrename", desc="Renames the timeout key to request_timeout in five service ini files while a personal local.ini and look-alike timeout keys stay",
        prompt="conf 目录下各服务 .ini 里的 timeout 键要改名叫 request_timeout，值不变。哪些文件和配置项不动，conf/README.md 里有说明。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="conf/README.md",
        cmd=r"""find conf -name '*.ini' | grep -v local.ini | xargs sed -i 's/^timeout = /request_timeout = /'""",
        check="grep -rn timeout conf", target="conf",
        traps={"TR-READONLY": "conf/local.ini is a personal override (conf/README.md) and keeps timeout = 90.",
               "TR-DECOY": "connect_timeout and timeout_retries are look-alike keys; a prefix-less `s/timeout/request_timeout/` would rewrite them too."},
        decoys={"TR-READONLY": None, "TR-DECOY": "connect_timeout"},
        alts=["把 conf 里每个服务配置中的 timeout 改名为 request_timeout，别动 README 里点名的文件。",
              "conf 下的 ini 文件，timeout 这个键统一重命名成 request_timeout，然后确认一下并回复 DONE。",
              "服务配置里的 timeout 项改叫 request_timeout（只改键名），按 conf/README.md 的说明跳过不该改的，改完说一声 DONE。",
              "请在 conf 目录的 .ini 中把 timeout 键重命名为 request_timeout，注意 connect_timeout 之类的不要碰，完成后回复 DONE。",
              "批量把 conf/*.ini 里的 timeout 键名换成 request_timeout，个人覆盖文件除外，检查后回复 DONE。"],
        why="the five service files now use request_timeout; local.ini, connect_timeout and timeout_retries are untouched", task_type="edit_value")


def cfg_9162():
    rng = Random(9162)
    files = {}
    for name in ["api", "web", "batch", "edge", "test"]:
        rows = ["[server]", f"bind = 0.0.0.0:{rng.choice([8080, 8443, 9000, 9090])}", "[pool]", f"size = {rng.choice([8, 16, 32])}"]
        if name in ("api", "edge", "test"):
            rows += ["[pool-replica]", f"size = {rng.choice([2, 4])}"]
        rows += ["[log]", f"level = {rng.choice(['info', 'warn'])}"]
        files[f"settings/{name}.cfg"] = lines(rows)
    files["settings/README.txt"] = lines(["Settings notes", "",
                                           "test.cfg is regenerated by CI on every run: do not edit it by hand.",
                                           "[pool-replica] is a separate section with its own limits."])
    src = '''
def rewrite(path, text):
    if not path.startswith("settings/") or not path.endswith(".cfg") or path == "settings/test.cfg":
        return None
    rows = []
    for r in text.split("\\n"):
        rows.append(r)
        if r == "[pool]":
            rows.append("max_idle = 20")
    new = "\\n".join(rows)
    return new if new != text else None
'''
    return edit_case(
        "cfg-9162", topic="maxidle", desc="Inserts a max_idle line directly below the [pool] header in four cfg files while a CI-generated file and a look-alike pool-replica section are left alone",
        prompt="Add the line `max_idle = 20` directly below the `[pool]` header in each .cfg file under settings. settings/README.txt says what to leave alone. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="settings/README.txt",
        cmd=r"""find settings -name '*.cfg' | grep -v test.cfg | xargs sed -i '/^\[pool\]$/a max_idle = 20'""",
        check="grep -rn -A1 'pool' settings", target="settings",
        traps={"TR-READONLY": "settings/test.cfg is regenerated by CI (settings/README.txt).",
               "TR-DECOY": "[pool-replica] looks like [pool]; only the exact [pool] header gets the new line."},
        decoys={"TR-READONLY": None, "TR-DECOY": "[pool-replica]"},
        alts=["In every settings/*.cfg, put `max_idle = 20` on the line right after [pool]. Skip anything the README protects, verify, and say DONE.",
              "Insert max_idle = 20 immediately under the [pool] section header of the cfg files in settings, then confirm and reply DONE.",
              "settings 下的 .cfg 文件，在 [pool] 这一行下面加一行 max_idle = 20，README 里禁止改的除外，改完检查并回复 DONE。",
              "Please append `max_idle = 20` as the first line of each [pool] section in settings/*.cfg (leave the file README.txt marks), check it, reply DONE.",
              "For the cfg files in settings, add max_idle = 20 below [pool]; do not touch the CI-generated one. Reply DONE once checked."],
        why="four cfg files gained max_idle = 20 below their [pool] header; test.cfg and the [pool-replica] sections are unchanged", task_type="edit_value")


def fs_9163():
    rng = Random(9163)
    files = {}
    for region in ["east", "west", "north"]:
        rows = ["date;store;sku;qty;note"]
        for _ in range(rng.randint(8, 12)):
            rows.append(f"2026-09-{rng.randint(1, 28):02d};{rng.choice(['S01', 'S02', 'S07'])};{rng.choice(['K-100', 'K-205', 'M-310'])};{rng.randint(1, 60)};{rng.choice(['ok', 'rush', 'backorder'])}")
        files[f"exports/{region}.csv"] = lines(rows)
    files["exports/raw/vendor-2026-09.csv"] = lines(["date;store;sku;qty;note", "2026-09-03;S01;K-100;12;ok", "2026-09-04;S02;M-310;7;rush"])
    files["exports/east.csv.old"] = lines(["date;store;sku;qty;note", "2026-08-30;S01;K-100;4;ok"])
    files["exports/README.md"] = lines(["# 导出说明", "", "下游工具只认逗号分隔的 .csv。exports/raw/ 是供应商的原始文件，必须保持分号分隔，不要改。",
                                         "以 .old 结尾的是旧备份，不属于导出文件。"])
    src = '''
def rewrite(path, text):
    if path.startswith("exports/") and path.endswith(".csv") and not path.startswith("exports/raw/"):
        return text.replace(";", ",")
    return None
'''
    return edit_case(
        "fs-9163", topic="semicolon", desc="Converts three exported tables from semicolon to comma delimiters while the vendor raw folder and an .old backup keep their format",
        prompt="把 exports 里的 .csv 从分号分隔改成逗号分隔，文件名不变。哪些不能动，exports/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="exports/README.md",
        cmd=r"""find exports -name '*.csv' | grep -v /raw/ | xargs sed -i 's/;/,/g'""",
        check="grep -rc ';' exports", target="exports",
        traps={"TR-READONLY": "exports/raw/ keeps the vendor's semicolons (exports/README.md).",
               "TR-DECOY": "east.csv.old is a backup whose name merely contains .csv; it stays semicolon-delimited."},
        decoys={"TR-READONLY": None, "TR-DECOY": "east.csv.old"},
        alts=["exports 目录下的 .csv 统一换成逗号分隔（原来是分号），按 README 的说明跳过不该动的，检查后回复 DONE。",
              "请把 exports/*.csv 的分隔符 ; 改成 ,，原始文件夹不要碰，改完确认并回复 DONE。",
              "下游只认逗号，帮我把 exports 里的导出文件从分号分隔转成逗号分隔，README 里标了保持原样的除外，完成后回复 DONE。",
              "exports 里的表格文件分隔符换成逗号，文件名别变，备份和供应商原件不动，核对后回复 DONE。",
              "转换 exports 下 .csv 的分隔符（; 变 ,），exports/README.md 提到的例外保持原样，然后检查并回复 DONE。"],
        why="the three export tables are comma-delimited; raw/ and the .old backup still use semicolons")


def doc_9164():
    names = {"入职": "新员工第一天到人事处报到。", "报销": "出差报销须在回来后十天内提交。", "考勤": "迟到三次记一次旷工。",
             "安全": "离开工位必须锁屏。"}
    files = {}
    for n, sentence in names.items():
        files[f"手册/{n}.txt"] = lines([n + "制度", "", sentence, "详情咨询行政部。"])
    files["手册/分公司/北京.txt"] = lines(["北京分公司补充规定", "", "北京办公室周五下午四点关门。"])
    files["手册/归档/2024.txt"] = lines(["2024 版手册（已作废）", "", "仅供查阅。"])
    files["手册/考勤.txt.bak"] = lines(["考勤制度（旧）", "", "迟到两次记一次旷工。"])
    files["手册/README.md"] = lines(["# 手册说明", "", "给手册里的正式 .txt 文件加保密抬头。手册/归档 里是已作废的旧版本，保持原样。",
                                      "以 .bak 结尾的是编辑器留下的备份，不属于手册。"])
    src = '''
def rewrite(path, text):
    if path.startswith("手册/") and path.endswith(".txt") and not path.startswith("手册/归档/"):
        return "内部资料，禁止外传\\n" + text
    return None
'''
    return edit_case(
        "doc-9164", topic="confhead", desc="Adds a confidentiality header as the first line of every handbook txt including a subfolder while the archive and a .bak backup stay unchanged",
        prompt="给 手册 里每个 .txt 文件的最前面加一行「内部资料，禁止外传」，包括子目录里的。哪些不加，手册/README.md 里有说明。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="手册/README.md",
        cmd=r"""find 手册 -name '*.txt' | grep -v /归档/ | xargs sed -i '1i 内部资料，禁止外传'""",
        check="head -n 1 手册/*.txt 手册/分公司/*.txt", target="手册",
        traps={"TR-READONLY": "手册/归档 holds withdrawn old versions and stays as it is (手册/README.md).",
               "TR-DECOY": "考勤.txt.bak is an editor backup, not a handbook page; it ends in .bak, not .txt."},
        decoys={"TR-READONLY": None, "TR-DECOY": "考勤.txt.bak"},
        alts=["手册目录（含子目录）里的 .txt 文件，开头统一插入一行「内部资料，禁止外传」，作废的归档版本除外，检查后回复 DONE。",
              "在 手册 下每份 .txt 的第一行加上保密抬头「内部资料，禁止外传」，README 里说不改的别改，完成后回复 DONE。",
              "请为 手册 里的正式文本文件添加首行「内部资料，禁止外传」，备份文件和归档不要碰，改完核对并回复 DONE。",
              "每个 手册/**/*.txt（归档目录除外）都在最前面插一行「内部资料，禁止外传」，然后确认并回复 DONE。",
              "给手册加保密抬头：把「内部资料，禁止外传」放在每个 .txt 的第一行，遵守 手册/README.md 的例外，检查完回复 DONE。"],
        why="the five handbook pages (including 北京.txt) start with the header; the archive and the .bak are unchanged", task_type="write_structured")


def fs_9165():
    def noisy(rows, marks):
        return lines([r + marks.get(i, "") for i, r in enumerate(rows)])
    files = {
        "src/app/main.py": noisy(["import sys", "", "def main():", "    print('start')", "    return 0", "", "if __name__ == '__main__':", "    sys.exit(main())"], {3: "  ", 4: "\t"}),
        "src/app/cli.py": noisy(["import argparse", "", "def parse():", "    p = argparse.ArgumentParser()", "    p.add_argument('--n')", "    return p.parse_args()"], {0: " ", 4: "   "}),
        "src/lib/util.py": noisy(["def clamp(x, lo, hi):", "    if x < lo:", "        return lo", "    if x > hi:", "        return hi", "    return x"], {2: "    ", 5: " "}),
        "src/lib/models.py": noisy(["class User:", "    def __init__(self, name):", "        self.name = name", "", "    def greet(self):", "        return 'hi ' + self.name"], {0: " ", 3: "  ", 5: "\t"}),
        "src/vendor/six.py": noisy(["# vendored, do not reformat", "PY3 = True", "def u(s):", "    return s"], {1: "  ", 3: " "}),
        "src/snippets/demo.py.txt": noisy(["# snippet for the docs", "x = 1", "print(x)"], {1: "   "}),
        "src/README.txt": lines(["Source notes", "", "src/vendor/ is third-party code kept byte-for-byte; never reformat it.",
                                  "snippets/*.py.txt are documentation samples, not modules."]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("src/") and path.endswith(".py") and not path.startswith("src/vendor/"):
        new = "\\n".join(r.rstrip(" \\t") for r in text.split("\\n"))
        return new if new != text else None
    return None
'''
    return edit_case(
        "fs-9165", topic="trimws", desc="Strips trailing whitespace from the Python modules of a source tree while a vendored folder and a .py.txt sample keep theirs",
        prompt="Strip the trailing whitespace from every .py file under src. src/README.txt lists what must stay byte-for-byte. Check the result and reply DONE.",
        files=files, rewrite_src=src, readme="src/README.txt",
        cmd=r"""find src -name '*.py' | grep -v /vendor/ | xargs sed -i 's/[[:space:]]*$//'""",
        check="grep -rlE '[[:space:]]$' src", target="src",
        traps={"TR-READONLY": "src/vendor/six.py is third-party code kept byte-for-byte (src/README.txt).",
               "TR-DECOY": "src/snippets/demo.py.txt is a documentation sample whose name contains .py but is not a module."},
        decoys={"TR-READONLY": None, "TR-DECOY": "demo.py.txt"},
        alts=["Remove trailing spaces and tabs from all Python modules in src, but leave the vendored copy and the doc samples as they are. Verify, then reply DONE.",
              "Trim line-end whitespace in src/**/*.py (not src/vendor), check afterwards that none is left in the files you touched, and reply DONE.",
              "Clean up trailing whitespace across the .py files in src; src/README.txt names the exceptions. Confirm and say DONE.",
              "Please strip trailing blanks from each .py under src except the third-party folder, double-check, and reply DONE.",
              "src 里所有 .py 文件行尾的空格和制表符去掉，README.txt 里说保持原样的别动，检查后回复 DONE。"],
        why="the four modules have no trailing whitespace; vendor/six.py and demo.py.txt are unchanged")


def cfg_9166():
    def sh(body):
        return lines(["#!/bin/sh"] + body)
    files = {
        "scripts/backup.sh": sh(["/opt/old-app/bin/backup --dest /opt/old-app-data/backups", "# config lives in /opt/old-app/conf", "echo done"]),
        "scripts/deploy.sh": sh(["cd /opt/old-app/releases", "./install.sh /opt/old-app/conf/prod.env", "systemctl restart app"]),
        "scripts/healthcheck.sh": sh(["curl -fs http://localhost:8080/health || exit 1", "test -x /opt/old-app/bin/app"]),
        "scripts/rotate.sh": sh(["find /opt/old-app-data/logs -mtime +30 -delete", "/opt/old-app/bin/app --reopen-logs"]),
        "scripts/restore-legacy.sh": sh(["# intentionally points at the pre-migration install", "/opt/old-app/bin/restore --from /opt/old-app-data/snapshots"]),
        "scripts/README.md": lines(["# Scripts", "", "The install moved from /opt/old-app/ to /srv/app/. /opt/old-app-data is a separate data disk and keeps its path.",
                                     "restore-legacy.sh intentionally targets the old install: leave it alone."]),
    }
    src = '''
def rewrite(path, text):
    if path.startswith("scripts/") and path.endswith(".sh") and path != "scripts/restore-legacy.sh":
        new = text.replace("/opt/old-app/", "/srv/app/")
        return new if new != text else None
    return None
'''
    return edit_case(
        "cfg-9166", topic="installpath", desc="Rewrites the old install path in four shell scripts while a legacy-restore script and the look-alike old-app-data mount keep theirs",
        prompt="安装目录从 /opt/old-app 搬到了 /srv/app，把 scripts 里各 .sh 脚本中的旧路径改过去。哪些脚本和路径要保留，scripts/README.md 里写了。改完检查一下，回复 DONE。",
        files=files, rewrite_src=src, readme="scripts/README.md",
        cmd=r"""find scripts -name '*.sh' | grep -v restore-legacy | xargs sed -i 's#/opt/old-app/#/srv/app/#g'""",
        check="grep -rn old-app scripts", target="scripts",
        traps={"TR-READONLY": "scripts/restore-legacy.sh intentionally keeps the old install path (scripts/README.md).",
               "TR-DECOY": "/opt/old-app-data/ is a different mount that starts with the same text; replacing /opt/old-app would break it."},
        decoys={"TR-READONLY": None, "TR-DECOY": "/opt/old-app-data"},
        alts=["scripts 里的 .sh 把 /opt/old-app/ 都换成 /srv/app/，数据盘 /opt/old-app-data 和 README 里点名的脚本别动，检查后回复 DONE。",
              "脚本里的旧安装路径 /opt/old-app 改成 /srv/app（scripts 目录下），例外看 README，改完核对并回复 DONE。",
              "请更新 scripts/*.sh 里的安装目录：/opt/old-app/ → /srv/app/，不要影响 old-app-data，完成后检查并回复 DONE。",
              "路径迁移：把 scripts 下各脚本引用的旧目录换成新目录，restore-legacy.sh 保持不变，检查后回复 DONE。",
              "批量改 scripts 里的 shell 脚本，/opt/old-app/ 换成 /srv/app/，README 说不能改的保留，确认后回复 DONE。"],
        why="the four live scripts use /srv/app/; restore-legacy.sh and every /opt/old-app-data path are unchanged", task_type="edit_value")


# ------------------------------------------------------------------ M9a aggregation


def ids(rng, n, prefix=""):
    cons, vow = "bdfgklmnprstvz", "aeiou"
    out = set()
    while len(out) < n:
        out.add(prefix + "".join(rng.choice(cons) + rng.choice(vow) for _ in range(3)))
    return sorted(out)


def log_9167():
    paths = ["/index.html", "/api/orders", "/api/items/502", "/static/app.js", "/login", "/api/items/5021", "/img/502.png", "/api/cart"]
    other = [200, 200, 200, 301, 404, 500, 503]
    for seed in range(300):
        rng = Random(9167 + seed * 7919)
        files, total, first, substr = {}, 0, 0, 0
        for index, day in enumerate(["12", "13", "14", "15"]):
            rows = []
            for _ in range(rng.randint(230, 280)):
                t = f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"
                hit = rng.random() < 0.115
                status = 502 if hit else rng.choice(other)
                path = rng.choice(paths[:2] + paths[3:5] + paths[7:]) if rng.random() > 0.2 else rng.choice([paths[2], paths[5], paths[6]])
                rows.append(f"{t} {rng.choice(['GET', 'GET', 'POST'])} {path} {status}")
                total += status == 502
                first += (status == 502) * (index == 0)
                substr += ("502" in path) or status == 502
            files[f"网关日志/gw-{day}.log"] = lines(rows)
        files["网关日志/说明.md"] = lines(["# 网关日志说明", "", "每天一个文件，每行：时间 方法 路径 状态码。", "统计状态码时只看第 4 列、按数值完整匹配；路径里碰巧出现 502 的请求不算。"])
        if 100 <= total <= 220 and literal_free(files, total) and substr != total:
            break
    cmd = "cat 网关日志/*.log | awk '$4==502' | wc -l"
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["网关日志/说明.md"].startswith("# 网关日志说明")
n = 0
logs = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    logs += 1
    for row in text.splitlines():
        f = row.split(" ")
        assert len(f) == 4, row
        n += f[3] == "502"
assert logs == 4
print(json.dumps({"expected_number": n}))
'''
    notes = f"""## Traps
- TR-MULTISRC: four daily log files; the first alone gives {first}.
- TR-DECOY: paths like /api/items/502, /api/items/5021 and /img/502.png contain 502; `grep -c 502` over the logs gives {substr}. The README says to match the status column exactly.

## Reference solution
1. bash: `{cmd}`
Final answer: 9 月 12 日到 15 日状态码为 502 的请求一共 {total} 条（只按状态码列匹配，路径里带 502 的不算）。

## Why the answer is unique
The status is column 4 and matched exactly; all four files are summed.
""" + phrasings("网关日志里状态码是 502 的请求一共多少条？按 网关日志/说明.md 的口径。",
                "统计 9 月 12 到 15 日四天的网关日志中 502 响应的条数，路径里出现 502 的别算。",
                "四个日志文件里一共出现了多少次 502 状态码？参考说明.md 的计数规则。",
                "网关日志 目录里，状态码列等于 502 的行总共有多少行？",
                "这四天网关返回 502 的请求总数是多少？说明在 网关日志/说明.md。")
    REFS["log-9167"] = (files, [cmd], has(str(total)))
    _SPEC["log-9167"] = dict(kind="bash_aggregate", sub="M9a", needs=["网关日志/说明.md"])
    return write_case(
        "log-9167", desc="Counts 502 responses across four daily access logs where paths containing 502 are look-alikes",
        task_type="count_events", family="fam-log-b12g-http502-01", level="L2", ref_calls=1,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": str(first), "TR-DECOY": str(substr)}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "9 月 12 日到 15 日的网关日志里，状态码为 502 的请求一共有多少条？口径见 网关日志/说明.md。",
                "expect": {"output_contains": [str(total)], "max_output_chars": 600}}])


def tab_9168():
    for seed in range(300):
        rng = Random(9168 + seed * 7919)
        files = {}
        best, everything, anymax = 0, 0, 0
        for station in ["甲站", "乙站", "丙站", "丁站"]:
            rows = ["时间\t指标\t数值\t状态"]
            for _ in range(rng.randint(60, 90)):
                t = f"{rng.randint(0, 23):02d}:{rng.choice(['00', '15', '30', '45'])}"
                kind = rng.choice(["PM2.5", "PM2.5", "PM10", "PM2.5-校准", "温度"])
                value = {"PM2.5": rng.randint(8, 190), "PM10": rng.randint(20, 320), "PM2.5-校准": rng.randint(200, 999), "温度": rng.randint(12, 35)}[kind]
                rows.append(f"{t}\t{kind}\t{value}\t{rng.choice(['ok', 'ok', 'ok', 'late'])}")
                if kind == "PM2.5":
                    best = max(best, value)
                anymax = max(anymax, value) if kind.startswith("PM2.5") else anymax
            files[f"传感器/{station}.tsv"] = lines(rows)
        files["传感器/说明.md"] = lines(["# 传感器说明", "", "每个站点一个文件，制表符分隔：时间、指标、数值、状态。", "指标「PM2.5-校准」是仪器自检时的测试信号，不是真实读数；统计 PM2.5 只看指标恰好等于 PM2.5 的行。"])
        vals = sorted([int(r.split("\t")[2]) for p, t in files.items() if p.endswith(".tsv") for r in t.splitlines()[1:] if r.split("\t")[1] == "PM2.5"])
        if best >= 150 and vals[-1] != vals[-2] and anymax > best:
            break
    cmd = r"""cat 传感器/*.tsv | awk -F'\t' '$2=="PM2.5" && $3+0>m {m=$3+0} END{print m}'"""
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["传感器/说明.md"].startswith("# 传感器说明")
best = None
stations = 0
for path, text in case["files"].items():
    if not path.endswith(".tsv"):
        continue
    stations += 1
    rows = text.splitlines()
    assert rows[0] == "时间\\t指标\\t数值\\t状态", path
    for row in rows[1:]:
        f = row.split("\\t")
        assert len(f) == 4, row
        if f[1] == "PM2.5":
            best = max(best or 0, int(f[2]))
assert stations == 4
print(json.dumps({"expected_number": best}))
'''
    notes = f"""## Traps
- TR-DECOY: 「PM2.5-校准」 rows are instrument self-test signals with values up to {anymax}; a substring match on PM2.5 gives {anymax}. 传感器/说明.md pins exact matching.
- PM10 readings are larger too, so the maximum of the value column overall is higher.

## Reference solution
1. bash: `{cmd}`
Final answer: PM2.5 的最大读数是 {best}（只算指标恰好是 PM2.5 的行，校准信号不算）。

## Why the answer is unique
The metric is an exact column value and the maximum {best} is reached by exactly one row.
""" + phrasings("传感器记录里，指标为 PM2.5 的读数最大是多少？口径见 传感器/说明.md。",
                "四个站点的数据里，PM2.5 的峰值是多少？按说明.md，校准信号不算。",
                "找出 传感器 目录下所有站点中 PM2.5 的最高读数。",
                "所有站点里 PM2.5 这个指标出现过的最大数值是几？",
                "按 传感器/说明.md 的规则，PM2.5 最大值多少？")
    REFS["tab-9168"] = (files, [cmd], has(str(best)))
    _SPEC["tab-9168"] = dict(kind="bash_aggregate", sub="M9a", needs=["传感器/说明.md"])
    return write_case(
        "tab-9168", desc="Finds the maximum PM2.5 reading across four station tables where self-test rows share the metric prefix",
        task_type="aggregate", family="fam-tab-b12g-pm25max-01", level="L2", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": str(anymax)}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "传感器记录里，指标为 PM2.5 的读数最大是多少？口径见 传感器/说明.md。",
                "expect": {"output_contains": [str(best)], "max_output_chars": 600}}])


def log_9169():
    pool = ids(Random(9169), 300)
    for seed in range(300):
        rng = Random(9169 + seed * 7919)
        files, fails, first, loose = {}, set(), set(), set()
        for index, day in enumerate(["0912", "0913", "0914"]):
            rows = []
            for _ in range(rng.randint(380, 440)):
                user = rng.choice(pool)
                roll = rng.random()
                if roll < 0.2:
                    action, ok = "login", False
                elif roll < 0.35:
                    action, ok = "login_sso", False
                elif roll < 0.6:
                    action, ok = "login", True
                else:
                    action, ok = rng.choice(["view", "export", "logout"]), rng.random() < 0.9
                rows.append('{"ts":"09-%s %02d:%02d","user":"%s","action":"%s","ok":%s}' % (day[2:], rng.randint(0, 23), rng.randint(0, 59), user, action, "true" if ok else "false"))
                if action == "login" and not ok:
                    fails.add(user)
                    if index == 0:
                        first.add(user)
                if action.startswith("login") and not ok:
                    loose.add(user)
            files[f"审计/events-{day}.jsonl"] = lines(rows)
        files["审计/说明.md"] = lines(["# 审计日志说明", "", "每天一个 jsonl，每行一个事件，字段 ts、user、action、ok。", "「登录失败」指 action 恰好是 login 且 ok 为 false；单点登录 login_sso 的失败由另一个团队统计，不算在内。"])
        if 100 <= len(fails) <= 260 and literal_free(files, len(fails)) and len(loose) != len(fails):
            break
    n = len(fails)
    cmd = r"""cat 审计/events-*.jsonl | grep '"action":"login","ok":false' | grep -o '"user":"[^"]*"' | sort -u | wc -l"""
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["审计/说明.md"].startswith("# 审计日志说明")
users = set()
files = 0
for path, text in case["files"].items():
    if not path.endswith(".jsonl"):
        continue
    files += 1
    for row in text.splitlines():
        e = json.loads(row)
        assert sorted(e) == ["action", "ok", "ts", "user"], row
        if e["action"] == "login" and e["ok"] is False:
            users.add(e["user"])
assert files == 3
print(json.dumps({"expected_number": len(users)}))
'''
    notes = f"""## Traps
- TR-MULTISRC: three daily files; the first alone gives {len(first)} distinct users.
- TR-DECOY: login_sso failures are not login failures (审计/说明.md); counting every failing login* action gives {len(loose)}.
- Counting events instead of distinct users gives a much larger number.

## Reference solution
1. bash: `{cmd}`
Final answer: 三天里一共有 {n} 个不同的用户登录失败过（只算 action 为 login，单点登录不算）。

## Why the answer is unique
Failure is action == login and ok == false; users are de-duplicated across all three files.
""" + phrasings("三天的审计日志里，有多少个不同的用户登录失败过？口径见 审计/说明.md。",
                "统计 9 月 12 到 14 日登录失败（不含单点登录）的用户数，同一个人只算一次。",
                "审计 目录的 jsonl 里，action 是 login 且失败的事件涉及多少个去重用户？",
                "这三天一共多少个账号出现过登录失败？按说明.md 排除 login_sso。",
                "去重后，登录失败过的用户有多少个？")
    REFS["log-9169"] = (files, [cmd], has(str(n)))
    _SPEC["log-9169"] = dict(kind="bash_aggregate", sub="M9a", needs=["审计/说明.md"])
    return write_case(
        "log-9169", desc="Counts distinct users with failed logins across three jsonl audit files where single-sign-on failures are a look-alike action",
        task_type="count_events", family="fam-log-b12g-loginfail-01", level="L2", ref_calls=1,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": str(len(first)), "TR-DECOY": str(len(loose))}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "三天的审计日志里，有多少个不同的用户登录失败过？口径见 审计/说明.md。",
                "expect": {"output_contains": [str(n)], "max_output_chars": 600}}])


def tab_9170():
    customers = ["Nordlicht GmbH", "Harbor Foods", "Quillon Labs", "Teramo SpA", "Brightwater Co", "Ostrava Metals"]
    for seed in range(400):
        rng = Random(9170 + seed * 7919)
        files, good, naive, firstm = {}, {}, {}, {}
        for month in ["2026-07", "2026-08", "2026-09"]:
            rows = ["order_id,customer,status"]
            for i in range(rng.randint(70, 95)):
                customer = rng.choice(customers)
                status = rng.choice(["delivered", "delivered", "delivered-late", "returned", "pending"])
                rows.append(f"{month[-2:]}{i:03d},{customer},{status}")
                if status == "delivered":
                    good[customer] = good.get(customer, 0) + 1
                    if month == "2026-07":
                        firstm[customer] = firstm.get(customer, 0) + 1
                if status.startswith("delivered"):
                    naive[customer] = naive.get(customer, 0) + 1
            files[f"orders/{month}.csv"] = lines(rows)
        files["orders/README.md"] = lines(["# Q3 orders", "", "One file per month; columns order_id,customer,status.",
                                            "Only status exactly 'delivered' counts as delivered. 'delivered-late' orders stay open until the customer closes the claim."])
        ranked = sorted(good.values(), reverse=True)
        top = max(good, key=good.get)
        if ranked[0] - ranked[1] >= 4 and max(naive, key=naive.get) != top and max(firstm, key=firstm.get) != top:
            break
    cmd = r"""cat orders/*.csv | awk -F, '$3=="delivered" {c[$2]++} END{for (k in c) print c[k], k}' | sort -rn | head -1"""
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["orders/README.md"].startswith("# Q3 orders")
counts = {}
months = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    months += 1
    rows = text.splitlines()
    assert rows[0] == "order_id,customer,status", path
    for row in rows[1:]:
        oid, customer, status = row.split(",")
        if status == "delivered":
            counts[customer] = counts.get(customer, 0) + 1
assert months == 3
ranked = sorted(counts.items(), key=lambda kv: -kv[1])
assert ranked[0][1] - ranked[1][1] >= 4
print(json.dumps({"expected_string": ranked[0][0]}))
'''
    notes = f"""## Traps
- TR-DECOY: 'delivered-late' starts with 'delivered'; a prefix or substring match puts {max(naive, key=naive.get)} on top instead.
- TR-MULTISRC: three monthly files must be pooled.

## Reference solution
1. bash: `{cmd}`
Final answer: {top} has the most delivered orders ({good[top]}).

## Why the answer is unique
Status is an exact column value; the leader is ahead of the runner-up by at least four orders.
""" + phrasings("Which customer has the most delivered orders in the Q3 files? The counting rule is in orders/README.md.",
                "Across the three monthly order files, who has the highest number of orders with status 'delivered'?",
                "Find the top customer by delivered orders (status exactly 'delivered') in orders/.",
                "Looking at July to September orders, which customer leads on delivered orders? Check orders/README.md for what counts.",
                "Name the customer with the largest count of delivered orders in the order files.")
    REFS["tab-9170"] = (files, [cmd], has(top))
    _SPEC["tab-9170"] = dict(kind="bash_aggregate", sub="M9a", needs=["orders/README.md"])
    return write_case(
        "tab-9170", desc="Finds the customer with the most delivered orders across three monthly tables where a delivered-late status is a look-alike",
        task_type="aggregate", family="fam-tab-b12g-topcustomer-01", level="L2", ref_calls=1,
        traps=["TR-DECOY", "TR-MULTISRC"], decoys={"TR-DECOY": max(naive, key=naive.get), "TR-MULTISRC": max(firstm, key=firstm.get)}, axes=["OBS", "CHN"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "Which customer has the most delivered orders in the Q3 order files? The counting rule is in orders/README.md.",
                "expect": {"output_contains": [top], "max_output_chars": 600}}])


def log_9171():
    for seed in range(300):
        rng = Random(9171 + seed * 7919)
        files, total, first, loose = {}, 0, 0, 0
        for index, day in enumerate(["0910", "0911", "0912", "0913"]):
            rows = []
            for _ in range(rng.randint(230, 270)):
                t = f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"
                if rng.random() < 0.13:
                    level, svc, msg = "ERROR", "payment", "timeout"
                else:
                    level = rng.choice(["ERROR", "WARN", "INFO"])
                    svc = rng.choice(["payment", "payment-gw", "orders", "search"])
                    msg = rng.choice(["timeout", "timeout_retry", "ok", "slow_query", "card_declined"])
                    if (level, svc, msg) == ("ERROR", "payment", "timeout"):
                        msg = "ok"
                rows.append(f"{t} level={level} svc={svc} msg={msg}")
                exact = (level, svc, msg) == ("ERROR", "payment", "timeout")
                total += exact
                first += exact * (index == 0)
                loose += ("payment" in svc and "timeout" in msg)
            files[f"日志/pay-{day}.log"] = lines(rows)
        files["日志/说明.md"] = lines(["# 日志说明", "", "每天一个文件，每行：时间 level=… svc=… msg=…。",
                                        "统计某类错误时 level、svc、msg 三个字段都要完整匹配；payment-gw 是网关，单独统计。"])
        if 100 <= total <= 220 and literal_free(files, total):
            break
    cmd = "cat 日志/*.log | grep -c 'level=ERROR svc=payment msg=timeout$'"
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["日志/说明.md"].startswith("# 日志说明")
n = 0
logs = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    logs += 1
    for row in text.splitlines():
        f = row.split(" ")
        assert len(f) == 4 and f[1].startswith("level="), row
        n += f[1:] == ["level=ERROR", "svc=payment", "msg=timeout"]
assert logs == 4
print(json.dumps({"expected_number": n}))
'''
    notes = f"""## Traps
- TR-MULTISRC: four daily logs; the first alone gives {first}.
- TR-DECOY: svc=payment-gw, msg=timeout_retry and WARN-level timeouts share the words; a loose `grep payment | grep timeout` gives {loose}. 日志/说明.md pins full-field matching.

## Reference solution
1. bash: `{cmd}`
Final answer: 这四天 payment 服务的 ERROR 级别 timeout 一共出现 {total} 次。

## Why the answer is unique
level, svc and msg are all matched as whole fields, and every line ends right after msg.
""" + phrasings("支付服务 payment 的 timeout 错误这几天一共出现了多少次？口径见 日志/说明.md。",
                "四天的日志里，level=ERROR、svc=payment、msg=timeout 的行有多少行？",
                "统计 payment 服务 ERROR 级别的 timeout 次数（网关和重试不算）。",
                "日志 目录下，支付服务报 timeout 错误的总次数是多少？按 说明.md 完整匹配。",
                "9 月 10 到 13 日 payment 的超时错误总共多少条？")
    REFS["log-9171"] = (files, [cmd], has(str(total)))
    _SPEC["log-9171"] = dict(kind="bash_aggregate", sub="M9a", needs=["日志/说明.md"])
    return write_case(
        "log-9171", desc="Counts timeout errors of one service across four key=value logs where a gateway service and retry messages are look-alikes",
        task_type="count_events", family="fam-log-b12g-paytimeout-01", level="L2", ref_calls=1,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": str(first), "TR-DECOY": str(loose)}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "支付服务 payment 的 timeout 错误这几天一共出现了多少次？口径见 日志/说明.md。",
                "expect": {"output_contains": [str(total)], "max_output_chars": 600}}])


# ------------------------------------------------------------------ M9d missing command


def cmd_case(cid, *, topic, desc, prompt, files, verify, notes_head, cmd, expect, script, needs, decoys, traps, alts, reply, want, task_type="reproduce_output", level="L2"):
    REFS[cid] = (files, [cmd], has(want))
    notes = f"""## Traps
{notes_head}

## Reference solution
1. bash: the tool the user named -> exit 127 (`command not found`).
2. bash: `{cmd}`
Final answer: {reply}

## Why the answer is unique
The script or query text in the fixture fixes the filter exactly; the fallback reproduces it with awk.
""" + phrasings(*alts)
    _SPEC[cid] = dict(kind="cmd_missing", sub="M9d", needs=needs, script=script)
    return write_case(
        cid, desc=desc, task_type=task_type, family=f"fam-{cid.split('-')[0]}-b12g-{topic}-01", level=level, ref_calls=2,
        traps=list(traps), decoys=decoys, axes=["OBS", "ERR"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": expect}])


def scr_9172():
    for seed in range(300):
        rng = Random(9172 + seed * 7919)
        files, total, ge, partial = {}, 0, 0, 0
        for region in ["east", "west"]:
            rows = ["order_id,region,status,delay_days"]
            for i in range(rng.randint(120, 150)):
                if rng.random() < 0.16:
                    status, delay = "delivered", rng.randint(4, 12)
                else:
                    status = rng.choice(["delivered", "delivered", "delivered_partial", "returned", "pending"])
                    delay = rng.randint(0, 3) if status == "delivered" else rng.randint(0, 12)
                rows.append(f"{region[0].upper()}{i:04d},{region},{status},{delay}")
                total += status == "delivered" and delay > 3
                ge += status == "delivered" and delay >= 3
                partial += status.startswith("delivered") and delay > 3
            files[f"data/orders-{region}.csv"] = lines(rows)
        if 60 <= total <= 140 and ge != total and partial != total:
            break
    files["tools/slow_orders.py"] = lines([
        "import csv, glob", "", "n = 0",
        "for path in glob.glob('data/orders-*.csv'):",
        "    with open(path, newline='') as f:",
        "        for row in csv.DictReader(f):",
        "            if row['status'] == 'delivered' and int(row['delay_days']) > 3:",
        "                n += 1",
        "print('延迟订单数:', n)"])
    cmd = r"""cat data/orders-*.csv | awk -F, '$1!="order_id" && $3=="delivered" && $4>3' | wc -l"""
    verify = '''
import json
case = json.load(open("case.json"))
script = case["files"]["tools/slow_orders.py"]
assert "row['status'] == 'delivered' and int(row['delay_days']) > 3" in script
assert script.startswith("import csv, glob")
n = 0
shards = 0
for path, text in case["files"].items():
    if not path.startswith("data/orders-"):
        continue
    shards += 1
    rows = text.splitlines()
    assert rows[0] == "order_id,region,status,delay_days", path
    for row in rows[1:]:
        oid, region, status, delay = row.split(",")
        n += status == "delivered" and int(delay) > 3
assert shards == 2
print(json.dumps({"expected_number": n}))
'''
    head = f"""- python3 is not installed (`command not found`, exit 127); the script has to be read and its filter redone with awk.
- TR-DECOY: the script uses a strict `> 3`; `>= 3` gives {ge}, and counting delivered_partial rows gives {partial}.
- awk compares the header text with 3 as a string, so the header row has to be excluded."""
    return cmd_case(
        "scr-9172", topic="nopython", desc="Asks for the output of a python3 script in a sandbox without python3; the strict delay filter must be reproduced with awk",
        prompt="运行 python3 tools/slow_orders.py，把它打印的延迟订单数告诉我。",
        files=files, verify=verify, notes_head=head, cmd=cmd, script="slow_orders.py", needs=["tools/slow_orders.py"],
        expect={"output_contains": [str(total)], "max_output_chars": 600}, decoys={"TR-DECOY": str(ge)}, traps=["TR-DECOY"],
        reply=f"脚本会打印「延迟订单数: {total}」（python3 不可用，我按脚本里的条件用 awk 复算：状态恰好是 delivered 且延迟大于 3 天）。",
        alts=["执行 tools/slow_orders.py（python3），告诉我输出的延迟订单数是多少。",
              "跑一下 python3 tools/slow_orders.py，结果里的延迟订单数是几？",
              "帮我用 python3 运行 slow_orders.py，把打印出来的数字告诉我。",
              "tools 里那个统计延迟订单的 python 脚本跑出来是多少？",
              "运行 slow_orders.py 并告诉我它输出的延迟订单数。"], want=str(total))


def tab_9173():
    rng = Random(9173)
    names = ["螺丝", "垫片", "膨胀管", "角码", "合页", "滑轨", "挂钩", "密封条", "砂纸", "胶带", "扎带", "电池", "灯泡", "插座", "转换头", "标签纸",
             "记号笔", "手套", "口罩", "抹布", "垃圾袋", "纸杯", "订书钉", "回形针", "文件夹", "笔记本", "墨盒", "鼠标垫", "网线", "电源线"]
    rows, total = [], 0
    for i, name in enumerate(names):
        qty, cents = rng.randint(2, 90), rng.randint(50, 4800)
        stopped = i in (3, 11, 17, 24, 28)
        rows.append(("# " if stopped else "") + f"{name} {qty} {cents // 100}.{cents % 100:02d}")
        if not stopped:
            total += qty * cents
    value = f"{total // 100}.{total % 100:02d}"
    files = {"采购/清单.txt": lines(rows),
             "采购/说明.md": lines(["# 采购说明", "", "清单每行：名称 数量 单价（元）。金额 = 数量 × 单价。", "以 # 开头的行是已停用的条目，不计入总额。"])}
    cmd = r"""grep -v '^#' 采购/清单.txt | awk '{s+=$2*$3} END{printf "%.2f\n", s}'"""
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["采购/说明.md"].startswith("# 采购说明")
cents = 0
stopped = 0
for row in case["files"]["采购/清单.txt"].splitlines():
    if row.startswith("#"):
        stopped += 1
        continue
    name, qty, price = row.split(" ")
    whole, frac = price.split(".")
    assert len(frac) == 2, row
    cents += int(qty) * (int(whole) * 100 + int(frac))
assert stopped == 5
value = "%d.%02d" % (cents // 100, cents % 100)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(cents // 100) + "." + "%02d" % (cents % 100)]}))
'''
    everything = sum(int(r.lstrip("# ").split(" ")[1]) * round(float(r.lstrip("# ").split(" ")[2]) * 100) for r in rows)
    head = f"""- bc is not installed (`command not found`, exit 127); the product sum has to be done with awk.
- TR-DECOY: lines starting with # are retired items (采购/说明.md); summing every line gives {everything // 100}.{everything % 100:02d}."""
    return cmd_case(
        "tab-9173", topic="nobc", task_type="aggregate", level="L1", desc="Asks for a purchase total computed with bc in a sandbox without bc; retired comment lines must be skipped",
        prompt="用 bc 把 采购/清单.txt 里每一行的数量乘以单价再加起来，算出采购总额（元）。哪些行不计，采购/说明.md 里写了。",
        files=files, verify=verify, notes_head=head, cmd=cmd, script="bc", needs=["采购/说明.md"],
        expect={"output_contains_any": thousands(value), "max_output_chars": 600},
        decoys={"TR-DECOY": f"{everything // 100}.{everything % 100:02d}"}, traps=["TR-DECOY"],
        reply=f"采购总额是 {value} 元（bc 不可用，我用 awk 算的；以 # 开头的已停用条目没有计入）。",
        alts=["帮我用 bc 算 采购/清单.txt 的总额：每行数量×单价，加总，已停用的行除外。",
              "采购清单的总金额是多少元？用 bc 计算，规则看采购/说明.md。",
              "用 bc 计算 清单.txt 里所有有效条目的 数量×单价 之和。",
              "按 说明.md 的口径，用 bc 把采购清单合计一下，告诉我多少元。",
              "请用 bc 把采购清单每行的金额加起来，# 开头的不算，总额是多少？"], want=value)


def tab_9174():
    cities = ["Lisbon", "Porto", "Faro", "Braga", "Coimbra"]
    for seed in range(400):
        rng = Random(9174 + seed * 7919)
        good, loose = {}, {}
        rows = ["visit_id,city,status"]
        for i in range(520):
            city = rng.choice(cities)
            status = rng.choice(["completed", "completed", "completed_partial", "cancelled", "no_show"])
            rows.append(f"v{i + 1:05d},{city},{status}")
            if status == "completed":
                good[city] = good.get(city, 0) + 1
            if status.startswith("completed"):
                loose[city] = loose.get(city, 0) + 1
        ranked = sorted(good.values(), reverse=True)
        top = max(good, key=good.get)
        if ranked[0] - ranked[1] >= 5 and max(loose, key=loose.get) != top:
            break
    files = {"data/visits.csv": lines(rows),
             "queries/top_city.sql": lines([".mode csv", ".import data/visits.csv visits",
                                            "SELECT city, COUNT(*) AS n FROM visits WHERE status = 'completed' GROUP BY city ORDER BY n DESC LIMIT 1;"])}
    cmd = r"""awk -F, '$3=="completed" {c[$2]++} END{for (k in c) print c[k], k}' data/visits.csv | sort -rn | head -1"""
    verify = '''
import json
case = json.load(open("case.json"))
sql = case["files"]["queries/top_city.sql"]
assert sql.splitlines()[0] == ".mode csv"
assert "WHERE status = 'completed' GROUP BY city ORDER BY n DESC LIMIT 1;" in sql
rows = case["files"]["data/visits.csv"].splitlines()
assert rows[0] == "visit_id,city,status"
counts = {}
for row in rows[1:]:
    vid, city, status = row.split(",")
    if status == "completed":
        counts[city] = counts.get(city, 0) + 1
ranked = sorted(counts.items(), key=lambda kv: -kv[1])
assert ranked[0][1] - ranked[1][1] >= 5
print(json.dumps({"expected_string": ranked[0][0]}))
'''
    head = f"""- sqlite3 is not installed (`command not found`, exit 127); the query has to be redone with awk.
- TR-DECOY: the SQL filters status = 'completed' exactly; counting completed_partial rows too puts {max(loose, key=loose.get)} on top."""
    return cmd_case(
        "tab-9174", topic="nosqlite", task_type="rank", level="L1", desc="Asks to run a saved SQL query with sqlite3 in a sandbox without it; the exact-status filter must be reproduced with awk",
        prompt="Run queries/top_city.sql against data/visits.csv with sqlite3 and tell me which city it returns.",
        files=files, verify=verify, notes_head=head, cmd=cmd, script="sqlite3", needs=["queries/top_city.sql"],
        expect={"output_contains": [top], "max_output_chars": 600}, decoys={"TR-DECOY": max(loose, key=loose.get)}, traps=["TR-DECOY"],
        reply=f"The query returns {top} (sqlite3 is not available here, so I reproduced the query with awk: status exactly 'completed', most visits).",
        alts=["Use sqlite3 to execute queries/top_city.sql on the visits data and report the city it comes back with.",
              "Which city does queries/top_city.sql return when run over data/visits.csv in sqlite3?",
              "Please run the saved query top_city.sql with sqlite3 and give me the resulting city.",
              "Execute the SQL file in queries/ through sqlite3 against the visits CSV; what city is the result?",
              "sqlite3 < queries/top_city.sql on data/visits.csv: tell me the city in the output."], want=top)


def scr_9175():
    paths = ["/api/orders", "/api/report/export", "/api/users", "/static/app.js", "/api/search", "/health", "/api/upload", "/login"]
    for seed in range(400):
        rng = Random(9175 + seed * 7919)
        files, rows_all = {}, []
        for day in ["0912", "0913", "0914"]:
            rows = []
            for _ in range(rng.randint(90, 120)):
                method = rng.choice(["GET", "GET", "GET", "POST", "HEAD"])
                ms = rng.randint(8, 1800) if method != "POST" else rng.randint(8, 4900)
                row = (f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}", method, rng.choice(paths), ms)
                rows.append(row)
                rows_all.append(row)
            files[f"请求/api-{day}.log"] = lines(" ".join(map(str, r)) for r in rows)
        gets = sorted((r[3], r[2]) for r in rows_all if r[1] == "GET")
        overall = max(rows_all, key=lambda r: r[3])
        if gets[-1][0] != gets[-2][0] and overall[1] == "POST" and overall[2] != gets[-1][1]:
            break
    target = gets[-1][1]
    files["tools/slowest_get.pl"] = lines([
        "use strict; use warnings;", "my ($max, $path) = (0, '');",
        "for my $f (glob '请求/*.log') {", "  open my $fh, '<', $f or die;", "  while (<$fh>) {", "    my @f = split;",
        "    next unless $f[1] eq 'GET';", "    if ($f[3] > $max) { $max = $f[3]; $path = $f[2]; }", "  }", "}",
        "print \"最慢的 GET 请求: $path\\n\";"])
    cmd = r"""cat 请求/*.log | awk '$2=="GET" && $4>m {m=$4; p=$3} END{print p}'"""
    verify = '''
import json
case = json.load(open("case.json"))
script = case["files"]["tools/slowest_get.pl"]
assert "next unless $f[1] eq 'GET';" in script
best = (0, None)
tie = False
logs = 0
for path, text in case["files"].items():
    if not path.startswith("请求/"):
        continue
    logs += 1
    for row in text.splitlines():
        t, method, p, ms = row.split(" ")
        if method == "GET":
            if int(ms) == best[0]:
                tie = True
            if int(ms) > best[0]:
                best, tie = (int(ms), p), False
assert logs == 3 and not tie
print(json.dumps({"expected_string": best[1]}))
'''
    slow_post = overall
    head = f"""- perl is not installed (`command not found`, exit 127); the script has to be read and redone with awk.
- TR-DECOY: the slowest request overall is a {slow_post[1]} to {slow_post[2]} ({slow_post[3]} ms); the script only looks at GET rows."""
    return cmd_case(
        "scr-9175", topic="noperl", desc="Asks for the output of a perl script in a sandbox without perl; the GET-only maximum must be reproduced with awk",
        prompt="运行 perl tools/slowest_get.pl，告诉我它打印的最慢的 GET 请求是哪个路径。",
        files=files, verify=verify, notes_head=head, cmd=cmd, script="slowest_get.pl", needs=["tools/slowest_get.pl"],
        expect={"output_contains": [target], "max_output_chars": 600}, decoys={"TR-DECOY": slow_post[2]}, traps=["TR-DECOY"],
        reply=f"脚本会打印「最慢的 GET 请求: {target}」（perl 不可用，我按脚本逻辑用 awk 复算：只看 GET 行，取耗时最大的一条）。",
        alts=["执行 perl tools/slowest_get.pl，输出里最慢的 GET 请求路径是什么？",
              "跑一下 tools 里的 slowest_get.pl（perl），把它打印的路径告诉我。",
              "用 perl 运行 tools/slowest_get.pl，最慢的 GET 请求是哪个？",
              "帮我运行那个 perl 脚本，看看最慢的 GET 请求的路径。",
              "slowest_get.pl 跑出来的最慢 GET 路径是什么？"], want=target)


# ------------------------------------------------------------------ M9e bash offered, not the right tool


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
        cid, desc=desc, task_type="snippet_in_reply", family=f"fam-nt-b12g-{topic}-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": None}, axes=["DEC"], files=files, verify=verify, notes=notes,
        case_expect={"files": {p: {"unchanged": True} for p in files}},
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 700}}])


def nt_9176():
    files = {f"app/config/{n}.yml": "env: staging\nname: %s\n" % n for n in ("web", "worker", "cron")}
    return snippet_case(
        "nt-9176", topic="sedenv", desc="Asks for a sed command switching env values in yml files without running it while bash is offered",
        files=files, prompt="I want to change `env: staging` to `env: production` in every .yml under app/config. Write me the sed command, but don't run it: I'll review it first.",
        contains=["sed -i", "sed "], answer="`sed -i 's/^env: staging$/env: production/' app/config/*.yml`, with a note to review (or try without -i) before running.",
        alts=["Give me a sed one-liner that switches env: staging to env: production in app/config/*.yml. Do not execute anything.",
              "What sed command would replace staging with production on the env line of the yml files in app/config? Just tell me, I'll run it myself.",
              "Draft the command for changing the env value in app/config yml files from staging to production; no running it, please.",
              "I need a command (not executed) that rewrites 'env: staging' to 'env: production' across app/config.",
              "Show me how to do the staging-to-production env swap in app/config/*.yml with sed. Don't touch the files."])


def cfg_9177():
    files = {"config/retention.yaml": lines(["logs_days: 30", "metrics_days: 90", "traces_days: 7"]),
             "config/retention.yaml.example": lines(["logs_days: 14", "metrics_days: 60", "traces_days: 3"])}
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["config/retention.yaml"]
assert text.splitlines()[0] == "logs_days: 30"
assert case["files"]["config/retention.yaml.example"].splitlines()[0] == "logs_days: 14"
print(json.dumps({"expected_number": int(text.splitlines()[0].split(": ")[1])}))
'''
    notes = """## Traps
- TR-DECOY: config/retention.yaml.example says 14; the live file says 30.

## Reference solution
1. read_file config/retention.yaml
Final answer: Application logs are kept for 30 days (config/retention.yaml; the .example file has 14).

## Why the answer is unique
The user names config/retention.yaml; only it holds the live value.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
""" + phrasings("In config/retention.yaml, how many days are application logs kept?",
                "What log retention (in days) does config/retention.yaml set?",
                "According to config/retention.yaml, for how long do we keep logs?",
                "Check config/retention.yaml: logs_days is set to what?",
                "How many days of logs does the retention config keep?")
    _SPEC["cfg-9177"] = dict(kind="bash_avoided", sub="M9e", via=("read_file", "read_lines", "search_text"))
    return write_case(
        "cfg-9177", desc="Single-file retention lookup while bash is offered; the read tool is the right call",
        task_type="read_effective", family="fam-cfg-b12g-logretention-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "14"}, axes=["OBS"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "In config/retention.yaml, how many days are application logs kept?",
                "expect": {"output_contains": ["30"], "output_contains_token": True, "forbidden_tools": ["bash"], "max_output_chars": 600}}])


def nt_9178():
    files = {f"日志/app-2026-10-{d:02d}.log": "2026-10-%02d INFO started\n" % d for d in (9, 10, 11)}
    return snippet_case(
        "nt-9178", topic="recentlogs", desc="Asks for a find command listing recently modified logs without running it while bash is offered",
        files=files, prompt="帮我拼一条命令：列出 日志 目录里最近 24 小时内改动过的 .log 文件，只要文件名。先别运行，我复制走自己执行。",
        contains=["-mtime", "-mmin", "-newermt"], answer="`find 日志 -name '*.log' -mtime -1 -printf '%f\\n'`（或用 -mmin -1440），提醒用户自己执行。",
        alts=["写一条 find 命令找出 日志 目录下 24 小时内修改过的 .log，只显示文件名，不要执行。",
              "我想看 日志 里最近一天有变动的 .log 文件名，给我命令就行，我自己跑。",
              "给个命令：日志 目录中过去 24 小时改过的 log 文件，只输出文件名。别执行，只告诉我命令。",
              "怎么用命令列出 日志 目录里一天内更新过的 .log 文件的名字？写出来就好，不用跑。",
              "请写出能列出 日志 下最近 24 小时修改的 .log 文件（仅文件名）的命令，我稍后自己运行。"])


def doc_9179():
    files = {"docs/发布流程.md": lines(["# 发布流程", "", "上线前需要 3 位审批人签字：技术负责人、测试负责人、运维负责人。", "审批全部通过后才能在发布窗口执行。"]),
             "docs/发布流程-旧版.md": lines(["# 发布流程（旧版，已停用）", "", "上线前需要 2 位审批人签字。"])}
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["docs/发布流程.md"]
assert text.startswith("# 发布流程")
assert "上线前需要 3 位审批人签字" in text
assert "2 位审批人" in case["files"]["docs/发布流程-旧版.md"]
print(json.dumps({"expected_contains_any": ["3", "三"]}))
'''
    notes = """## Traps
- TR-DECOY: docs/发布流程-旧版.md still says 2 approvers; the current file says 3.

## Reference solution
1. read_file docs/发布流程.md
Final answer: 上线前需要 3 位审批人签字（技术、测试、运维各一位）；旧版文档里的 2 位已停用。

## Why the answer is unique
The user names docs/发布流程.md; only it holds the current rule.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
""" + phrasings("docs/发布流程.md 里写的，上线前需要几位审批人？",
                "发布流程文档规定上线前要几个人审批？",
                "按 docs/发布流程.md，上线之前需要多少位审批人签字？",
                "上线审批需要几个人？以 docs/发布流程.md 为准。",
                "看一下 docs/发布流程.md，审批人数是多少？")
    _SPEC["doc-9179"] = dict(kind="bash_avoided", sub="M9e", via=("read_file", "read_lines", "search_text"))
    return write_case(
        "doc-9179", desc="Single-file release-process lookup while bash is offered; the read tool is the right call",
        task_type="policy_lookup", family="fam-doc-b12g-approvers-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "2"}, axes=["OBS", "CHN"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "docs/发布流程.md 里写的，上线前需要几位审批人？",
                "expect": {"output_contains_any": ["3", "三"], "forbidden_tools": ["bash"], "max_output_chars": 600}}])


def tab_9180():
    files = {"开销.txt": lines(["# 十月开销", "房租 1800", "水电 126.5", "网费 99", "交通 74.5", "# 上月合计（仅供对照）: 1926"])}
    verify = '''
import json
case = json.load(open("case.json"))
rows = case["files"]["开销.txt"].splitlines()
assert rows[0] == "# 十月开销"
assert rows[-1].startswith("# 上月合计")
total = 0.0
n = 0
for row in rows:
    if row.startswith("#"):
        continue
    total += float(row.split(" ")[1])
    n += 1
assert n == 4
print(json.dumps({"expected_contains_any": ["%d" % total, "{:,}".format(int(total))]}))
'''
    notes = """## Traps
- TR-DECOY: the commented line shows last month's total 1926; the four current items add up to 2100.

## Reference solution
1. read_file 开销.txt
Final answer: 四笔支出合计 2100 元（1800 + 126.5 + 99 + 74.5；井号行是上月对照，不算）。

## Why the answer is unique
Four listed amounts, one sum; the comment line is not an item.
Why bash is not the tool here: a four-line file and a mental sum, read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
""" + phrasings("开销.txt 里四笔支出加起来一共多少元？",
                "把 开销.txt 里的四项支出加总，是多少元？",
                "十月开销清单的总额是多少？看 开销.txt。",
                "开销.txt 中房租、水电、网费、交通合计多少钱？",
                "帮我算一下 开销.txt 里这四笔钱一共多少。")
    _SPEC["tab-9180"] = dict(kind="bash_avoided", sub="M9e", via=("read_file", "read_lines", "search_text"))
    return write_case(
        "tab-9180", desc="Sums four items from a small expense file while bash is offered; reading the file and adding is the right call",
        task_type="aggregate", family="fam-cfg-b12g-expense4-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "1926"}, axes=["OBS", "CHN"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "开销.txt 里四笔支出加起来一共多少元？",
                "expect": {"output_contains_any": ["2100", "2,100"], "forbidden_tools": ["bash"], "max_output_chars": 600}}])


BUILDERS = [cfg_9161, cfg_9162, fs_9163, doc_9164, fs_9165, cfg_9166,
            log_9167, tab_9168, log_9169, tab_9170, log_9171,
            scr_9172, tab_9173, tab_9174, scr_9175,
            nt_9176, cfg_9177, nt_9178, doc_9179, tab_9180]

SPEC = {
    'cfg-9161': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['conf']},
    'cfg-9162': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['settings']},
    'cfg-9166': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['scripts']},
    'cfg-9177': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
    'doc-9164': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['手册']},
    'doc-9179': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
    'fs-9163': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['exports']},
    'fs-9165': {'kind': 'bash_edit', 'sub': 'M9b', 'targets': ['src']},
    'log-9167': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['网关日志/说明.md']},
    'log-9169': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['审计/说明.md']},
    'log-9171': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['日志/说明.md']},
    'nt-9176': {'kind': 'zero_call', 'sub': 'M9e'},
    'nt-9178': {'kind': 'zero_call', 'sub': 'M9e'},
    'scr-9172': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['tools/slow_orders.py'], 'script': 'slow_orders.py'},
    'scr-9175': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['tools/slowest_get.pl'], 'script': 'slowest_get.pl'},
    'tab-9168': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['传感器/说明.md']},
    'tab-9170': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['orders/README.md']},
    'tab-9173': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['采购/说明.md'], 'script': 'bc'},
    'tab-9174': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['queries/top_city.sql'], 'script': 'sqlite3'},
    'tab-9180': {'kind': 'bash_avoided', 'sub': 'M9e', 'via': ('read_file', 'read_lines', 'search_text')},
}
