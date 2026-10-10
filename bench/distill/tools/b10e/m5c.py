"""M5 (v1.4 §3.5) b10e: edit a value according to another file (lock / change ticket / approval record / official web page)."""
import json
import re

from common import revised
write_case = revised({'cfg-8665': 'S5：审批记录里月度上限 50000 也是「已批准」，题面「照批准的改」下两项都改才对；AP-2240 改为「待审批」。', 'cfg-8666': 'S5：词表补「改为 7 / 改成 7」——老师写「由 9 改为 7」被判挂。', 'cfg-8667': 'S5：题面补「行尾注释别动」——原题面没说，老师顺手更新了注释，文件精确比对判挂。', 'cfg-8671': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'cfg-8673': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8600': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8601': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8602': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8604': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8606': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8609': 'S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。', 'hyb-8603': 'S5：query_match「松江市社保」缩为「松江」——老师搜索词把城市与「社保」分开写，三遍搜索全部零结果。'})

VERIFY = '''
import json
import re

case = json.load(open("case.json"))
files = case["files"]
{WEBLOAD}
assert files["README.md"].startswith({README_HEAD})
assert basis.startswith({BASIS_HEAD})
m = re.search({BRE}, basis, re.M)
val = m.group(1)
src = files[{TARGET}]
old = {TLINE}
assert src.count(old) == 1
new = src.replace(old, {TMPL}.replace("{{V}}", val))
print(json.dumps({{"files": {{{TARGET}: new}}}}, ensure_ascii=False))
'''


def spec(cid, fam, zh, task_type, desc, basis_path, basis, target_path, target, tline, tmpl, bre,
         prompt, done, ans, decoy, readme, extra=None, web=None, web_url=None, level="L1", why=None, anys=None, alts=None):
    """basis_path None + web_url -> the basis is the content of that web fixture entry."""
    task_type = {"code": "fix_edge_case", "hyb": "web_then_edit"}.get(cid[:3 if cid[:3] == "hyb" else 4], task_type)
    val = re.search(bre, basis, re.M).group(1)
    assert target.count(tline) == 1, cid
    new_line = tmpl.replace("{V}", val)
    assert new_line not in target, cid
    new_target = target.replace(tline, new_line)
    lineno = target[:target.index(tline)].count("\n") + 1
    files = {target_path: target, "README.md": readme}
    if basis_path:
        files[basis_path] = basis
        webload = "basis = files[%r]" % basis_path
    else:
        webload = "basis = [w for w in case['web_fixture'] if w['url'] == %r][0]['content']" % web_url
    files.update(extra or {})
    # DONE replies and bare 1-2 digit values are not checked in the text; the file equality is the gate.
    anyl = anys or (None if done or re.fullmatch(r"\d{1,2}", val) else [val])
    expect = {"max_output_chars": 400 if not web else 500}
    if anyl:
        expect["output_contains_any"] = anyl
    if done:
        expect["output_contains"] = ["DONE"]
    if web:
        expect["required_tools"] = ["web_fetch"]
    assert (not anyl or any(a in ans for a in anyl)) and (not done or ans.rstrip().endswith("DONE")), cid
    assert len(ans) <= expect["max_output_chars"], cid
    traps = ["TR-DECOY"] + (["TR-WEBSTALE"] if web else [])
    verify = VERIFY.format(WEBLOAD=webload, README_HEAD=repr(readme[:10]), BASIS_HEAD=repr(basis[:12]), BRE=repr(bre), TARGET=repr(target_path),
                           TLINE=repr(tline), TMPL=repr(tmpl))
    src_name = basis_path or web_url
    if zh:
        notes = """
## Traps
- TR-DECOY: %s

## Reference solution
1. 读依据 %s，取出新值 %s。
2. 读 %s：要改的是第 %d 行「%s」。
3. replace_lines 第 %d 行为「%s」（同行其余内容和格式不动）。
4. 回读 %s 确认。
终答示例：%s
判据：目标文件逐字节等于预期%s。

## Why the answer is unique
%s
""" % (decoy, src_name, val, target_path, lineno, tline, lineno, new_line, target_path,
       ans.replace("\n", " / "), "；终答含 DONE" if done else "", why or "依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。")
    else:
        notes = """
## Traps
- TR-DECOY: %s

## Reference solution
1. Read the basis %s: the new value is %s.
2. Read %s: line %d, `%s`, is the one to change.
3. replace_lines line %d with `%s`; the rest of the line stays.
4. Read %s back to confirm.
Final answer example: %s
Criteria: exact target file content%s.

## Why the answer is unique
%s
""" % (decoy, src_name, val, target_path, lineno, tline, lineno, new_line, target_path,
       ans.replace("\n", " / "), "; output contains DONE" if done else "",
       why or "Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.")
    if web:
        assert alts and len(alts) == 5 and all(w[0]["query_match"].lower() in a.lower() for a in alts for w in [web]), cid
        notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    write_case(
        cid, desc=desc, task_type=task_type, family=fam, level=level, ref_calls=5 if web else 4,
        traps=traps, decoys={t: None for t in traps}, axes=["OBS"] + (["VER"] if web else []),
        files=files, web=web, case_expect={"files": {target_path: {"equals": new_target}}},
        turns=[{"prompt": prompt, "expect": expect}], verify=verify, notes=notes)

# ======================================================================= cfg (20)
# ---- Chinese (9)
spec("cfg-8665", "fam-cfg-b10e-purchasecap-01", True, "edit_value",
     "Set a purchase cap to the value in the approval log; a rejected request and a different cap are decoys",
     "审批/记录.txt",
     "AP-2231 | 单笔上限 | 8000 | 驳回（超预算）\nAP-2236 | 单笔上限 | 12000 | 已批准 2026-09-03\nAP-2240 | 月度上限 | 50000 | 待审批\n",
     "配置/采购限额.yaml",
     "部门: 行政部\n单笔上限: 5000   # 财务部 2026-05 核定\n月度上限: 30000\n",
     "单笔上限: 5000", "单笔上限: {V}", r"单笔上限 \| (\d+) \| 已批准",
     "审批/记录.txt 里行政部的采购限额申请有结果了，照批准的把 配置/采购限额.yaml 改过来，行尾注释留着。",
     False, "已按审批记录 AP-2236 把 配置/采购限额.yaml 的单笔上限从 5000 改成 12000，注释保留。",
     "审批记录里 AP-2231 的 8000 已驳回，月度上限 50000 是另一个字段；取错行或错字段都会写错值。",
     "行政部采购限额配置，数值以审批记录中已批准的为准。\n", anys=['12000', '12,000'])

spec("cfg-8666", "fam-cfg-b10e-drugfridge-01", True, "edit_value",
     "Apply the approved alarm threshold from a change ticket to the right fridge; a second ticket for another fridge and a withdrawn ticket are decoys",
     "变更/药房冷柜工单.txt",
     "工单 BG-301 设备: 冷柜A 告警上限: 8 状态: 已撤回\n工单 BG-305 设备: 冷柜B 告警上限: 6 状态: 已执行\n工单 BG-309 设备: 冷柜A 告警上限: 7 状态: 已审批\n",
     "配置/冷柜告警.ini",
     "[冷柜A]\n告警上限 = 9  ; 单位 ℃\n[冷柜B]\n告警上限 = 6  ; 单位 ℃\n",
     "告警上限 = 9  ; 单位 ℃", "告警上限 = {V}  ; 单位 ℃", r"设备: 冷柜A 告警上限: (\d+) 状态: 已审批",
     "药房冷柜A的告警上限要按已经批下来的变更工单改，工单在 变更/ 目录下。配置/冷柜告警.ini 里注释别动。",
     False, "配置/冷柜告警.ini 里冷柜A的告警上限已改成 7 ℃，依据是已审批的工单 BG-309，冷柜B没动。",
     "冷柜A有两张工单：BG-301 已撤回（8），BG-309 已审批（7）；冷柜B的 6 与目标无关。目标文件里冷柜A、B 各有一行告警上限，只能改 A 段。",
     "药房冷链配置。\n", anys=['7 ℃', '7℃', '7 度', '7度', '改为 7', '改成 7', '为 7'])

