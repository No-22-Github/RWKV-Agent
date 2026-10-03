"""M2 (v1.4 §3.2) pilot, part A: target absent with a near-match decoy."""
from common import write_case

NEG_ZH = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没"]
NEG_EN = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
          "not in the", "not on the", "no row", "missing", "not covered"]

YAML_KV = '''
def kv(text):
    out = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out
'''

# ---------------------------------------------------------------- cfg-8001
write_case(
    "cfg-8001",
    desc="Ticketing go-live asks a pier's daily ticket cap; the pier has no station file, only a freight yard with a similar name and a rollout plan saying its config is pending",
    task_type="read_effective", family="fam-cfg-b10-ferrypier-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 1800},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 渡口票务系统 站点配置\n\n每个售票点在 站点/ 下放一份 yaml，文件名就是站点名。\n上线前须满足 平台/必填键.yaml 列出的全部键。\n",
        "平台/必填键.yaml": "必填键:\n  - 站点类型\n  - 站点编号\n  - 单日售票上限\n  - 验票通道\n  - 应急联系人\n",
        "站点/北港码头.yaml": "站点类型: 客运码头\n站点编号: BG-01\n单日售票上限: 2400\n验票通道: 3\n应急联系人: 港务值班室 分机 2201\n",
        "站点/西渡码头.yaml": "站点类型: 客运码头\n站点编号: XD-02\n单日售票上限: 3100\n验票通道: 4\n应急联系人: 西渡调度 分机 3305\n",
        "站点/南湾货运堆场.yaml": "站点类型: 货运堆场\n站点编号: NW-Y1\n单日放行上限: 1800\n备注: 只走货车，不售票，不接入票务系统\n",
        "运营/上线排期.md": "# 售票点上线排期\n\n| 站点 | 状态 | 日期 | 负责 |\n|---|---|---|---|\n| 北港码头 | 已上线 | 2026-03-02 | 运营一组 |\n| 西渡码头 | 已上线 | 2026-05-18 | 运营一组 |\n| 南湾码头 | 站点配置待提交 | 计划 2026-10-20 开售 | 运营二组 |\n",
    },
    turns=[{
        "prompt": "渡口票务系统准备在南湾码头开售，南湾码头那边配置的单日售票上限是多少？",
        "expect": {
            "output_contains": ["南湾码头", "堆场"],
            "output_contains_any": NEG_ZH + ["待提交", "未提交", "没提交"],
            "output_excludes": ["1800"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=YAML_KV + '''
import json

case = json.load(open("case.json"))
files = case["files"]
required = [l.strip()[2:] for l in files["平台/必填键.yaml"].splitlines() if l.strip().startswith("- ")]
assert files["平台/必填键.yaml"].splitlines()[0] == "必填键:"
stations = {p.split("/")[1][:-5]: kv(t) for p, t in files.items() if p.startswith("站点/")}
# No passenger pier called 南湾码头 is configured: every 客运码头 file has all required keys, and the
# only 南湾 file is a freight yard that does not sell tickets.
assert "南湾码头" not in stations
nanwan = [n for n in stations if n.startswith("南湾")]
assert nanwan == ["南湾货运堆场"] and stations["南湾货运堆场"]["站点类型"] == "货运堆场"
for name, s in stations.items():
    if s.get("站点类型") == "客运码头":
        assert all(k in s for k in required), name
plan = files["运营/上线排期.md"]
assert any("南湾码头" in l and "待提交" in l for l in plan.splitlines())
neg = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "待提交", "未提交", "没提交"]
print(json.dumps({"expected_contains_any": neg}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 站点/ 下没有 南湾码头.yaml；运营/上线排期.md 写明南湾码头「站点配置待提交」，由运营二组负责，计划 2026-10-20 开售。不注意会把别的数当成答案，或者裸答 UNKNOWN。
- TR-DECOY: 站点/南湾货运堆场.yaml 名字里带「南湾」，有一个「单日放行上限: 1800」。它是货运堆场，不售票、不接入票务系统，把 1800 当售票上限就是诱饵答案。

## Reference solution
1. 列出工作区，看到 站点/ 下只有北港码头、西渡码头和南湾货运堆场三份配置，另有 运营/上线排期.md。
2. 读 站点/南湾货运堆场.yaml，确认它是货运堆场、不售票。
3. 读 运营/上线排期.md，南湾码头一行是「站点配置待提交 / 运营二组」。
终答（2–4 句）：南湾码头还没有站点配置（站点/ 下只有北港、西渡两个客运码头和南湾货运堆场；堆场不售票，它的 1800 是货车放行上限，不是售票上限），所以没有单日售票上限可读；排期表显示配置由运营二组待提交，可以找他们要，或者我按 平台/必填键.yaml 先起一份草稿。判据：包含「南湾码头」「堆场」和一个否定/待提交说法，不得出现 1800。

## Why the answer is unique
诱饵 1800 错在对象和含义都不对：文件的站点类型是货运堆场，备注写明不售票，键名是「单日放行上限」而不是「单日售票上限」。北港 2400、西渡 3100 是别的码头。排期表证实南湾码头的配置还没提交，工作区里不存在任何能读出南湾码头售票上限的地方，所以唯一站得住的回答是说明查不到、点出堆场不是它、给出补配置的下一步。
''',
)

# ---------------------------------------------------------------- doc-8001
write_case(
    "doc-8001",
    desc="Asks a cold-room temperature band from the third edition of a warehouse standard; only the second edition and a third-edition transport standard exist, and the revision log says edition three is still in draft",
    task_type="policy_lookup", family="fam-doc-b10-coldroom-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "-15"},
    axes=["DEC", "ERR"],
    files={
        "README.md": "规范/ 只放已发布的正式版本；修订中的版本只在 规范/修订记录.md 里登记，不放正文。\n\n青岚冷链 制度文档库，按部门维护。\n",
        "规范/修订记录.md": "# 修订记录\n\n| 文档 | 版本 | 状态 | 说明 |\n|---|---|---|---|\n| 冷库作业规范 | 第二版 | 已发布 2025-11-03 | 现行 |\n| 冷库作业规范 | 第三版 | 起草中 | 质量部牵头，预计 2026 年 11 月评审，正文未定稿 |\n| 冷链运输规范 | 第三版 | 已发布 2026-06-15 | 现行 |\n",
        "规范/冷库作业规范-第二版.md": "# 冷库作业规范（第二版）\n\n## 3 温度控制\n3.1 冷冻间库温保持在 -18℃ 至 -22℃。\n3.2 冷藏间库温保持在 0℃ 至 4℃。\n3.3 每 2 小时记录一次库温，超限 15 分钟内上报值班主管。\n\n## 4 出入库\n4.1 开门作业单次不超过 10 分钟。\n",
        "规范/冷链运输规范-第三版.md": "# 冷链运输规范（第三版）\n\n## 2 车厢温度\n2.1 冷藏车厢温度保持在 -15℃ 至 -18℃（冷冻品）。\n2.2 冷藏品车厢 2℃ 至 6℃。\n\n## 3 装卸\n3.1 装卸时间不超过 30 分钟。\n",
        "规范/仓储安全规范.md": "# 仓储安全规范\n\n叉车限速 5 km/h；货架承重标识每季度复核。\n",
    },
    turns=[{
        "prompt": "仓库要按《冷库作业规范》第三版做温控验收，第三版里冷藏间的库温区间是多少？",
        "expect": {
            "output_contains": ["第三版"],
            "output_contains_any": ["起草", "未发布", "没有发布", "尚未发布", "还没发布", "未定稿", "没有定稿"],
            "output_excludes": ["2℃ 至 6℃", "2℃至6℃", "2 至 6", "2-6℃", "2～6"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("规范/ 只放已发布的正式版本")
log = files["规范/修订记录.md"]
rows = [l for l in log.splitlines() if l.startswith("| 冷库作业规范")]
status = {r.split("|")[2].strip(): r.split("|")[3].strip() for r in rows}
assert status["第三版"] == "起草中" and status["第二版"].startswith("已发布")
assert not any("冷库作业规范-第三版" in p for p in files)
# The only third-edition text is the transport standard, whose 冷藏品 band is the decoy.
transport = files["规范/冷链运输规范-第三版.md"]
assert re.search(r"冷藏品车厢 2℃ 至 6℃", transport)
words = ["起草", "未发布", "没有发布", "尚未发布", "还没发布", "未定稿", "没有定稿"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 规范/ 下没有《冷库作业规范》第三版正文；规范/修订记录.md 登记第三版「起草中，质量部牵头，预计 2026 年 11 月评审，正文未定稿」。
- TR-NEARNAME: 规范/冷链运输规范-第三版.md 也叫「第三版」，里面冷藏品车厢是 2℃ 至 6℃（冷冻品 -15℃ 至 -18℃）。把运输规范的车厢温度当成冷库库温，就是诱饵答案。

## Reference solution
1. 列出 规范/，看到冷库作业规范只有第二版，第三版只有《冷链运输规范》。
2. 读 规范/修订记录.md：冷库作业规范第三版起草中、未定稿。
3. 读 规范/冷库作业规范-第二版.md，现行冷藏间是 0℃ 至 4℃，可作为现行口径告诉用户。
终答（2–4 句）：《冷库作业规范》第三版还在起草（修订记录：质量部牵头、预计 11 月评审），工作区里没有它的正文，所以给不出第三版的冷藏间区间；名字里带第三版的是《冷链运输规范》，管的是车厢温度，不适用于库温；现行第二版规定冷藏间 0℃ 至 4℃，验收是否先按第二版，需要和质量部确认。判据：包含「第三版」和一个「起草/未发布」说法，不得把 2℃ 至 6℃ 当答案。

## Why the answer is unique
运输规范第三版的 2℃ 至 6℃ 是冷藏车厢温度，文件标题和章节都写明是运输，不是冷库作业；修订记录明确冷库作业规范第三版未定稿，规范/ 目录按 README 只放已发布版本。第二版的 0℃ 至 4℃ 是现行值而不是第三版的值，只能作为参考给出。所以「第三版的区间」在工作区里不存在，正确回答只能是说明这一点并给出下一步。
''',
)

# ---------------------------------------------------------------- fs-8001
write_case(
    "fs-8001",
    desc="Asks where the signed harbor-gate 4.2.0 release bundle is; only an unsigned 4.2.0 release candidate and older signed bundles exist, and the signing log says 4.2.0 is awaiting sign-off",
    task_type="find_file", family="fam-fs-b10-signedbundle-01", level="L2", ref_calls=2,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "releases/harbor-gate-4.2.0-rc2.tar.gz"},
    axes=["DEC", "OBS"],
    files={
        "releases/SIGNING-LOG.txt": "bundle | status | signer | date\nharbor-gate-4.1.2.tar.gz | signed | ops-release (key 7C1E) | 2026-06-30\nharbor-gate-4.1.3.tar.gz | signed | ops-release (key 7C1E) | 2026-08-11\nharbor-gate-4.2.0-rc2.tar.gz | unsigned (release candidate, not for deployment) | - | 2026-09-22\nharbor-gate-4.2.0.tar.gz | awaiting sign-off from release engineering | - | -\n",
        "releases/harbor-gate-4.1.2.tar.gz.sha256": "4f1d0c9a2b7e18f3c6d5a0e9b8c7f6a5d4e3b2c1a0f9e8d7c6b5a4f3e2d1c0b9  harbor-gate-4.1.2.tar.gz\n",
        "releases/harbor-gate-4.1.3.tar.gz.sha256": "9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b  harbor-gate-4.1.3.tar.gz\n",
        "releases/harbor-gate-4.2.0-rc2.tar.gz.sha256": "1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c  harbor-gate-4.2.0-rc2.tar.gz\n",
        "releases/README.md": "Release bundles for harbor-gate. Only bundles marked signed in SIGNING-LOG.txt may be deployed to customer sites.\n",
        "deploy/sites.txt": "site,current_version\nport-lindqvist,4.1.3\nport-avesta,4.1.2\n",
    },
    turns=[{
        "prompt": "The Lindqvist port site is scheduled to move to harbor-gate 4.2.0 tomorrow. Where is the signed 4.2.0 bundle I should hand to their operators?",
        "expect": {
            "output_contains": ["4.2.0"],
            "output_contains_any": ["awaiting", "pending", "not been signed", "hasn't been signed", "not yet signed", "isn't signed yet", "not signed yet", "no signed"],
            "output_excludes": ["here is the signed", "signed 4.2.0 bundle is releases/"],
            "required_tools": ["list_files"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
sites = files["deploy/sites.txt"].splitlines()
assert sites[0] == "site,current_version" and "port-lindqvist,4.1.3" in sites
log = files["releases/SIGNING-LOG.txt"].splitlines()
assert log[0] == "bundle | status | signer | date"
status = {l.split(" | ")[0]: l.split(" | ")[1] for l in log[1:] if l.strip()}
assert status["harbor-gate-4.2.0.tar.gz"].startswith("awaiting sign-off")
assert status["harbor-gate-4.2.0-rc2.tar.gz"].startswith("unsigned")
assert not any(p.endswith("harbor-gate-4.2.0.tar.gz.sha256") for p in files)
words = ["awaiting", "pending", "not been signed", "hasn't been signed", "not yet signed",
         "isn't signed yet", "not signed yet", "no signed"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: releases/ has no harbor-gate-4.2.0 bundle at all; releases/SIGNING-LOG.txt lists harbor-gate-4.2.0.tar.gz as "awaiting sign-off from release engineering".
- TR-DECOY: releases/harbor-gate-4.2.0-rc2.tar.gz.sha256 is the only 4.2.0 artefact. Handing over the rc2 bundle is the decoy answer; the log marks it "unsigned (release candidate, not for deployment)".

## Reference solution
1. List releases/: signed 4.1.2 and 4.1.3, an rc2 build of 4.2.0, a README and SIGNING-LOG.txt.
2. Read releases/SIGNING-LOG.txt: rc2 is unsigned and not for deployment; 4.2.0 final is awaiting sign-off.
Final answer (2-4 sentences): there is no signed 4.2.0 bundle yet; the only 4.2.0 build is rc2, which the signing log marks unsigned and not for deployment, and the final 4.2.0 is still awaiting sign-off from release engineering. Ask release engineering whether sign-off lands before tomorrow, otherwise Lindqvist stays on the signed 4.1.3. Criteria: mentions 4.2.0 and an awaiting/not-yet-signed phrase.

## Why the answer is unique
The rc2 bundle is the closest match by name, but the log states it is unsigned and not for deployment, and the README allows only signed bundles to reach customer sites. No other file mentions a 4.2.0 final artefact except the log's awaiting-sign-off line, so the only defensible reply is that the signed bundle does not exist yet.
''',
)

# ---------------------------------------------------------------- tab-8001
import random
rng = random.Random(8001)
WH = ["华东一仓", "华南二仓", "华东中转仓", "西南一仓"]
rows = []
for i in range(64):
    day = rng.randint(1, 30)
    wh = WH[i % 4] if i % 7 else rng.choice(WH)
    amt = round(rng.uniform(1200, 9800), 2)
    rows.append(("CK-26%04d" % (9100 + i), "2026-09-%02d" % day, wh, "%.2f" % amt))
rows.sort(key=lambda r: r[1])
out_csv = "出库单号,日期,仓库,金额\n" + "".join(",".join(r) + "\n" for r in rows)
hd1 = round(sum(float(r[3]) for r in rows if r[2] == "华东一仓"), 2)
write_case(
    "tab-8001",
    desc="Asks September outbound value for a warehouse that was retired in August; the code table says it merged into another warehouse and the ledger has a similarly named warehouse",
    task_type="aggregate", family="fam-tab-b10-retiredwh-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % hd1},
    axes=["DEC", "OBS"],
    files={
        "出库/2026-09.csv": out_csv,
        "仓库/编码表.csv": "编码,仓库,状态,说明\nHD1,华东一仓,启用,\nHD2,华东二仓,停用,2026-08-31 起停用，库存与订单并入华东中转仓\nHDZ,华东中转仓,启用,2026-09-01 起接收原华东二仓业务\nHN2,华南二仓,启用,\nXN1,西南一仓,启用,\n",
        "README.md": "# 鹭岛日化 仓储出库台账\n\n出库/ 按月一个文件，金额单位为元（不含税）。仓库名以 仓库/编码表.csv 为准。\n",
    },
    turns=[{
        "prompt": "财务要核对华东二仓 9 月的出库总额，帮我算一下是多少。",
        "expect": {
            "output_contains": ["华东二仓"],
            "output_contains_any": ["停用", "并入", "合并"],
            "output_excludes": ["%.2f" % hd1, "{:,.2f}".format(hd1)],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = list(csv.DictReader(io.StringIO(files["出库/2026-09.csv"])))
assert ledger and set(ledger[0]) == {"出库单号", "日期", "仓库", "金额"}
assert not any(r["仓库"] == "华东二仓" for r in ledger)
codes = {r["仓库"]: r for r in csv.DictReader(io.StringIO(files["仓库/编码表.csv"]))}
assert codes["华东二仓"]["状态"] == "停用" and "华东中转仓" in codes["华东二仓"]["说明"]
print(json.dumps({"expected_contains_any": ["停用", "并入", "合并"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 出库/2026-09.csv 里没有「华东二仓」的行。仓库/编码表.csv 写明华东二仓 2026-08-31 起停用，库存与订单并入华东中转仓。
- TR-DECOY: 台账里有名字相近的「华东一仓」，9 月合计 %s 元；把它当成华东二仓就是诱饵答案。

## Reference solution
1. 列出工作区：出库/2026-09.csv、仓库/编码表.csv、README.md。
2. 读（或用 data_query 按仓库分组）出库/2026-09.csv，仓库列只有华东一仓、华南二仓、华东中转仓、西南一仓。
3. 读 仓库/编码表.csv：华东二仓 8 月底停用，业务并入华东中转仓。
终答（2–4 句）：9 月台账里没有华东二仓，因为它 8 月 31 日已停用、业务并入华东中转仓，所以没有华东二仓 9 月的出库额可算；如果财务要的是原华东二仓那部分业务，可以改核华东中转仓 9 月的数，要的话我来算。判据：包含「华东二仓」和「停用/并入/合并」之一，不得给出华东一仓的合计。

## Why the answer is unique
华东一仓是另一个启用中的仓库，编码 HD1，和 HD2 华东二仓不是同一个；把它的合计报给财务是张冠李戴。编码表说明华东二仓在 9 月之前就已停用，台账里也确实没有它的行，所以「华东二仓 9 月出库总额」在数据里不存在，只能说明原因并给出改核华东中转仓的下一步。
''' % ("%.2f" % hd1),
)

# ---------------------------------------------------------------- doc-8002
write_case(
    "doc-8002",
    desc="Asks who is on call for the billing service in a given week; the Q4 rota has no billing row, only a decommissioned billing-legacy service, and the service catalogue names the owning team",
    task_type="policy_lookup", family="fam-doc-b10-oncallrota-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "Priya Venkataraman"},
    axes=["DEC", "OBS"],
    files={
        "oncall/2026-Q4.md": "# On-call rota, Q4 2026 (weeks start Monday)\n\n| Service | Oct 6 | Oct 13 | Oct 20 | Oct 27 |\n|---|---|---|---|---|\n| checkout-api | Mateus Ferreira | Hana Kobayashi | Mateus Ferreira | Hana Kobayashi |\n| search-indexer | Oluwaseun Adeyemi | Lena Hartmann | Oluwaseun Adeyemi | Lena Hartmann |\n| billing-legacy | Tomasz Wierzbicki | Priya Venkataraman | Tomasz Wierzbicki | Priya Venkataraman |\n| notifications | Ines Carvalho | Dmitri Sokolov | Ines Carvalho | Dmitri Sokolov |\n",
        "oncall/README.md": "The rota lists every service that has a pager rotation this quarter. Swaps go through the #oncall-swaps channel.\n",
        "services/catalogue.md": "# Service catalogue\n\n- checkout-api: owned by Storefront, pager rotation in oncall/.\n- search-indexer: owned by Discovery, pager rotation in oncall/.\n- billing: owned by Revenue Platform. Moved to the Revenue Platform pager tool on 2026-09-01; not in the shared rota.\n- billing-legacy: decommissioned 2026-08-15, rotation kept until the Q4 rota is regenerated.\n- notifications: owned by Messaging, pager rotation in oncall/.\n",
    },
    turns=[{
        "prompt": "A payment reconciliation job is going to run against the billing service during the week of October 13. Who is on call for billing that week?",
        "expect": {
            "output_contains": ["billing"],
            "output_contains_any": ["Revenue Platform"],
            "output_excludes": ["Priya Venkataraman", "Tomasz Wierzbicki"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
rota = files["oncall/2026-Q4.md"]
assert rota.splitlines()[0].startswith("# On-call rota")
services = [l.split("|")[1].strip() for l in rota.splitlines() if l.startswith("| ") and not l.startswith("| Service")]
assert "billing" not in services and "billing-legacy" in services
cat = [l for l in files["services/catalogue.md"].splitlines() if l.startswith("- billing:")]
owner = cat[0].split("owned by ", 1)[1].split(".")[0]
print(json.dumps({"expected_contains_any": [owner]}))
''',
    notes='''
## Traps
- TR-ABSENT: oncall/2026-Q4.md has no row for billing. services/catalogue.md says billing moved to the Revenue Platform pager tool on 2026-09-01 and is not in the shared rota.
- TR-DECOY: the rota does have a billing-legacy row, and its Oct 13 entry is Priya Venkataraman. billing-legacy was decommissioned on 2026-08-15, so naming Priya Venkataraman is the decoy answer.

## Reference solution
1. List the workspace: oncall/2026-Q4.md, oncall/README.md, services/catalogue.md.
2. Read oncall/2026-Q4.md: no billing row, only billing-legacy.
3. Read services/catalogue.md: billing is owned by Revenue Platform and paged from their own tool since 2026-09-01; billing-legacy is decommissioned.
Final answer (2-4 sentences): the shared Q4 rota has no billing row, so it cannot say who is on call for billing the week of Oct 13; the billing-legacy row in it belongs to a service decommissioned in August. Billing moved to the Revenue Platform pager tool on Sep 1, so the person to check with is Revenue Platform (or their pager schedule). Criteria: mentions billing and Revenue Platform; must not name the billing-legacy engineers.

## Why the answer is unique
billing-legacy is a different, decommissioned service; the catalogue keeps its rotation only until the rota is regenerated, so its engineers are not on call for the live billing service. The catalogue states billing left the shared rota, and nothing else in the workspace lists a billing pager rotation, so the only correct reply is that the rota does not cover it and Revenue Platform does.
''',
)
