"""G0 controls (answer on the first screen, the question asks about the head of the file): ids 35531..35540."""
import random

import fill
from common import make, T

B = []


def reg(f):
    B.append(f)
    return f


def R(k):
    return random.Random("b23g-g0-" + k)


@reg
def a01():
    r = R("01")
    bl = fill.changelog_blocks(r, top=(4, 8, 2), n_blocks=100)
    header = ["# Orchard SDK release notes", "", "Newest release first."]
    ps = [(300, ["", "Archive note: releases before 3.0 live in the legacy file; the last entry there is 2.9.7."])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("doc-35531", sub="G0", task_type="latest_version", desc="Changelog, question about the top entry",
         path="docs/relnotes-orchard-sdk.md", lines=lines,
         turns=[T("What is the newest release listed at the top of docs/relnotes-orchard-sdk.md?", "4.8.2", "## 4.8.2 - ", None,
                  excl=["2.9.7"], deep="the last entry there is 2.9.7")],
         notes=("The long file tempts paging, but the question is about the top.", "read_file once -> 4.8.2.", "Only the first release heading is the top one."))


@reg
def a02():
    r = R("02")
    bl = fill.en_doc_blocks(r, 160)
    header = ["# Quillpad contributor handbook", "", "Owner: Dana Ostrowski", "Version: 3.2 (2026-08-18)", ""]
    ps = [(300, ["", "Template maintained by: Hugh Marlowe (template version 1.9)", ""])]
    lines = fill.compose(bl, ps, header=header, n=480)
    make("doc-35532", sub="G0", task_type="lookup_value", desc="Handbook header owner, a template maintainer line far below",
         path="docs/handbook-intro-quillpad.md", lines=lines,
         turns=[T("Who owns the handbook, according to the header of docs/handbook-intro-quillpad.md?", "Dana Ostrowski", "Owner: Dana Ostrowski", None,
                  excl=["Hugh Marlowe"], deep="Template maintained by: Hugh Marlowe")],
         notes=("A later line names another person.", "read_file once -> Dana Ostrowski.", "The header line says Owner."))


@reg
def a03():
    r = R("03")
    bl = fill.zh_doc_blocks(r, 170)
    header = ["# 数据治理规范（第 3 版）", "", "生效日期：2026-03-01", "适用范围：全部对外数据接口", ""]
    ps = [(310, ["", "修订历史：第 2 版生效日期为 2025-07-15，现已废止。"])]
    lines = fill.compose(bl, ps, header=header, n=480)
    make("doc-35533", sub="G0", task_type="lookup_value", desc="数据治理规范开头的生效日期，后部有旧版日期",
         path="文档/数据治理规范-v3.md", lines=lines,
         turns=[T("文档/数据治理规范-v3.md 开头写的这一版是哪天生效的？", "2026-03-01", "生效日期：2026-03-01", None, excl=["2025-07-15"],
                  deep="第 2 版生效日期为 2025-07-15")],
         notes=("后部修订历史里有旧版日期。", "read_file 一次 -> 2026-03-01。", "开头一行就是生效日期。"))


@reg
def a04():
    r = R("04")
    base, times = fill.log_lines(r, 560, day=(2026, 9, 26))
    lines = list(base)
    lines.insert(400, "%s INFO  sync: agent restarted, previous segment began 2026-09-25 23:41:17" % fill.stamp("app", (2026, 9, 26), times[400]))
    first = lines[0].split()[0]
    make("log-35534", sub="G0", task_type="lookup_value", desc="Sync agent log, question about the very first line",
         path="logs/sync-agent-0926.log", lines=lines,
         turns=[T("What time does the first line of logs/sync-agent-0926.log show?", first, lines[0][:8], None, excl=["23:41:17"],
                  deep="previous segment began 2026-09-25 23:41:17")],
         notes=("A restart line far below mentions another time.", "read_file once -> first timestamp.", "The first line is unique."))


@reg
def a05():
    r = R("05")
    pl = [(0, lambda ts: "%s INFO  对账: 任务启动 批次号=BATCH-20260928-07" % ts),
          (420, lambda ts: "%s WARN  对账: 发现上一批遗留数据 批次号=BATCH-20260927-31" % ts)]
    lines = fill.log_with_plants(r, 540, pl, lang="zh", day=(2026, 9, 28))
    make("log-35535", sub="G0", task_type="lookup_value", desc="对账任务日志开头的批次号，后部有遗留批次",
         path="logs/对账任务-0928.log", lines=lines,
         turns=[T("logs/对账任务-0928.log 开头那次任务启动的批次号是什么？", "BATCH-20260928-07", "任务启动 批次号=BATCH-20260928-07", None,
                  excl=["20260927-31"], deep="上一批遗留数据 批次号=BATCH-20260927-31")],
         notes=("后部提到另一个批次号。", "read_file 一次 -> BATCH-20260928-07。", "任务启动只有第一行。"))


@reg
def a06():
    r = R("06")
    bl = fill.yaml_blocks(r, 90)
    header = ["# ledger stack defaults", "schema_version: 2026.2", "owner_team: platform-core"]
    ps = [(310, ["", "legacy-import:", "  schema_version: 2025.4", "  enabled: false"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("cfg-35536", sub="G0", task_type="lookup_value", desc="YAML top-level schema_version, legacy block far below",
         path="deploy/ledger-stack-defaults.yaml", lines=lines,
         turns=[T("What schema_version is declared at the top of deploy/ledger-stack-defaults.yaml?", "2026.2", "schema_version: 2026.2", None,
                  excl=["2025.4"], deep="schema_version: 2025.4")],
         notes=("The legacy-import block far below has another schema_version.", "read_file once -> 2026.2.", "Top-level key is on line 2."))


@reg
def a07():
    r = R("07")
    bl = fill.ini_blocks(r, 90)
    header = ["; kiln agent settings", "; maintainer: platform-infra@lumenstack.io", "; last reviewed 2026-07-02"]
    ps = [(310, ["", "[legacy]", "; contact: ops-legacy@lumenstack.io"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("cfg-35537", sub="G0", task_type="lookup_value", desc="INI header maintainer, legacy contact far below",
         path="conf/kiln-agent.ini", lines=lines,
         turns=[T("Who is listed as the maintainer in the header comments of conf/kiln-agent.ini?", "platform-infra@lumenstack.io",
                  "maintainer: platform-infra@lumenstack.io", None, excl=["ops-legacy@lumenstack.io"], deep="contact: ops-legacy@lumenstack.io")],
         notes=("A legacy contact appears far below.", "read_file once -> platform-infra@lumenstack.io.", "Header comment names the maintainer."))


@reg
def a08():
    r = R("08")
    bl = fill.toml_blocks(r, 90)
    header = ["# 调度器基线配置", "# 配置负责人：韩晓梅", ""]
    ps = [(310, ["", "[legacy.contact]", "# 备选联系人：吕建国"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("cfg-35538", sub="G0", task_type="lookup_value", desc="TOML 文件头的配置负责人，后部有备选联系人",
         path="配置/调度器基线.toml", lines=lines,
         turns=[T("配置/调度器基线.toml 文件开头写的配置负责人是谁？", "韩晓梅", "配置负责人：韩晓梅", None, excl=["吕建国"], deep="备选联系人：吕建国")],
         notes=("后部有另一个联系人。", "read_file 一次 -> 韩晓梅。", "文件头第二行写明负责人。"))


@reg
def a09():
    r = R("09")
    bl = fill.py_blocks(r, 70)
    header = ['"""Key rotation helpers."""', "", '__version__ = "1.14.0"', "", "import time"]
    ps = [(310, ["", "", 'LEGACY_VERSION = "0.9.3"'])]
    lines = fill.compose(bl, ps, header=header, n=480)
    make("code-35539", sub="G0", task_type="lookup_value", desc="Python __version__ near the top, legacy version constant far below",
         path="src/vault/key_rotation.py", lines=lines,
         turns=[T("What does __version__ say in src/vault/key_rotation.py?", "1.14.0", '__version__ = "1.14.0"', None, excl=["0.9.3"],
                  deep='LEGACY_VERSION = "0.9.3"')],
         notes=("A LEGACY_VERSION constant far below.", "read_file once -> 1.14.0.", "__version__ is on line 3."))


@reg
def a10():
    r = R("10")
    bl = fill.go_blocks(r, 70)
    header = ["package telemetry", "", "import (", '\t"context"', '\t"strings"', '\t"sync"', ")"]
    ps = [(300, ["", "// legacy package metricsv1 is kept for the old dashboards."]),
          (380, ["", '// the old exporter also imported "net/http/pprof".'])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("code-35540", sub="G0", task_type="lookup_value", desc="Go file head: package name and first import, two look-alike comments far below",
         path="internal/metrics/exporter.go", lines=lines,
         turns=[T("What package name does internal/metrics/exporter.go declare?", "telemetry", "package telemetry", None, excl=["metricsv1"],
                  deep="legacy package metricsv1"),
                T("And what is the first import in its import block?", "context", '\t"context"', None, excl=["pprof"], deep="net/http/pprof")],
         notes=("Comments far below mention another package and another import.", "read_file once; the second turn is answered from the same screen.",
                "Both facts are in the first 8 lines."))