spec("cfg-8667", "fam-cfg-b10e-rentindex-01", True, "edit_value",
     "Update a rent figure in a lease config from the signed amendment; an unsigned draft amendment has a different amount",
     "合同/补充协议汇总.md",
     "# 补充协议汇总\n\n- 补充协议一（草案，未签）：月租 18600 元\n- 补充协议二（2026-08-20 双方盖章生效）：月租 17200 元\n- 补充协议三（仅停车位，月租 1500 元）\n",
     "配置/铺面租金.yaml",
     "铺面: 东街12号\n月租: 16000   # 2025 年起\n押金: 32000\n",
     "月租: 16000", "月租: {V}", r"盖章生效）：月租 (\d+) 元",
     "东街12号铺面的租金按最新生效的补充协议调一下，配置/铺面租金.yaml 里改，行尾注释别动。",
     False, "已按 2026-08-20 生效的补充协议二把 配置/铺面租金.yaml 的月租改为 17200，草案里的 18600 未采用。",
     "草案 18600 未签，补充协议三的 1500 是停车位租金，不是铺面月租。",
     "铺面租金配置，数值来自已签署的合同文件。\n", anys=['17200', '17,200'])

spec("cfg-8668", "fam-cfg-b10e-nginxpool-01", True, "edit_value",
     "Copy the pool size for one service from the capacity plan into its config; the plan has a column for the previous year",
     "容量规划.csv",
     "服务,2025 连接池,2026 连接池\n订单,40,64\n库存,24,32\n通知,16,20\n",
     "conf/pools.conf",
     "# pools.conf\n订单.pool_size = 40\n库存.pool_size = 24\n通知.pool_size = 16\n",
     "库存.pool_size = 24", "库存.pool_size = {V}", r"库存,\d+,(\d+)",
     "库存服务的连接池大小改成容量规划.csv 里 2026 年的数，在 conf/pools.conf 里改，其它服务别碰。",
     False, "conf/pools.conf 里库存服务的 pool_size 已从 24 改为 32，取自容量规划.csv 的 2026 年列。",
     "容量规划表有 2025 和 2026 两列，2025 年的 24 正是配置里的现值；订单、通知的行也在表里。",
     "连接池配置，各服务一行。\n")
spec("cfg-8669", "fam-cfg-b10e-shiftrate-01", True, "edit_value",
     "Set an hourly wage to the approved level from an HR memo with several grades",
     "人事/薪级通知.txt",
     "2026 年 10 月起薪级调整（已定稿）：\n  初级技工 小时工资 32 元\n  中级技工 小时工资 41 元\n  高级技工 小时工资 55 元\n（9 月版：中级技工 38 元，已作废）\n",
     "配置/工资表参数.yaml",
     "初级技工: 30\n中级技工: 38   # 小时工资，元\n高级技工: 52\n",
     "中级技工: 38", "中级技工: {V}", r"中级技工 小时工资 (\d+) 元",
     "人事发了新的薪级通知，把 配置/工资表参数.yaml 里中级技工的小时工资更新一下。改完回复 DONE。",
     True, "配置/工资表参数.yaml 里中级技工的小时工资已按 10 月薪级通知从 38 改为 41，注释没动。\nDONE",
     "通知里 38 元是已作废的 9 月版，恰好等于配置现值；初级 32、高级 55 是别的级别。",
     "工资表参数，数值取自人事薪级通知。\n")
spec("cfg-8670", "fam-cfg-b10e-nodelock-01", True, "edit_value",
     "Pin a dependency in package.json to the version resolved in the lock file; a similarly named package has another version",
     "package-lock.json",
     '{\n  "packages": {\n    "node_modules/dayjs": {"version": "1.11.13"},\n    "node_modules/dayjs-plugin-utc": {"version": "0.9.2"},\n    "node_modules/lodash": {"version": "4.17.21"}\n  }\n}\n',
     "package.json",
     '{\n  "name": "shop-admin",\n  "dependencies": {\n    "dayjs": "1.10.7",\n    "lodash": "4.17.21"\n  }\n}\n',
     '"dayjs": "1.10.7"', '"dayjs": "{V}"', r'node_modules/dayjs": \{"version": "([^"]+)"',
     "package.json 里 dayjs 钉的版本比 package-lock.json 落地的旧，改成锁文件里的版本。",
     False, "package.json 里 dayjs 已从 1.10.7 改为 1.11.13，与 package-lock.json 一致。",
     "锁文件里 dayjs-plugin-utc 的 0.9.2 紧跟在 dayjs 后面；lodash 已一致。",
     "后台前端。版本以 package-lock.json 为准。\n", level="L1")
spec("cfg-8671", "fam-cfg-b10e-clinicslot-01", True, "edit_value",
     "Change one clinic's slot length per the scheduling committee minutes; a proposal that was voted down is a decoy",
     "会议/排班委员会纪要.md",
     "## 2026-09-10 纪要\n\n1. 提案：门诊每号时长改 15 分钟——表决未通过。\n2. 提案：专家门诊每号时长改 20 分钟——表决通过，自 9 月 1 日起执行。\n3. 提案：急诊分诊每号 5 分钟——维持现状。\n",
     "配置/号源.yaml",
     "普通门诊:\n  每号分钟: 10\n专家门诊:\n  每号分钟: 15   # 2026-03 起\n急诊分诊:\n  每号分钟: 5\n",
     "  每号分钟: 15   # 2026-03 起", "  每号分钟: {V}   # 2026-03 起", r"专家门诊每号时长改 (\d+) 分钟——表决通过",
     "专家门诊的每号时长按排班委员会纪要里通过的那条改，在 配置/号源.yaml 里。",
     False, "配置/号源.yaml 里专家门诊的每号分钟已从 15 改为 20 分钟，依据是 9 月 10 日纪要中表决通过的第 2 条。",
     "纪要里 15 分钟的提案属于普通门诊且未通过（而 15 恰是专家门诊现值）；急诊 5 分钟维持现状。",
     "门诊号源配置。\n", anys=['20 分钟','20分钟'])

