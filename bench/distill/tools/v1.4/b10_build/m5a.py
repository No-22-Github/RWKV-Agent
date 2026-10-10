"""M5 (v1.4 §3.5) pilot, part A: in-place edits that keep comments and indentation; multi-line ranges."""
from common import write_case

READBACK = "Expected path: read target -> write -> read the same file back -> one-sentence answer."

# ---------------------------------------------------------------- cfg-8005
probe = """# 冷库温度探头配置
探头组: 北区一号库
采样间隔秒: 30        # 2026-07 校准后调整，勿删注释
告警上限: -16         # 单位 ℃
告警下限: -24         # 单位 ℃
上报地址: http://iot-gw.internal:8086/write
"""
ticket = "变更项: 告警上限\n新值: -18\n范围: 北区一号库探头，其余配置不变\n申请: 质检部 郝晓楠 2026-09-12\n"
write_case(
    "cfg-8005",
    desc="Change one probe threshold to the value in a change ticket, keeping the trailing comment and column alignment, then reply DONE",
    task_type="edit_value", family="fam-cfg-b10-probethreshold-01", level="L1", ref_calls=4,
    traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
    files={"配置/冷库探头.yaml": probe, "工单/GD-0732.txt": ticket,
           "README.md": "冷库物联网配置。配置改动以工单为准。\n"},
    case_expect={"files": {"配置/冷库探头.yaml": {"equals": probe.replace("告警上限: -16 ", "告警上限: -18 ")}}},
    turns=[{
        "prompt": "照 工单/GD-0732.txt 改一下 配置/冷库探头.yaml，注释和对齐都保持原样。改完回复 DONE。",
        "expect": {"output_contains": ["DONE"], "output_contains_any": ["-18"], "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
t = dict(l.split(": ", 1) for l in files["工单/GD-0732.txt"].splitlines() if ": " in l)
assert t["变更项"] == "告警上限"
lines = files["配置/冷库探头.yaml"].splitlines(keepends=True)
out = []
for l in lines:
    if l.startswith(t["变更项"] + ": "):
        old = l.split(": ", 1)[1].split()[0]
        l = l.replace(": " + old + " ", ": " + t["新值"] + " ", 1)
    out.append(l)
print(json.dumps({"files": {"配置/冷库探头.yaml": "".join(out)}}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-READONLY: 工单范围写明「其余配置不变」，采样间隔那一行还注明「勿删注释」。整文件重写、顺手改别的键、丢掉行尾注释或对齐空格，文件都不再逐字节相等。

## Reference solution
1. 读 工单/GD-0732.txt：告警上限 改为 -18，其余不变。
2. 读 配置/冷库探头.yaml：告警上限在第 4 行，「告警上限: -16         # 单位 ℃」。
3. replace_lines 第 4 行为「告警上限: -18         # 单位 ℃」（-16 与 -18 等宽，对齐不变）。
4. 回读 配置/冷库探头.yaml 确认只改了这一处。
终答：一句话说明改了哪个文件哪一项，例如「已按 GD-0732 把 配置/冷库探头.yaml 的告警上限从 -16 改成 -18，注释和对齐没动。」另起一行写 DONE。判据：文件逐字节等于预期（只改 -16→-18），终答含 DONE 和 -18。

## Why the answer is unique
工单只要求改一个键，新值明确；保留注释与对齐后，结果文件唯一。
''',
)

# ---------------------------------------------------------------- cfg-8006
ini = """[search]
image = registry.local/search:4.2.0
min_replicas = 3
max_replicas = 12  ; raised for Q4 peak (CHG-5521)
cpu_target = 65

[indexer]
image = registry.local/indexer:4.2.0
min_replicas = 1
max_replicas = 12  ; batch reindex window
cpu_target = 80
"""
write_case(
    "cfg-8006",
    desc="Lower one section's max_replicas in an INI file while keeping its inline change-ticket comment; another section has the same key and value",
    task_type="edit_value", family="fam-cfg-b10-replicacap-01", level="L1", ref_calls=3,
    traps=["TR-DECOY"], decoys={"TR-DECOY": None}, axes=["OBS"],
    files={"deploy/autoscale.ini": ini, "README.md": "Autoscaling limits per service. Keep change-ticket comments next to the values they explain.\n"},
    case_expect={"files": {"deploy/autoscale.ini": {"equals": ini.replace("max_replicas = 12  ; raised", "max_replicas = 9  ; raised")}}},
    turns=[{
        "prompt": "Lower the search service's max_replicas to 9 in deploy/autoscale.ini, and leave the change-ticket note on that line in place.",
        "expect": {"output_contains": ["9"], "output_contains_token": True, "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Autoscaling limits per service.")
text = case["files"]["deploy/autoscale.ini"]
assert text.startswith("[search]")
out, section = [], None
for l in text.splitlines(keepends=True):
    if l.startswith("["):
        section = l.strip()
    if section == "[search]" and l.startswith("max_replicas = "):
        l = "max_replicas = 9" + l[len("max_replicas = 12"):]
    out.append(l)
print(json.dumps({"files": {"deploy/autoscale.ini": "".join(out)}}))
''',
    notes='''
## Traps
- TR-DECOY: [indexer] also has `max_replicas = 12` (line 10). Editing that line, or both lines, leaves the file wrong; the decoy is a file state, so trap_decoys is null.

## Reference solution
1. Read deploy/autoscale.ini: [search] max_replicas is line 4, `max_replicas = 12  ; raised for Q4 peak (CHG-5521)`.
2. replace_lines line 4 with `max_replicas = 9  ; raised for Q4 peak (CHG-5521)`.
3. Read the file back to confirm only line 4 changed and [indexer] still says 12.
Final answer, one sentence: search's max_replicas in deploy/autoscale.ini is now 9 (line 4), with the CHG-5521 note kept; indexer is unchanged. Criteria: exact file content; output contains 9.

## Why the answer is unique
Only the [search] section is named; the comment must stay on the edited line, which fixes the replacement text.
''',
)

# ---------------------------------------------------------------- code-8002
settings = '''import os

DEBUG = os.environ.get("DEBUG") == "1"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "pg-main.internal",
        "PORT": 5432,  # direct to postgres
        "NAME": "orders",
        "CONN_MAX_AGE": 60,
    },
    "reporting": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "pg-replica.internal",
        "PORT": 5432,
        "NAME": "orders",
    },
}
'''
new_settings = settings.replace('"PORT": 5432,  # direct to postgres', '"PORT": 6432,  # pgbouncer')
write_case(
    "code-8002",
    desc="Point the default database at the connection pooler port in a Python settings module, updating the inline comment, keeping indentation and leaving the reporting database alone",
    task_type="fix_edge_case", family="fam-code-b10-poolerport-01", level="L1", ref_calls=3,
    traps=["TR-DECOY"], decoys={"TR-DECOY": None}, axes=["OBS"],
    files={"app/settings.py": settings, "docs/pgbouncer.md": "pgbouncer runs on each app host and listens on 6432. Point only the read-write (default) connection at it; the reporting replica stays direct.\n",
           "README.md": "Orders service (Django).\n"},
    case_expect={"files": {"app/settings.py": {"equals": new_settings}}},
    turns=[{
        "prompt": "Switch the default database in app/settings.py over to pgbouncer on port 6432, and change the comment on that line to just say pgbouncer.",
        "expect": {"output_contains": ["6432"], "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["docs/pgbouncer.md"].startswith("pgbouncer runs on each app host and listens on 6432")
assert files["README.md"].startswith("Orders service")
src = files["app/settings.py"]
old = '"PORT": 5432,  # direct to postgres'
assert src.count(old) == 1
print(json.dumps({"files": {"app/settings.py": src.replace(old, '"PORT": 6432,  # pgbouncer')}}))
''',
    notes='''
## Traps
- TR-DECOY: the reporting database also has `"PORT": 5432,` (line 16); it must stay at 5432.

## Reference solution
1. Read app/settings.py: the default entry's port is line 9, `        "PORT": 5432,  # direct to postgres` (8-space indent).
2. replace_lines line 9 with `        "PORT": 6432,  # pgbouncer`.
3. Read app/settings.py back to confirm indentation and that reporting is untouched.
Final answer, one sentence: default now connects on 6432 (pgbouncer) in app/settings.py line 9; reporting still goes direct on 5432. Criteria: exact file content; output contains 6432.

## Why the answer is unique
The prompt names the default database and the new comment text; indentation must be kept for valid Python, so only one resulting file is acceptable.
''',
)

# ---------------------------------------------------------------- cfg-8008
gw = """路由:
  /pay:
    上游: pay-svc:9000
    连接超时秒: 2
    读超时秒: 10
    写超时秒: 10
    重试次数: 1
  /refund:
    上游: refund-svc:9100
    连接超时秒: 2
    读超时秒: 10
    写超时秒: 10
    重试次数: 0
"""
gw_new = gw.replace("  /pay:\n    上游: pay-svc:9000\n    连接超时秒: 2\n    读超时秒: 10\n    写超时秒: 10\n",
                    "  /pay:\n    上游: pay-svc:9000\n    连接超时秒: 5\n    读超时秒: 5\n    写超时秒: 5\n")
assert gw_new != gw
write_case(
    "cfg-8008",
    desc="Set three consecutive timeout lines of one route to the same value; the next route has identical lines that must stay",
    task_type="edit_value", family="fam-cfg-b10-routetimeouts-01", level="L1", ref_calls=3,
    traps=["TR-DECOY"], decoys={"TR-DECOY": None}, axes=["OBS"],
    files={"网关/路由.yaml": gw, "README.md": "支付网关路由配置，缩进两格。\n"},
    case_expect={"files": {"网关/路由.yaml": {"equals": gw_new}}},
    turns=[{
        "prompt": "把 网关/路由.yaml 里 /pay 的连接、读、写三个超时都改成 5 秒，别的不动。",
        "expect": {"output_contains_any": ["/pay"], "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("支付网关路由配置")
lines = case["files"]["网关/路由.yaml"].splitlines(keepends=True)
start = lines.index("  /pay:\\n")
end = next(i for i in range(start + 1, len(lines)) if not lines[i].startswith("    "))
for i in range(start + 1, end):
    key = lines[i].strip().split(":")[0]
    if key in ("连接超时秒", "读超时秒", "写超时秒"):
        lines[i] = "    %s: 5\\n" % key
print(json.dumps({"files": {"网关/路由.yaml": "".join(lines)}}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-DECOY: /refund 下面有完全相同的三行超时（第 10–12 行），只能改 /pay 的第 4–6 行。

## Reference solution
1. 读 网关/路由.yaml：/pay 的三行超时在第 4–6 行（连接 2、读 10、写 10）。
2. replace_lines start_line 4、end_line 6，content 三行：「    连接超时秒: 5」「    读超时秒: 5」「    写超时秒: 5」（四格缩进）。
3. 回读确认 /refund 未变。
终答一句话：已把 网关/路由.yaml 中 /pay 的连接、读、写超时（第 4–6 行）都改成 5 秒，/refund 没动。判据：文件逐字节相等；终答提到 /pay。

## Why the answer is unique
三行连续，行号范围必须正好覆盖 4–6；缩进要保持四格，结果唯一。
''',
)

# ---------------------------------------------------------------- doc-8005
kpi = """# Support KPI targets, FY2026

| Quarter | First response (h) | Resolution (h) | CSAT (%) |
|---|---|---|---|
| Q1 | 4 | 48 | 88 |
| Q2 | 4 | 40 | 89 |
| Q3 | 3 | 36 | 90 |
| Q4 | 3 | 36 | 90 |

Targets are reviewed each quarter by the support leads.
"""
kpi_new = kpi.replace("| Q3 | 3 | 36 | 90 |\n| Q4 | 3 | 36 | 90 |", "| Q3 | 2 | 30 | 91 |\n| Q4 | 2 | 28 | 92 |")
write_case(
    "doc-8005",
    desc="Replace two adjacent rows of a KPI table with new targets given in the prompt",
    task_type="write_structured", family="fam-doc-b10-kpitargets-01", level="L0", ref_calls=3,
    axes=[],
    files={"docs/kpi-targets.md": kpi, "docs/leads.md": "Support leads: Amara Osei (EMEA), Jun Takeda (APAC).\n"},
    case_expect={"files": {"docs/kpi-targets.md": {"equals": kpi_new}}},
    turns=[{
        "prompt": "The support leads agreed new targets for the second half. In docs/kpi-targets.md, set Q3 to 2 h first response, 30 h resolution, 91% CSAT, and Q4 to 2 h, 28 h, 92%.",
        "expect": {"output_contains_any": ["Q3"], "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
text = case["files"]["docs/kpi-targets.md"]
assert text.startswith("# Support KPI targets")
assert case["files"]["docs/leads.md"].startswith("Support leads:")
new = {"Q3": "| Q3 | 2 | 30 | 91 |", "Q4": "| Q4 | 2 | 28 | 92 |"}
out = []
for l in text.splitlines(keepends=True):
    for q, row in new.items():
        if l.startswith("| %s |" % q):
            l = row + "\\n"
    out.append(l)
print(json.dumps({"files": {"docs/kpi-targets.md": "".join(out)}}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. Read docs/kpi-targets.md: Q3 and Q4 rows are lines 7 and 8.
2. replace_lines start_line 7, end_line 8 with the two rows `| Q3 | 2 | 30 | 91 |` and `| Q4 | 2 | 28 | 92 |`.
3. Read the file back.
Final answer, one sentence: Q3 and Q4 rows in docs/kpi-targets.md now carry the new targets (2/30/91 and 2/28/92). Criteria: exact file content; output mentions Q3.

## Why the answer is unique
The prompt gives every new value; the table format is fixed, so the resulting file is unique.
''',
)
