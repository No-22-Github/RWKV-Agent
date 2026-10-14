"""E: no list_files; locate files with search_text or bash (20121-20128)."""
from common import has, lines, mk, value

BUILDERS = []
NL = ["list_files"]


def reg(f):
    BUILDERS.append(f)
    return f


def tree(extra, base):
    f = dict(base)
    f.update(extra)
    return f


BASE_ZH = {"docs/客服/售后手册.md": "# 售后手册\n\n退款流程：申请 -> 审核 -> 打款。\n", "docs/客服/话术.md": "# 话术\n\n开场白要简短。\n",
           "docs/运营/周报模板.md": "# 周报\n\n本周完成：\n", "src/app/main.py": "def main():\n    pass\n", "src/app/util.py": "def clamp(x):\n    return x\n",
           "config/dev.yaml": "port: 8080\n", "config/prod.yaml": "port: 8443\n", "config/test.yaml": "port: 9090\n",
           "finance/invoice-2026-08.csv": "id,amt\n1,10\n", "finance/summary.csv": "m,t\n8,10\n", "README.md": "# 项目\n"}
BASE_EN = {"src/billing/invoice.py": "def parse_invoice(text):\n    return text.split(',')\n", "src/billing/tax.py": "def tax(x):\n    return x * 0.2\n",
           "src/core/settings.json": "{}\n", "config/settings.json": "{\"a\": 1}\n", "config/settings.local.json": "{\"a\": 2}\n",
           "scripts/deploy.sh": "#!/bin/sh\necho deploy\n", "scripts/backup.sh": "#!/bin/sh\necho backup\n", "tools/ci/lint.sh": "#!/bin/sh\necho lint\n",
           "tools/ci/test.sh": "#!/bin/sh\necho test\n", "README.md": "# repo\n", "docs/notes.txt": "misc\n"}


def case(cid, prompt, files, must, body, exp, *, sub, tt, desc, ref_text, why, cmds=None, extra=None, scen_ref=None):
    turns = [(prompt, exp)] + ([extra] if extra else [])
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=NL, must=must,
       traps_notes=["No directory listing tool: find the file by searching contents, or with find/ls in the shell."],
       ref_text=ref_text, why=why, body=body, ref_calls=2, ref=scen_ref)


def bash_ref(cmds, *needles):
    return (cmds, has(*needles))


@reg
def e1():
    f = dict(BASE_ZH)
    body = 'print(json.dumps({"expected_string": [p for p in case["files"] if "invoice" in p][0].split("/")[-1]}, ensure_ascii=False))\n'
    case("fs-20121", "项目里名字带 invoice 的文件是哪个？只回答文件名。", f, ["bash"], body, value(["invoice-2026-08.csv"]), sub="E-bash", tt="find_file",
         desc="Finds a file by name part when no listing tool exists", ref_text="bash: find . -name '*invoice*' -> finance/invoice-2026-08.csv",
         why="Exactly one path contains invoice.", scen_ref=bash_ref(["find . -name '*invoice*'"], "invoice-2026-08.csv"))


@reg
def e2():
    body = 'print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "退款流程" in t][0].split("/")[-1]}, ensure_ascii=False))\n'
    case("fs-20122", "写着「退款流程」的文档是哪个文件？只回答文件名。", dict(BASE_ZH), ["search_text"], body, value(["售后手册.md"]), sub="E-search", tt="find_file",
         desc="Finds the document containing a phrase when no listing tool exists", ref_text="search_text query=退款流程 -> docs/客服/售后手册.md",
         why="The phrase occurs in one file.")