spec("cfg-8672", "fam-cfg-b10e-rustlock-01", True, "edit_value",
     "Bump one crate in Cargo.toml to the version in Cargo.lock; a crate with a shared prefix has another version",
     "Cargo.lock",
     '[[package]]\nname = "serde"\nversion = "1.0.210"\n\n[[package]]\nname = "serde_json"\nversion = "1.0.128"\n\n[[package]]\nname = "tokio"\nversion = "1.40.0"\n',
     "Cargo.toml",
     '[package]\nname = "ingest"\nversion = "0.3.0"\n\n[dependencies]\nserde = "1.0.190"\nserde_json = "1.0.128"\ntokio = "1.40.0"\n',
     'serde = "1.0.190"', 'serde = "{V}"', r'name = "serde"\nversion = "([^"]+)"',
     "Cargo.toml 里 serde 的版本落后于 Cargo.lock，按锁文件改，serde_json 不用管。",
     False, "Cargo.toml 的 serde 已从 1.0.190 改为 1.0.210，与 Cargo.lock 一致；serde_json 没动。",
     "serde_json 的 1.0.128 与 serde 同前缀，读错块会写成 1.0.128。",
     "数据接入服务。\n")
spec("cfg-8673", "fam-cfg-b10e-feeschedule-01", True, "edit_value",
     "Set a fee from the latest notice among several dated notices in one file",
     "公告/收费通知.txt",
     "【2026-01-05】停车费调整为 每小时 4 元\n【2026-06-18】停车费调整为 每小时 5 元\n【2026-09-01】停车费调整为 每小时 6 元（自 2026-09-01 起）\n【2026-03-02】洗车费 每次 15 元\n",
     "配置/园区收费.yaml",
     "停车费每小时: 5   # 元\n洗车费每次: 15\n",
     "停车费每小时: 5", "停车费每小时: {V}", r"调整为 每小时 (\d+) 元（自 2026-09-01 起）",
     "园区的停车费要按最新的收费通知调整，配置/园区收费.yaml 里改成通知里的数，注释保留。",
     False, "配置/园区收费.yaml 的停车费每小时已从 5 改为 6，依据是 2026-09-01 的收费通知，注释保留。",
     "通知文件按非时间顺序排列，且含多次调整；最新的是 9 月 1 日那条（6 元），6 月的 5 元正是现值。",
     "园区收费配置。\n", anys=['改为 6', '改成 6', '6 元', '6元'])

# ---- English (11)

spec("cfg-8674", "fam-cfg-b10e-rateplan-01", False, "edit_value",
     "Set an API rate limit from the signed order form; an expired quote and another tier are decoys",
     "contracts/order-form-2026Q3.txt",
     "Quote Q-118 (expired 2026-06-30): Pro tier 600 requests/min\nOrder form OF-2209 (signed 2026-08-14): Pro tier 900 requests/min; Basic tier 120 requests/min\n",
     "config/ratelimit.yaml",
     "tier: pro\nrequests_per_min: 600   # per API key\nburst: 50\n",
     "requests_per_min: 600", "requests_per_min: {V}", r"signed 2026-08-14\): Pro tier (\d+) requests/min",
     "We upgraded our API contract. Update the Pro tier limit in config/ratelimit.yaml to what the signed order form says, comment left as is.",
     False, "config/ratelimit.yaml now has requests_per_min: 900 for Pro, from signed order form OF-2209; the expired quote's 600 is not used.",
     "The expired quote still shows 600 (the current value); the Basic tier line has a different number.",
     "Rate limit config for the public API.\n")
spec("cfg-8675", "fam-cfg-b10e-pylock-01", False, "edit_value",
     "Pin a requirement to the version in poetry.lock; a package with a near-identical name sits just above",
     "poetry.lock",
     '[[package]]\nname = "requests-oauthlib"\nversion = "2.0.0"\n\n[[package]]\nname = "requests"\nversion = "2.32.3"\n\n[[package]]\nname = "urllib3"\nversion = "2.2.2"\n',
     "requirements.txt",
     "flask==3.0.3\nrequests==2.31.0\nurllib3==2.2.2\n",
     "requests==2.31.0", "requests=={V}", r'name = "requests"\nversion = "([^"]+)"',
     "requests in requirements.txt is behind poetry.lock. Bump the pin to the locked version",
     False, "requirements.txt now pins requests==2.32.3, the version in poetry.lock.",
     "requests-oauthlib (2.0.0) is listed right before requests in the lock.",
     "Deploy installs from requirements.txt; poetry.lock is authoritative.\n")
spec("cfg-8676", "fam-cfg-b10e-gologmod-01", False, "edit_value",
     "Update a Go module requirement to the version listed in the vendor manifest; a sibling module from the same org differs",
     "vendor/modules.txt",
     "# github.com/jackc/pgx/v5 v5.6.0\n# github.com/jackc/pgconn v1.14.3\n# github.com/rs/zerolog v1.33.0\n",
     "go.mod",
     "module example.com/billing\n\ngo 1.22\n\nrequire (\n\tgithub.com/jackc/pgx/v5 v5.4.3\n\tgithub.com/rs/zerolog v1.33.0\n)\n",
     "github.com/jackc/pgx/v5 v5.4.3", "github.com/jackc/pgx/v5 {V}", r"# github.com/jackc/pgx/v5 (v[\d.]+)",
     "go.mod asks for an older pgx than what vendor/modules.txt actually vendors. Make go.mod match the vendored version.",
     False, "go.mod now requires github.com/jackc/pgx/v5 v5.6.0, matching vendor/modules.txt; pgconn was left alone.",
     "pgconn is from the same org with a different version (v1.14.3).",
     "Billing service, Go modules with vendoring.\n")
spec("cfg-8677", "fam-cfg-b10e-retention-01", False, "edit_value",
     "Apply the retention days from the approved record; a rejected change request for the same setting exists",
     "approvals/log-retention.txt",
     "CR-77 | log retention | 365 days | REJECTED (cost)\nCR-81 | log retention | 120 days | APPROVED 2026-09-09\nCR-82 | metrics retention | 30 days | APPROVED 2026-09-09\n",
     "config/retention.env",
     "LOG_RETENTION_DAYS=90\nMETRICS_RETENTION_DAYS=15\n",
     "LOG_RETENTION_DAYS=90", "LOG_RETENTION_DAYS={V}", r"log retention \| (\d+) days \| APPROVED",
     "Set LOG_RETENTION_DAYS in config/retention.env to what was approved in the approval log.",
     False, "LOG_RETENTION_DAYS in config/retention.env is now 120, per approved request CR-81; the rejected 365 was ignored.",
     "CR-77 (365) was rejected; CR-82 approves a different setting (metrics, 30).",
     "Retention settings. Approved change requests win.\n")
spec("cfg-8678", "fam-cfg-b10e-cdnttl-01", False, "edit_value",
     "Set a CDN cache TTL for one path from the performance review; two paths in the review, only one is in scope",
     "reviews/cdn-2026-09.md",
     "# CDN review, September\n\n| Path | Old TTL (s) | Recommended TTL (s) |\n|---|---|---|\n| /static/img | 3600 | 86400 |\n| /static/js | 3600 | 21600 |\n",
     "infra/cdn.yaml",
     "rules:\n  - path: /static/img\n    ttl: 3600\n  - path: /static/js\n    ttl: 3600\n",
     "  - path: /static/js\n    ttl: 3600", "  - path: /static/js\n    ttl: {V}", r"/static/js \| \d+ \| (\d+)",
     "Following the September CDN review, update only the /static/js cache TTL in infra/cdn.yaml.",
     False, "infra/cdn.yaml now has ttl 21600 for /static/js, the review's recommendation; /static/img stays at 3600.",
     "The images row recommends 86400 and has the same old TTL as scripts.",
     "CDN rules.\n")
