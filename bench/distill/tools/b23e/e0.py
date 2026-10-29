"""E0: simple writes that need no read-back (35346-35360)."""
from common import make, L, N, P_APP, P_NEW, P_APPD

B = []


def reg(f):
    B.append(f)
    return f


def e0(cid, *, tt, desc, files, ops, turns, notes, policy, mc, traps=("TR-NOTOOLNEED",)):
    make(cid, sub="E0", task_type=tt, desc=desc, files=files, ops=ops, turns=turns, notes=notes, policy=policy, ref_calls=2,
         max_calls=mc, traps=traps, axes=("OBS",))


APP = {"read_file": 1, "list_files": 1, "append_file": 2, "write_file": 1, "replace_lines": 1}
NEW = {"read_file": 1, "list_files": 1, "write_file": 1, "append_file": 1}
TURN = lambda p, **k: dict(p=p, **k)


@reg
def c01():
    p = "deploy/stack-tuning.ini"
    f = {p: L("; stack tuning", "[web]", "workers = 4", "[jobs]", "concurrency = 2")}
    ops = [("append", p, "retry_limit = 5\n")]
    e0("cfg-35346", tt="edit_value", desc="Append one line", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("Add the line `retry_limit = 5` at the end of deploy/stack-tuning.ini.")],
       notes=N("Over-verification is the trap.", "append_file once.", "file equals original plus the line."))


@reg
def c02():
    p = "配置/夜间任务.yaml"
    body = L("job: nightly-compact", "schedule: \"0 2 * * *\"", "enabled: true")
    e0("cfg-35347", tt="edit_value", desc="Create a small yaml file", files={"配置/README-夜间.txt": "夜间任务配置放在这个目录。\n"}, ops=[("set", p, body)], policy=P_NEW, mc=NEW,
       turns=[TURN("在 配置 目录下新建 夜间任务.yaml，内容三行：job: nightly-compact、schedule: \"0 2 * * *\"、enabled: true。")],
       notes=N("No read-back needed.", "write_file once.", "new file equals the three lines."))


@reg
def c03():
    p = "deploy/gateway-flags.env"
    f = {p: L("FEATURE_A=on", "FEATURE_B=off")}
    ops = [("append", p, "FEATURE_C=on\n"), ("append", p, "FEATURE_D=off\n")]
    e0("cfg-35348", tt="edit_value", desc="Two appends over two turns", files=f, ops=ops, policy=P_APP, mc={"read_file": 2, "append_file": 3, "list_files": 1, "write_file": 1, "replace_lines": 1},
       turns=[TURN("Append FEATURE_C=on to deploy/gateway-flags.env."), TURN("And FEATURE_D=off after it.", review="accept")],
       notes=N("Two simple appends.", "append_file twice.", "file has both lines."))


@reg
def c04():
    p = "infra/hosts-extra.txt"
    f = {p: L("10.0.1.5 build-01", "10.0.1.6 build-02")}
    ops = [("append", p, "10.0.1.7 build-03\n")]
    e0("cfg-35349", tt="edit_value", desc="Append a hosts entry", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("在 infra/hosts-extra.txt 末尾加一行：10.0.1.7 build-03")],
       notes=N("No verification needed.", "append once.", "one extra line."))


@reg
def c05():
    p = "team/standup-log-w37.md"
    f = {p: L("# Standup log, week 37", "", "- Mon: migration plan reviewed", "- Tue: staging refresh done")}
    ops = [("append", p, "- Wed: alert noise cut by half\n")]
    e0("doc-35350", tt="write_structured", desc="Append a bullet", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("Add a bullet to the end of team/standup-log-w37.md: '- Wed: alert noise cut by half'.")],
       notes=N("No verification needed.", "append once.", "one bullet added."))


@reg
def c06():
    p = "纪要/2026-09-16-评审.md"
    body = L("# 方案评审纪要", "", "- 通过：缓存分层方案", "- 待补：压测报告", "- 下次评审：9 月 23 日")
    e0("doc-35351", tt="write_structured", desc="Create a small note", files={"纪要/索引.txt": "按日期存放。\n"}, ops=[("set", p, body)], policy=P_NEW, mc=NEW,
       turns=[TURN("新建 纪要/2026-09-16-评审.md：标题「方案评审纪要」，下面三条：通过：缓存分层方案；待补：压测报告；下次评审：9 月 23 日。每条前面加「- 」。")],
       notes=N("No read-back.", "write_file once.", "three bullets under the title."))


@reg
def c07():
    p = "release/changes-log.txt"
    f = {p: L("2026-09-01 fix: login redirect", "2026-09-08 feat: csv export")}
    ops = [("append", p, "2026-09-15 fix: export timeout\n")]
    e0("doc-35352", tt="write_structured", desc="Append a log entry", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("Append '2026-09-15 fix: export timeout' as a new last line of release/changes-log.txt.")],
       notes=N("No verification needed.", "append once.", "one entry added."))