@reg
def e3():
    f = dict(BASE_ZH)
    for i in range(1, 8):
        f["backup/2026-0%d.tar" % i] = "x\n"
    for i in range(1, 4):
        f["backup/2026-0%d.tar.sig" % i] = "s\n"
    body = 'print(json.dumps({"expected_number": sum(1 for p in case["files"] if p.startswith("backup/") and p.endswith(".tar"))}))\n'
    case("fs-20123", "backup 目录里有多少个 .tar 文件？只回答数字。", f, ["bash"], body, value(["7"], token=True), sub="E-bash", tt="count_by_type",
         desc="Counts files of one extension when no listing tool exists", ref_text="bash: find backup -name '*.tar' | wc -l -> 7",
         why=".tar.sig files are decoys and do not end in .tar.", scen_ref=bash_ref(["find backup -name '*.tar' | wc -l"], "7"))


@reg
def e4():
    body = 'print(json.dumps({"expected_string": [p for p in case["files"] if p.endswith("settings.local.json")][0]}))\n'
    case("fs-20124", "Where is settings.local.json? Give me the path only.", dict(BASE_EN), ["bash"], body, value(["config/settings.local.json"]), sub="E-bash",
         tt="find_file", desc="Finds a named file among near-name decoys when no listing tool exists",
         ref_text="bash: find . -name settings.local.json -> ./config/settings.local.json", why="Other settings.json files have different names.",
         scen_ref=bash_ref(["find . -name settings.local.json"], "config/settings.local.json"))


@reg
def e5():
    body = 'print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "def parse_invoice" in t][0]}))\n'
    case("fs-20125", "Which file defines parse_invoice? Path only.", dict(BASE_EN), ["search_text"], body, value(["src/billing/invoice.py"]), sub="E-search",
         tt="find_file", desc="Finds the defining file of a function when no listing tool exists", ref_text="search_text query='def parse_invoice' -> src/billing/invoice.py",
         why="One definition in the tree.")


@reg
def e6():
    f = dict(BASE_ZH)
    f["docs/运营/SLA说明.md"] = "# SLA\n\n承诺可用性 99.9%\n"
    f["docs/运营/旧SLA.md"] = "# 旧 SLA\n\n承诺可用性 99.5%\n"
    body = 'print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "99.9%" in t][0].split("/")[-1]}, ensure_ascii=False))\n'
    case("fs-20126", "哪个文件里写了可用性 99.9%？只回答文件名。", f, ["search_text"], body, value(["SLA说明.md"]), sub="E-search-multi", tt="find_file",
         desc="Finds two files by their quoted availability figures, one per turn, when no listing tool exists",
         extra=("那写 99.5% 的是哪个文件？同样只回答文件名。", value(["旧SLA.md"])), ref_text="Turn 1: search_text 99.9% -> SLA说明.md. Turn 2: search_text 99.5% -> 旧SLA.md.",
         why="Each figure appears in one file.")


@reg
def e7():
    body = 'print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "8443" in t][0].split("/")[-1]}))\n'
    case("fs-20127", "哪个配置文件里的端口是 8443？只回答文件名。", dict(BASE_ZH), ["search_text"], body, value(["prod.yaml"]), sub="E-search", tt="find_file",
         desc="Finds the config file holding a port number when no listing tool exists", ref_text="search_text query=8443 -> config/prod.yaml",
         why="The port is in one config file.")


@reg
def e8():
    f = dict(BASE_EN)
    body = 'print(json.dumps({"expected_string": [p for p in case["files"] if p.endswith("deploy.sh")][0]}))\n'
    case("fs-20128", "Where is deploy.sh? Path only.", f, ["bash"], body, value(["scripts/deploy.sh"]), sub="E-bash-multi", tt="find_file",
         desc="Finds a script, then counts all shell scripts, when no listing tool exists",
         extra=("How many .sh files are there in the whole project? Just the number.", value(["4"], token=True)),
         ref_text="Turn 1: bash find . -name deploy.sh. Turn 2: find . -name '*.sh' | wc -l -> 4.", why="Four .sh files in the tree.",
         scen_ref=(["find . -name deploy.sh", "find . -name '*.sh' | wc -l"], lambda out, read: None if "4" in out else "bad %r" % out))