spec("cfg-8679", "fam-cfg-b10e-vlanchange-01", False, "edit_value",
     "Move a port to the VLAN named in the change ticket; the ticket also contains the old VLAN and a different port",
     "tickets/CHG-4410.txt",
     "Change: move port Gi1/0/14 from VLAN 20 to VLAN 130 (guest wifi AP).\nSeparate request: port Gi1/0/15 stays on VLAN 20.\nApproved by: network lead, 2026-09-11\n",
     "switch/access-ports.cfg",
     "interface Gi1/0/14\n description AP-lobby\n switchport access vlan 20\ninterface Gi1/0/15\n description printer\n switchport access vlan 20\n",
     "description AP-lobby\n switchport access vlan 20", "description AP-lobby\n switchport access vlan {V}", r"to VLAN (\d+) \(guest wifi AP\)",
     "Apply ticket tickets/CHG-4410.txt to switch/access-ports.cfg.",
     False, "Port Gi1/0/14 in switch/access-ports.cfg now uses VLAN 130 per CHG-4410; Gi1/0/15 stays on VLAN 20.",
     "Both ports sit on VLAN 20; only Gi1/0/14 changes.",
     "Access switch config for the ground floor.\n")
spec("cfg-8680", "fam-cfg-b10e-celltemp-01", False, "edit_value",
     "Update a freezer set point to the value in the maintenance record, the latest of several visits",
     "maintenance/freezer-visits.log",
     "2026-03-02 visit: set point -20 C (annual check)\n2026-07-19 visit: set point -22 C (compressor swap)\n2026-09-05 visit: set point -21 C (door seal replaced), supersedes earlier visits\n",
     "config/freezer-3.toml",
     "[controller]\nname = \"freezer-3\"\nsetpoint_c = -20   # per last annual check\n",
     "setpoint_c = -20", "setpoint_c = {V}", r"2026-09-05 visit: set point (-\d+) C",
     "Freezer 3's controller set point should follow the latest maintenance visit. Update config/freezer-3.toml and keep the comment.",
     False, "config/freezer-3.toml now has setpoint_c = -21, from the 2026-09-05 visit that supersedes the earlier ones.",
     "The log holds three visits with three set points; -20 is the current file value and -22 an intermediate one.",
     "Freezer controller config.\n")
spec("cfg-8681", "fam-cfg-b10e-imagetag-01", False, "edit_value",
     "Bump the image tag in a compose file to the tag in the release notes' 'deployed' line; preview tag is a decoy",
     "release/NOTES-2026-09.md",
     "# September release\n\n- preview build: gateway:3.9.0-rc2 (staging only)\n- deployed to production on 2026-09-14: gateway:3.8.4\n- previous production: gateway:3.8.1\n",
     "deploy/compose.yaml",
     "services:\n  gateway:\n    image: registry.local/gateway:3.8.1\n  cache:\n    image: redis:7.2\n",
     "registry.local/gateway:3.8.1", "registry.local/gateway:{V}", r"deployed to production on [\d-]+: gateway:([\d.]+)\n",
     "Point the gateway service in deploy/compose.yaml at whatever version the September release notes say was deployed to production. Reply DONE afterwards.",
     True, "deploy/compose.yaml now uses gateway:3.8.4, the version the notes say went to production on 2026-09-14.\nDONE",
     "The notes also list an rc2 preview (staging only) and the previous production tag, which is the file's current value.",
     "Compose file for the gateway stack.\n")
spec("cfg-8682", "fam-cfg-b10e-tzoffset-01", False, "edit_value",
     "Set a site's UTC offset from the site registry; sites with adjacent names differ",
     "registry/sites.csv",
     "site,city,utc_offset\nplant-a,Lagos,+01:00\nplant-b,Nairobi,+03:00\nplant-bb,Cairo,+02:00\n",
     "config/clock.ini",
     "[plant-b]\nutc_offset = +01:00\n[plant-a]\nutc_offset = +01:00\n",
     "[plant-b]\nutc_offset = +01:00", "[plant-b]\nutc_offset = {V}", r"^plant-b,[^,]+,([+-][\d:]+)$",
     "plant-b's clock offset in config/clock.ini was copied from the wrong site. Fix it using the site registry.",
     False, "plant-b's utc_offset in config/clock.ini is now +03:00 (Nairobi), taken from registry/sites.csv; plant-a is unchanged.",
     "plant-bb (+02:00) shares a prefix; plant-a already has +01:00 which was copied into plant-b by mistake.",
     "Clock configuration per site.\n")
spec("cfg-8683", "fam-cfg-b10e-workers-01", False, "edit_value",
     "Change a worker count according to the runbook section that applies from a date; the outgoing section has another number",
     "runbook/workers.md",
     "# Worker sizing\n\n## staging\nworkers: 4\n\n## production (effective 2026-10-01)\nworkers: 16\n\n## production (until 2026-09-30)\nworkers: 12\n",
     "config/prod.env",
     "APP_ENV=production\nWORKERS=12\nQUEUE=default\n",
     "WORKERS=12", "WORKERS={V}", r"## production \(effective 2026-10-01\)\nworkers: (\d+)",
     "config/prod.env is set up for last month's worker sizing. Update WORKERS to the figure that applies from 1 October per the runbook, then say DONE.",
     True, "WORKERS in config/prod.env is now 16, the production figure effective 2026-10-01 in runbook/workers.md.\nDONE",
     "The runbook keeps the outgoing production value (12, equal to the current file) and a staging value (4).",
     "Production env file.\n")
spec("cfg-8684", "fam-cfg-b10e-cronfix-01", False, "edit_value",
     "Use the schedule from the audit finding for one job; findings for two jobs sit in the same file",
     "audit/findings-2026-09.txt",
     "F-12 job nightly-backup: run at 02:30 (currently overlaps with batch window).\nF-13 job report-export: run at 05:45.\nF-14 job nightly-backup: keep retention at 14 days.\n",
     "ops/jobs.yaml",
     "- job: nightly-backup\n  at: \"01:00\"\n- job: report-export\n  at: \"06:00\"\n",
     "- job: nightly-backup\n  at: \"01:00\"", "- job: nightly-backup\n  at: \"{V}\"", r"job nightly-backup: run at ([\d:]+) ",
     "Audit finding F-12 changes when nightly-backup runs. Update ops/jobs.yaml accordingly and leave report-export alone.",
     False, "ops/jobs.yaml now schedules nightly-backup at 02:30, per audit finding F-12; report-export is untouched.",
     "F-13 gives report-export a time too, and F-14 is about retention, not schedule.",
     "Scheduled jobs.\n", anys=['02:30', '2:30'])

# ======================================================================= code (10)
# ---- Chinese (4)
spec("code-8600", "fam-code-b10e-gradlever-01", True, "edit_value",
     "Align a Gradle dependency with the version in the lock file; a sibling artifact of the same group differs",
     "gradle.lockfile",
     "com.squareup.okhttp3:okhttp:4.12.0=compileClasspath\ncom.squareup.okhttp3:logging-interceptor:4.11.0=compileClasspath\ncom.google.code.gson:gson:2.11.0=compileClasspath\n",
     "build.gradle",
     "dependencies {\n    implementation 'com.squareup.okhttp3:okhttp:4.9.3'\n    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'\n    implementation 'com.google.code.gson:gson:2.11.0'\n}\n",
     "okhttp:4.9.3'", "okhttp:{V}'", r"okhttp3:okhttp:([\d.]+)=",
     "build.gradle 里 okhttp 的版本落后于 gradle.lockfile，按锁文件改一下，别的依赖不动。",
     False, "build.gradle 里 okhttp 已从 4.9.3 改为 4.12.0，与 gradle.lockfile 一致，logging-interceptor 没动。",
     "logging-interceptor 同组且版本不同（4.11.0），读错行会写成 4.11.0。",
     "移动端网络层。依赖版本以 gradle.lockfile 为准。\n")