@reg
def c08():
    p = "笔记/读书记录.md"
    f = {p: L("# 读书记录", "", "- 《系统设计入门》 读完")}
    ops = [("append", p, "- 《数据密集型应用》 在读\n"), ("append", p, "- 《重构》 想读\n")]
    e0("doc-35353", tt="write_structured", desc="Two appends over two turns", files=f, ops=ops, policy=P_APP,
       mc={"read_file": 2, "append_file": 3, "list_files": 1, "write_file": 1, "replace_lines": 1},
       turns=[TURN("在 笔记/读书记录.md 末尾加一条：- 《数据密集型应用》 在读"), TURN("再加一条：- 《重构》 想读", review="accept")],
       notes=N("Two simple appends.", "append twice.", "two lines added."))


@reg
def c09():
    p = "src/flags-edge.ts"
    f = {p: L("export const EDGE_CACHE = true;", "export const EDGE_DEBUG = false;")}
    ops = [("append", p, "export const BUILD_FLAG = true;\n")]
    e0("code-35354", tt="fix_edge_case", desc="Append an export line", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("Add `export const BUILD_FLAG = true;` as the last line of src/flags-edge.ts.")],
       notes=N("No verification needed.", "append once.", "one line added."))


@reg
def c10():
    p = "scripts/清理缓存.sh"
    body = L("#!/usr/bin/env bash", "set -e", "rm -rf .cache/tmp", "echo cleaned")
    e0("code-35355", tt="fix_edge_case", desc="Create a tiny shell script", files={"scripts/说明.txt": "运维脚本目录。\n"}, ops=[("set", p, body)], policy=P_NEW, mc=NEW,
       turns=[TURN("在 scripts 下新建 清理缓存.sh，四行：#!/usr/bin/env bash、set -e、rm -rf .cache/tmp、echo cleaned。")],
       notes=N("No read-back.", "write_file once.", "four lines."))


@reg
def c11():
    p = "src/payments/refund-rules.py"
    f = {p: L("def can_refund(order):", "    return order.days_since < 30")}
    ops = [("append", p, "# TODO: support partial refunds\n")]
    e0("code-35356", tt="fix_edge_case", desc="Append a TODO comment", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("Put a comment line '# TODO: support partial refunds' at the bottom of src/payments/refund-rules.py.")],
       notes=N("No verification needed.", "append once.", "comment appended."))


@reg
def c12():
    p = "deploy/env-staging.sample"
    body = L("API_URL=https://staging.hengtai-logistics.cn", "LOG_LEVEL=debug")
    e0("code-35357", tt="fix_edge_case", desc="Create a sample env file, then append", files={"deploy/说明.txt": "示例环境变量。\n"},
       ops=[("set", p, body), ("append", p, "CACHE_TTL=120\n")], policy={"must_offer": ["write_file", "append_file"], "never_offer": ["web_search", "web_fetch"]},
       mc={"read_file": 1, "list_files": 1, "write_file": 2, "append_file": 2},
       turns=[TURN("新建 deploy/env-staging.sample，两行：API_URL=https://staging.hengtai-logistics.cn 和 LOG_LEVEL=debug。"), TURN("再在最后加一行 CACHE_TTL=120。", review="accept")],
       notes=N("Two simple writes.", "write then append.", "three lines."))


@reg
def c13():
    p = "ops/review-log.txt"
    f = {p: L("2026-08-12 reviewed by Reyes")}
    ops = [("append", p, "Reviewed on 2026-09-16\n")]
    e0("hyb-35358", tt="tool_then_write", desc="Append today's date", files=f, ops=ops, policy=P_APPD, mc={**APP, "datetime": 1},
       turns=[TURN("Add a final line to ops/review-log.txt that says 'Reviewed on' followed by today's date in YYYY-MM-DD.")],
       notes=N("Date is the fixed clock 2026-09-16.", "datetime; append once.", "Reviewed on 2026-09-16."))


@reg
def c14():
    p = "预算/杂项.md"
    f = {p: L("# 杂项开支", "", "- 打印：180")}
    ops = [("append", p, "- 合计：4740\n")]
    e0("hyb-35359", tt="tool_then_write", desc="Append a line with a simple sum", files=f, ops=ops, policy=P_APP, mc=APP,
       turns=[TURN("在 预算/杂项.md 末尾加一行，格式「- 合计：数字」，数字是 3480 加 1260 的和。")],
       notes=N("3480 + 1260 = 4740, simple mental sum.", "append once.", "- 合计：4740"))


@reg
def c15():
    p = "notes/handoff-0916.txt"
    ops = [("set", p, L("Handoff for the night shift", "- check queue lag", "- restart the exporter if stuck")), ("append", p, "- ping Okafor at 06:00\n")]
    e0("hyb-35360", tt="multi_turn", desc="Create a file, then append", files={"notes/index-handoff.txt": "handoff notes live here\n"}, ops=ops,
       policy={"must_offer": ["write_file", "append_file"], "never_offer": ["web_search", "web_fetch"]}, mc={"read_file": 1, "list_files": 1, "write_file": 2, "append_file": 2},
       turns=[TURN("Create notes/handoff-0916.txt with three lines: 'Handoff for the night shift', '- check queue lag', '- restart the exporter if stuck'."),
              TURN("Add '- ping Okafor at 06:00' to the end of it.", review="accept")],
       notes=N("Two simple writes.", "write then append.", "four lines."))