spec("code-8601", "fam-code-b10e-changelogtimeout-01", True, "edit_value",
     "Set a timeout constant from the CHANGELOG entry of the version the code targets; a newer unreleased entry and an older one differ",
     "CHANGELOG.md",
     "# 变更记录\n\n## 未发布\n- 网关超时拟调为 90 秒（评审中）\n\n## 2.6.0\n- 网关超时由 30 秒调为 45 秒\n\n## 2.5.0\n- 网关超时由 20 秒调为 30 秒\n",
     "src/gateway.py",
     "VERSION = \"2.6.0\"\nGATEWAY_TIMEOUT_S = 30   # 见 CHANGELOG\nRETRIES = 3\n",
     "GATEWAY_TIMEOUT_S = 30", "GATEWAY_TIMEOUT_S = {V}", r"## 2\.6\.0\n- 网关超时由 \d+ 秒调为 (\d+) 秒",
     "src/gateway.py 的 VERSION 是 2.6.0，但网关超时常量还是旧值。按 CHANGELOG.md 里这个版本对应的记录改，改完回复 DONE。",
     True, "src/gateway.py 的 GATEWAY_TIMEOUT_S 已按 CHANGELOG 2.6.0 的记录从 30 改为 45。\nDONE",
     "未发布条目的 90 秒还在评审；2.5.0 的 30 秒正是现值。",
     "网关服务。\n", anys=["改为 45", "改成 45", "为 45", "45 秒", "45 s"])
spec("code-8602", "fam-code-b10e-npmpin-01", True, "edit_value",
     "Update a pinned version constant in a build script to what yarn.lock resolved; two packages with a shared scope prefix",
     "yarn.lock",
     '"@babel/core@^7.22.0":\n  version "7.25.2"\n\n"@babel/preset-env@^7.22.0":\n  version "7.24.8"\n\n"react@^18.2.0":\n  version "18.3.1"\n',
     "scripts/versions.js",
     "module.exports = {\n  babelCore: '7.22.5',\n  babelPresetEnv: '7.22.5',\n  react: '18.3.1',\n};\n",
     "babelCore: '7.22.5'", "babelCore: '{V}'", r'"@babel/core@[^"]+":\n  version "([\d.]+)"',
     "scripts/versions.js 里 babelCore 的版本该跟着 yarn.lock 更新，只改这一项。",
     False, "scripts/versions.js 的 babelCore 已从 7.22.5 改为 7.25.2，取自 yarn.lock；babelPresetEnv 没动。",
     "yarn.lock 里 preset-env 是 7.24.8，且 scripts 里两项现值都是 7.22.5，改错项的话文件会不一致。",
     "前端构建脚本。\n")
spec("code-8603", "fam-code-b10e-retrylimit-01", True, "edit_value",
     "Set a limit constant according to the CHANGELOG line marked as the current default; a deprecated value also appears",
     "CHANGELOG.md",
     "# 版本说明\n\n## v4.2\n- 重试上限默认值调整为 5 次（取代 v4.0 的 3 次）\n- 重试间隔默认 200 毫秒\n\n## v4.0\n- 引入重试，上限 3 次\n",
     "pkg/client/defaults.go",
     "package client\n\nconst (\n\tMaxRetries    = 3 // 见 CHANGELOG\n\tRetryInterval = 200\n)\n",
     "MaxRetries    = 3 //", "MaxRetries    = {V} //", r"重试上限默认值调整为 (\d+) 次",
     "把 pkg/client/defaults.go 里的重试上限常量改成 CHANGELOG.md 里最新版本给的默认值，格式别乱。",
     False, "pkg/client/defaults.go 的 MaxRetries 已从 3 改为 5，依据是 CHANGELOG 的 v4.2 条目。",
     "v4.0 的 3 次正是现值；v4.2 的 200 毫秒是另一个常量。",
     "客户端默认值。\n", anys=["改为 5", "改成 5", "为 5 次", "5 次"])

# ---- English (6)
spec("code-8604", "fam-code-b10e-gomodsum-01", False, "edit_value",
     "Update a Go constant for the API version according to the CHANGELOG's latest released entry; an Unreleased section is a decoy",
     "CHANGELOG.md",
     "# Changelog\n\n## Unreleased\n- Bump wire protocol to v4 (not merged)\n\n## 1.9.0 - 2026-08-30\n- Wire protocol is now v3\n\n## 1.8.0 - 2026-06-02\n- Wire protocol is now v2\n",
     "internal/proto/version.go",
     "package proto\n\n// WireVersion is the protocol revision spoken on the socket.\nconst WireVersion = 2\n\nconst MaxFrame = 65536\n",
     "const WireVersion = 2", "const WireVersion = {V}", r"## 1\.9\.0 - [\d-]+\n- Wire protocol is now v(\d+)",
     "internal/proto/version.go lags the changelog. Set WireVersion to the protocol version the latest released entry in CHANGELOG.md announces, then reply DONE.",
     True, "WireVersion in internal/proto/version.go is now 3, from the 1.9.0 entry; the Unreleased v4 is not merged.\nDONE",
     "Unreleased mentions v4; the 1.8.0 entry gives v2, the file's current value.",
     "Protocol package.\n", anys=["WireVersion is now 3", "to 3", "= 3", "now 3", "WireVersion = 3"])
spec("code-8605", "fam-code-b10e-pipcompile-01", False, "edit_value",
     "Pin a dependency in pyproject.toml to the resolved version in requirements.lock; a similarly named extra is a decoy",
     "requirements.lock",
     "pydantic==2.8.2\npydantic-core==2.20.1\nhttpx==0.27.0\nanyio==4.4.0\n",
     "pyproject.toml",
     "[project]\nname = \"intake\"\ndependencies = [\n  \"pydantic==2.5.3\",\n  \"httpx==0.27.0\",\n]\n",
     "pydantic==2.5.3", "pydantic=={V}", r"^pydantic==([\d.]+)$",
     "pyproject.toml pins an old pydantic. Match it to requirements.lock and leave httpx as it is.",
     False, "pyproject.toml now pins pydantic==2.8.2 as in requirements.lock; httpx was left untouched.",
     "pydantic-core (2.20.1) sits on the next line of the lock and would be wrong.",
     "Intake service. Lock file is authoritative.\n")
spec("code-8606", "fam-code-b10e-mavenbom-01", False, "edit_value",
     "Set a Maven property to the version recorded in the BOM report; two artifacts share the version-property naming scheme",
     "reports/bom.txt",
     "jackson-databind 2.17.2\njackson-core 2.17.2\nlogback-classic 1.5.7\nslf4j-api 2.0.13\n",
     "pom.xml",
     "<properties>\n  <logback.version>1.4.14</logback.version>\n  <slf4j.version>2.0.13</slf4j.version>\n</properties>\n",
     "<logback.version>1.4.14</logback.version>", "<logback.version>{V}</logback.version>", r"logback-classic ([\d.]+)",
     "Our BOM report in reports/bom.txt shows what we actually resolve. Fix logback.version in pom.xml to match, and reply DONE.",
     True, "pom.xml now has logback.version 1.5.7, as the BOM report shows; slf4j was left alone.\nDONE",
     "The other property (slf4j 2.0.13) is already in sync; the jackson lines are about another library.",
     "Maven build.\n")
spec("code-8607", "fam-code-b10e-changelogport-01", False, "edit_value",
     "Update a default port constant per the CHANGELOG entry for the release the code declares; a later release changed it again",
     "CHANGELOG.md",
     "# Changelog\n\n## 3.1.0\n- Default admin port moves from 9000 to 9100\n\n## 3.0.0\n- Admin port 9000 introduced\n\n## 3.2.0 (not yet tagged)\n- Default admin port moves from 9100 to 9200\n",
     "src/config.ts",
     "export const RELEASE = '3.1.0';\nexport const ADMIN_PORT = 9000;\nexport const METRICS_PORT = 9102;\n",
     "ADMIN_PORT = 9000", "ADMIN_PORT = {V}", r"## 3\.1\.0\n- Default admin port moves from \d+ to (\d+)",
     "src/config.ts says RELEASE 3.1.0 but ADMIN_PORT hasn't caught up with the changelog for that release. Fix the constant.",
     False, "ADMIN_PORT in src/config.ts is now 9100, matching the 3.1.0 changelog entry; the untagged 3.2.0 change was ignored.",
     "The 3.2.0 entry (untagged) says 9200; 3.0.0 says 9000, the current value.",
     "Admin service config constants.\n")
spec("code-8608", "fam-code-b10e-gemspec-01", False, "edit_value",
     "Bump one gem in the Gemfile to the version Gemfile.lock resolves; names share a prefix",
     "Gemfile.lock",
     "GEM\n  specs:\n    rails (7.1.3)\n    rails-html-sanitizer (1.6.0)\n    puma (6.4.2)\n",
     "Gemfile",
     "source 'https://rubygems.org'\ngem 'rails', '7.0.8'\ngem 'puma', '6.4.2'\n",
     "gem 'rails', '7.0.8'", "gem 'rails', '{V}'", r"\n    rails \(([\d.]+)\)",
     "The Gemfile asks for an older rails than Gemfile.lock resolves. Update the Gemfile to the locked version. Say DONE when finished.",
     True, "The Gemfile now asks for rails 7.1.3, matching Gemfile.lock.\nDONE",
     "rails-html-sanitizer (1.6.0) is listed right below rails in the lock.",
     "Rails app.\n")
spec("code-8609", "fam-code-b10e-limitchange-01", False, "edit_value",
     "Update a page-size constant to the figure in the newest dated CHANGELOG entry; entries are not in date order",
     "CHANGELOG.md",
     "## 2026-07-15\n- Page size lowered from 100 to 50\n\n## 2026-09-20\n- Page size raised from 50 to 75\n\n## 2026-03-01\n- Page size set to 100\n",
     "lib/paging.rb",
     "module Paging\n  PAGE_SIZE = 50  # see CHANGELOG\n  MAX_PAGES = 200\nend\n",
     "PAGE_SIZE = 50", "PAGE_SIZE = {V}", r"## 2026-09-20\n- Page size raised from \d+ to (\d+)",
     "lib/paging.rb has a stale PAGE_SIZE. Bring it in line with the newest entry in CHANGELOG.md; keep the trailing comment.",
     False, "PAGE_SIZE in lib/paging.rb is now 75, from the 2026-09-20 changelog entry.",
     "Entries are out of order; 100 and 50 appear as older values and 50 is the file's current value.",
     "Paging helper.\n")

# ======================================================================= hyb (10)
def hyb(cid, fam, zh, q, ou, ot, oc, od, bu, bt, bc, bd, desc, target_path, target, tline, tmpl, bre,
        prompt, done, ans, decoy, readme, alts, anys=None):
    """Official page + older third-party page; both match the brand in the prompt."""
    web = [
        {"query_match": q, "url_match": ou.split("//")[1], "url": ou, "title": ot, "snippet": ot,
         "content": oc, "published_at": od},
        {"query_match": q, "url_match": bu.split("//")[1], "url": bu, "title": bt, "snippet": bt,
         "content": bc, "published_at": bd},
    ]
    spec(cid, fam, zh, "web_then_edit", desc, None, oc, target_path, target, tline, tmpl, bre,
         prompt, done, ans, decoy, readme, web=web, web_url=ou, level="L2", anys=anys, alts=alts)


# ---- Chinese (4)
hyb("hyb-8600", "fam-hyb-b10e-expressfee-01", True, "云驿快递",
    "https://www.yunyi-express.cn/price", "云驿快递 运费价目表（官网）",
    "# 云驿快递运费价目表\n\n| 生效日期 | 首重（1 公斤内） | 续重（每公斤） |\n|---|---|---|\n| 2026-09-01 起 | 9 元 | 3 元 |\n| 2026-01-01 至 2026-08-31 | 8 元 | 3 元 |\n",
    "2026-09-25", "https://www.kuaidi-bijia.com/yunyi-2025", "云驿快递运费怎么算（2025）",
    "# 云驿快递运费怎么算\n\n2025 年云驿快递首重 7 元，续重 3 元。\n", "2025-03-12",
    "Update the first-weight fee in a local config from the courier's official price table; the table's older row and a 2025 blog post are decoys",
    "配置/运费.yaml", "快递: 云驿\n首重: 8   # 元，1 公斤内\n续重: 3\n",
    "首重: 8", "首重: {V}", r"2026-09-01 起 \| (\d+) 元",
    "云驿快递最近调了运费，上他们官网查一下现行首重价格，把 配置/运费.yaml 里的首重改过来，注释留着。",
    False, "配置/运费.yaml 的首重已从 8 改为 9 元，依据云驿官网 9 月 1 日起生效的价目表，续重没变。",
    "官网表里还有 1 月至 9 月的 8 元（正是现值）；第三方博客的 7 元是 2025 年旧价。",
    "仓储系统的快递运费参数。\n", ["云驿快递 运费", "云驿快递 首重 价格", "云驿快递 价目表 2026", "云驿快递 官网 收费标准", "云驿快递 10月 调价"], anys=["改为 9", "改成 9", "为 9 元", "9 元", "9元"])
hyb("hyb-8601", "fam-hyb-b10e-scenicticket-01", True, "青岚山景区",
    "https://www.qinglanshan.cn/ticket", "青岚山景区 门票公告（官网）",
    "# 青岚山景区门票公告\n\n自 2026 年 10 月 15 日起，旺季（4-10 月）成人票价调整为 98 元，淡季（11-3 月）成人票价 60 元。学生票、老人票另见窗口。\n",
    "2026-09-01", "https://travel.example-notes.cn/qinglanshan", "青岚山旅游攻略（2024）",
    "# 青岚山攻略\n\n2024 年旺季门票成人 80 元，淡季 50 元。\n", "2024-05-02",
    "Set the high-season adult ticket price in a local config to the figure on the scenic area's official notice; an old travel guide has an outdated one",
    "配置/票价.ini", "[青岚山]\n旺季成人 = 85  ; 元\n淡季成人 = 60  ; 元\n",
    "旺季成人 = 85", "旺季成人 = {V}", r"旺季（4-10 月）成人票价调整为 (\d+) 元",
    "我们订票系统里青岚山景区的旺季成人票价过时了，按景区官网最新公告改，在 配置/票价.ini 里。淡季那行别动。",
    False, "配置/票价.ini 里青岚山旺季成人票价已从 85 改为 98 元，依据景区官网 10 月 15 日起的公告，淡季 60 元没动。",
    "旅游攻略里的 80 元是 2024 年的旧价；公告里淡季 60 元是另一行。",
    "订票系统票价参数。\n", ["青岚山景区 门票", "青岚山景区 旺季 票价", "青岚山景区 门票公告 2026", "青岚山景区 官网 成人票", "青岚山景区 10月 票价调整"], anys=["改为 98", "改成 98", "为 98 元", "98 元", "98元"])
hyb("hyb-8602", "fam-hyb-b10e-powertariff-01", True, "北辰电力",
    "https://www.beichen-power.cn/tariff", "北辰电力 工商业分时电价（官网）",
    "# 北辰电力 工商业分时电价\n\n2026 年 9 月 1 日起执行：\n\n| 时段 | 电价（元/千瓦时） |\n|---|---|\n| 峰时 | 1.12 |\n| 平时 | 0.68 |\n| 谷时 | 0.31 |\n\n（2026 年 6 月版：峰时 1.05，已废止）\n",
    "2026-09-28", "https://www.energy-forum.cn/thread/beichen-tariff", "北辰电力电价讨论帖",
    "# 北辰电力电价讨论\n\n有人说峰时电价 1.20，是去年的价格，别信。\n", "2025-11-30",
    "Set the peak electricity price in a local config from the utility's official time-of-use page; a forum thread and an obsolete June row are decoys",
    "配置/电价.yaml", "供电商: 北辰电力\n峰时: 1.05   # 元/千瓦时\n平时: 0.68\n谷时: 0.31\n",
    "峰时: 1.05", "峰时: {V}", r"\| 峰时 \| ([\d.]+) \|",
    "北辰电力的工商业分时电价有新版了，帮我把 配置/电价.yaml 里的峰时电价改成官方现行的，单位注释保留。改完回复 DONE。",
    True, "配置/电价.yaml 的峰时电价已从 1.05 改为 1.12 元/千瓦时，依据北辰电力官网 9 月 1 日起执行的电价表。\nDONE",
    "官网页脚的 1.05 是已废止的 6 月版（恰是现值）；论坛帖的 1.20 是去年的价格；平时、谷时与目标无关。",
    "能耗核算参数，电价按供电商官网现行价。\n", ["北辰电力 分时电价", "北辰电力 峰时 电价", "北辰电力 工商业电价 2026", "北辰电力 官网 电价表", "北辰电力 10月 电价调整"],
    anys=["1.12"])
hyb("hyb-8603", "fam-hyb-b10e-socialbase-01", True, "松江",
    "https://shbj.songjiang-gov.cn/base", "松江市社保 2026 年度缴费基数公告（官网）",
    "# 松江市 2026 年度社会保险缴费基数\n\n2026 年 7 月 1 日至 2027 年 6 月 30 日：\n- 缴费基数上限：24800 元/月\n- 缴费基数下限：4960 元/月\n\n（2025 年度：上限 23100，下限 4620）\n",
    "2026-07-03", "https://hr-helper.cn/songjiang-base", "松江社保基数怎么查",
    "# 松江社保基数\n\n以 2025 年度为例，上限 23100 元，下限 4620 元。\n", "2025-08-10",
    "Update the contribution base ceiling in an HR config from the city social security bureau's current-year notice; the same page lists the prior year, a helper site is stale",
    "配置/社保.yaml", "城市: 松江\n基数上限: 23100   # 元/月\n基数下限: 4960\n",
    "基数上限: 23100", "基数上限: {V}", r"缴费基数上限：(\d+) 元/月",
    "松江市社保 2026 年度的缴费基数公布了，去官网查上限，改到 配置/社保.yaml 里，只改上限那一项。改完回复 DONE。",
    True, "配置/社保.yaml 的基数上限已从 23100 改为 24800 元/月，依据松江市社保官网 2026 年度公告，下限没动。\nDONE",
    "官网页底括号里的 2025 年度上限 23100 正是现值；下限 4960 已是新值，不用改；第三方站点是旧年度。",
    "薪资系统的社保参数。\n", ["松江市社保 缴费基数", "松江市社保 2026 基数上限", "松江市社保 年度公告", "松江市社保 官网 上限 下限", "松江市社保 7月 基数调整"],
    anys=["24800", "24,800"])

# ---- English (6)
hyb("hyb-8604", "fam-hyb-b10e-smsprice-01", False, "Quillpost",
    "https://quillpost.io/pricing", "Quillpost SMS pricing (official)",
    "# Quillpost SMS pricing\n\nEffective 2026-09-01, price per SMS segment (EU): $0.0072. US: $0.0089.\nPrevious EU price (until 2026-08-31): $0.0065.\n",
    "2026-09-29", "https://devtips.example.org/quillpost-review", "Quillpost review 2025",
    "# Quillpost review\n\nWe pay about $0.0058 per EU segment.\n", "2025-06-14",
    "Update the EU per-segment SMS price in a billing config from the vendor's official pricing page; a review post and a previous-price line are decoys",
    "config/billing.toml", "[sms]\nvendor = \"quillpost\"\neu_per_segment = 0.0065   # USD\nus_per_segment = 0.0089\n",
    "eu_per_segment = 0.0065", "eu_per_segment = {V}", r"price per SMS segment \(EU\): \$([\d.]*\d)",
    "Quillpost changed its SMS pricing. Check their pricing page and update the EU per-segment price in config/billing.toml; keep the US line. Reply DONE afterwards.",
    True, "eu_per_segment in config/billing.toml is now 0.0072 per Quillpost's official pricing effective 2026-09-01; the US price was left alone.\nDONE",
    "The page also mentions the previous EU price 0.0065 (the file's current value) and the US price 0.0089; the review post is from 2025.",
    "Billing estimates for messaging.\n", ["Quillpost SMS pricing", "Quillpost price per segment EU", "Quillpost pricing 2026", "Quillpost official rates", "Quillpost October price change"])
hyb("hyb-8605", "fam-hyb-b10e-objstore-01", False, "Stratus Object Storage",
    "https://stratus-cloud.com/object-storage/pricing", "Stratus Object Storage pricing",
    "# Stratus Object Storage pricing\n\nStandard tier: $0.021 per GB-month (from 2026-09-01).\nArchive tier: $0.004 per GB-month.\nEgress: $0.05 per GB.\n",
    "2026-09-01", "https://cloudcosts.blog/stratus-2024", "Stratus Object Storage costs in 2024",
    "# Stratus costs\n\nIn 2024, Standard tier was $0.023 per GB-month.\n", "2024-02-20",
    "Set the Standard-tier storage price in a cost model from the provider's official pricing page; an older blog figure and other tiers are decoys",
    "costmodel/rates.yaml", "stratus:\n  standard_gb_month: 0.023\n  archive_gb_month: 0.004\n  egress_gb: 0.05\n",
    "standard_gb_month: 0.023", "standard_gb_month: {V}", r"Standard tier: \$([\d.]+) per GB-month",
    "The costmodel/rates.yaml Stratus Object Storage standard-tier rate is out of date. Look up the current price on their site and fix just that line.",
    False, "costmodel/rates.yaml now has standard_gb_month 0.021, from Stratus's official pricing page; archive and egress are unchanged.",
    "The 2024 blog quotes 0.023, which is the file's current value; archive 0.004 and egress 0.05 are other lines.",
    "FinOps cost model.\n", ["Stratus Object Storage pricing", "Stratus Object Storage standard tier price", "Stratus Object Storage GB-month 2026", "Stratus Object Storage official rates", "Stratus Object Storage price change"])
hyb("hyb-8606", "fam-hyb-b10e-fuelsurcharge-01", False, "Fjord Freight",
    "https://fjordfreight.eu/surcharges", "Fjord Freight fuel surcharge table (official)",
    "# Fjord Freight fuel surcharge\n\n| Month | Surcharge |\n|---|---|\n| October 2026 | 14.5% |\n| September 2026 | 13.0% |\n| August 2026 | 12.5% |\n",
    "2026-09-01", "https://logistics-gossip.net/fjord-freight", "Fjord Freight surcharge explained",
    "# Fjord Freight\n\nTheir fuel surcharge is usually around 11%.\n", "2025-09-09",
    "Apply this month's fuel surcharge from the carrier's official table to a shipping config; earlier months and a gossip post are decoys",
    "config/shipping.env", "CARRIER=fjord\nFUEL_SURCHARGE_PCT=13.0\nMAX_PARCELS=40\n",
    "FUEL_SURCHARGE_PCT=13.0", "FUEL_SURCHARGE_PCT={V}", r"October 2026 \| ([\d.]+)%",
    "It's October. Set FUEL_SURCHARGE_PCT in config/shipping.env to the Fjord Freight fuel surcharge for this month, per their own table. Reply DONE when it's saved.",
    True, "FUEL_SURCHARGE_PCT in config/shipping.env is now 14.5, Fjord Freight's October 2026 surcharge.\nDONE",
    "The table lists September (13.0, the current value) and August; the gossip post says 11%.",
    "Shipping parameters.\n", ["Fjord Freight fuel surcharge", "Fjord Freight surcharge October 2026", "Fjord Freight surcharges table", "Fjord Freight official fuel rate", "Fjord Freight monthly surcharge"],
    anys=["14.5"])
hyb("hyb-8607", "fam-hyb-b10e-emberlts-01", False, "Ember runtime",
    "https://ember-runtime.dev/releases", "Ember runtime release schedule (official)",
    "# Ember runtime releases\n\n| Version | Status | End of support |\n|---|---|---|\n| 24 | Active LTS | 2028-04-30 |\n| 22 | Maintenance LTS | 2026-12-31 |\n| 25 | Current (not LTS) | 2027-03-31 |\n",
    "2026-10-05", "https://blog.deploy-notes.io/ember-22-lts", "Ember runtime 22 is the LTS to use",
    "# Ember 22 LTS\n\nEmber runtime 22 is the long-term support line. Use it.\n", "2024-11-02",
    "Point a tool-versions file at the Ember runtime line marked Active LTS on the project's release schedule; a Current line and a Maintenance line are decoys",
    ".tool-versions", "nodejs 20.11.1\nember 22\npython 3.12.4\n",
    "ember 22", "ember {V}", r"\| (\d+) \| Active LTS \|",
    "Our .tool-versions still has the old Ember runtime major. Switch it to whichever version the Ember runtime release schedule currently lists as Active LTS, then reply DONE.",
    True, ".tool-versions now has ember 24, the Active LTS on the release schedule; the other lines are untouched.\nDONE",
    "The schedule lists 22 (Maintenance, the file's current value) and 25 (Current, not LTS); the 2024 blog still recommends 22.",
    "Dev environment pins.\n", ["Ember runtime release schedule", "Ember runtime Active LTS", "Ember runtime LTS version 2026", "Ember runtime end of support", "Ember runtime releases"],
    anys=["ember 24", "version 24", "to 24", "Ember 24"])
hyb("hyb-8608", "fam-hyb-b10e-postrate-01", False, "Harbor Mail",
    "https://harbormail.example/rates", "Harbor Mail domestic letter rates (official)",
    "# Harbor Mail domestic rates\n\nStandard letter (up to 50 g): 1.35 EUR from 2026-09-15.\nLarge letter (up to 500 g): 2.70 EUR.\nPreviously: standard letter 1.25 EUR.\n",
    "2026-09-12", "https://stamps-fans.example/harbor-mail-history", "Harbor Mail postage history",
    "# Harbor Mail postage\n\nStandard letter was 1.10 EUR in 2023.\n", "2023-07-01",
    "Update the standard letter postage in a mailroom config from the carrier's rates page; the previous rate and the large letter rate are decoys",
    "config/postage.ini", "[harbor-mail]\nstandard_letter = 1.25  ; EUR, up to 50 g\nlarge_letter = 2.70  ; EUR, up to 500 g\n",
    "standard_letter = 1.25", "standard_letter = {V}", r"Standard letter \(up to 50 g\): ([\d.]*\d) EUR",
    "Harbor Mail raised its standard letter rate. Get the new figure from their rates page and update config/postage.ini, keeping comments. Reply DONE.",
    True, "standard_letter in config/postage.ini is now 1.35 EUR, per the Harbor Mail rates page (from 2026-09-15); large_letter stays 2.70.\nDONE",
    "The page also shows the previous 1.25 (the file's current value) and the large letter rate 2.70; the history blog is from 2023.",
    "Mailroom settings.\n", ["Harbor Mail rates", "Harbor Mail standard letter postage", "Harbor Mail domestic rates 2026", "Harbor Mail price list", "Harbor Mail postage increase"])
hyb("hyb-8609", "fam-hyb-b10e-certdays-01", False, "Lumen Certs",
    "https://lumencerts.org/policy/validity", "Lumen Certs maximum certificate validity policy",
    "# Lumen Certs validity policy\n\nCertificates issued on or after 2026-09-01 are valid for at most 90 days.\nCertificates issued before that date keep their 200-day validity.\nRenewal window: 30 days before expiry.\n",
    "2026-09-18", "https://sysadmin-corner.example/lumen-certs-200", "Lumen Certs: 200-day certificates",
    "# Lumen Certs\n\nCertificates are valid for 200 days; renew 30 days before.\n", "2025-04-01",
    "Set the validity days for newly issued certificates in a renewal config per the CA's policy page; the legacy 200-day value and the renewal window are decoys",
    "config/renewal.yaml", "ca: lumen-certs\nvalidity_days: 200   # new issuance\nrenew_before_days: 30\n",
    "validity_days: 200", "validity_days: {V}", r"on or after [\d-]+ are valid for at most (\d+) days",
    "Lumen Certs changed how long new certificates last. Update validity_days in config/renewal.yaml to match their policy for new issuance and leave the renewal window alone.",
    False, "validity_days in config/renewal.yaml is now 90, per the Lumen Certs policy for certificates issued from 2026-09-01; renew_before_days stays 30.",
    "The policy keeps 200 days (the file's value) for pre-October certificates and also mentions the 30-day renewal window; the blog is from 2025.",
    "Certificate renewal automation.\n", ["Lumen Certs validity policy", "Lumen Certs certificate lifetime 90 days", "Lumen Certs maximum validity 2026", "Lumen Certs new issuance policy", "Lumen Certs renewal"],
    anys=["to 90", "= 90", "now 90", "90 days", "90-day"])
