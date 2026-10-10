"""b10a (v1.4 §3.2) M2 part A: target absent with a near-match decoy.

18 cases: cfg-8012..cfg-8021 (config scenario) and doc-8006..doc-8013 (docs
scenario). Chinese cases keep the whole fixture in Chinese; domains are
ceramics workshops/kilns and library/reading-room management (zh) and
GIS/mapping services (en). Shapes follow the b10 pilot cfg-8001 / doc-8001 /
fs-8001 / tab-8001 / doc-8002; proper names are new and do not repeat across
the batch. Every verify.py pins the first line of the file `bank verify`'s
sabotage test deletes first (ext order .csv < ... < .yaml < .md, then path).

Run: cd bench/distill/tools/b10a && python3 m2a.py
"""
from common import revised

write_case = revised({'doc-8009': '排除项改为「把 2025-09-01 说成修订版生效日」的说法：S5 三遍老师都正确说明「暂行版自 2025-09-01 起施行、修订版待签署」，被裸日期误判。'})

NEG_ZH = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没"]
NEG_EN = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
          "not in the", "not on the", "no row", "missing", "not covered"]


def zh_words(words):
    """verify.py tail that echoes the acceptable surface forms (zh output)."""
    return "words = " + repr(words) + \
        '\nprint(json.dumps({"expected_contains_any": words}, ensure_ascii=False))\n'


def en_words(words):
    """verify.py tail that echoes the acceptable surface forms."""
    return "words = " + repr(words) + \
        '\nprint(json.dumps({"expected_contains_any": words}))\n'


# ---------------------------------------------------------------- cfg-8012
write_case(
    "cfg-8012",
    desc="Firing-curve question for a new electric kiln that has no config file; only two gas kilns and a test electric kiln exist and the equipment ledger says the new kiln's curve is pending submission",
    task_type="read_effective", family="fam-cfg-b10-kilncurve-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 1150},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 拾青陶艺工坊 窑炉配置\n\n每座窑在 窑炉/ 下放一份 yaml，文件名就是窑名。\n新窑由烧成工艺组提交升温曲线后才建配置文件。\n",
        "窑炉/1号气窑.yaml": "窑名: 1号气窑\n燃料: 液化气\n升温曲线:\n  - 600℃ 前每小时升 80℃\n  - 800℃ 起转还原气氛\n最高保温温度: 1250\n保温时长: 40 分钟\n",
        "窑炉/3号气窑.yaml": "窑名: 3号气窑\n燃料: 液化气\n升温曲线:\n  - 650℃ 前每小时升 90℃\n最高保温温度: 1280\n保温时长: 50 分钟\n",
        "窑炉/试验电窑.yaml": "窑名: 试验电窑\n用途: 试片与釉色试验\n升温曲线:\n  - 每小时升 150℃\n最高保温温度: 1150\n备注: 只烧试片，不接生产订单，不用于成品烧成\n",
        "设备/窑炉台账.md": "# 窑炉台账\n\n| 窑名 | 状态 | 说明 |\n|---|---|---|\n| 1号气窑 | 在用 | 2024-03 投用 |\n| 3号气窑 | 在用 | 2025-06 投用 |\n| 试验电窑 | 在用 | 只做试片 |\n| 5号电窑 | 基础安装完成 | 升温曲线待提交，烧成工艺组负责，计划 2026-10-18 提交；提交前不排产 |\n",
    },
    turns=[{
        "prompt": "拾青陶艺工坊准备把新烧的一批青瓷盏放进 5号电窑，5号电窑 的最高保温温度是多少？",
        "expect": {
            "output_contains": ["5号电窑", "电窑"],
            "output_contains_any": NEG_ZH + ["待提交", "未提交", "没提交"],
            "output_excludes": ["1150"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 窑炉/1号气窑.yaml ranks first (.yaml sorts before .md).
assert files["窑炉/1号气窑.yaml"].splitlines()[0] == "窑名: 1号气窑"
assert not any(p.startswith("窑炉/5号") for p in files)
test_kiln = files["窑炉/试验电窑.yaml"]
assert "试片" in test_kiln and "不接生产订单" in test_kiln
ledger = files["设备/窑炉台账.md"]
assert any("5号电窑" in l and "待提交" in l for l in ledger.splitlines())
''' + zh_words(NEG_ZH + ["待提交", "未提交", "没提交"]),
    notes='''
## Traps
- TR-ABSENT: 窑炉/ 下没有 5号电窑 的配置；设备/窑炉台账.md 写明 5号电窑「升温曲线待提交」，烧成工艺组负责，计划 2026-10-18 提交，提交前不排产。
- TR-DECOY: 窑炉/试验电窑.yaml 也叫电窑，最高保温温度 1150。把试片窑的 1150 当 5号电窑 的最高保温温度，就是诱饵答案。

## Reference solution
1. 列出工作区：窑炉/ 下只有 1号气窑、3号气窑、试验电窑三份配置，另有 设备/窑炉台账.md。
2. 读 窑炉/试验电窑.yaml，确认它是试片窑、不接生产订单。
3. 读 设备/窑炉台账.md：5号电窑 基础安装完成，升温曲线待提交（烧成工艺组，计划 2026-10-18）。
终答（2–4 句）：5号电窑 还没有升温曲线可查——窑炉/ 下只有两座在用气窑和一座只烧试片的试验电窑，台账写明 5号电窑 的曲线由烧成工艺组待提交（计划 10 月 18 日），提交前不排产。试验电窑虽然也叫电窑，但只做釉色试验，温度口径和成品烧成不一样。可以找烧成工艺组要曲线，等提交后我再帮你核对。判据：包含「5号电窑」「电窑」和一个否定/待提交说法，不得出现 1150。

## Why the answer is unique
诱饵 1150 错在对象和用途都不对：试验电窑的备注写明只烧试片、不接生产订单，与成品烧成用的 5号电窑 不是同一座窑，键名同是「最高保温温度」但口径不同。1号气窑、3号气窑 是别的窑。台账证实 5号电窑 的曲线还没提交，工作区里不存在任何能读出它最高保温温度的地方，所以唯一站得住的回答是说明查不到、点出试验电窑不是它、给出找烧成工艺组的下一步。
''',
)

# ---------------------------------------------------------------- cfg-8013
write_case(
    "cfg-8013",
    desc="Asks the current feldspar share of a glaze pulled in July for lead leaching; the recipe body was deleted per policy, only similarly named glazes are on file, and the revision log says a replacement is under review",
    task_type="read_effective", family="fam-cfg-b10-glazerecipe-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "18.5"},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 鹿溪陶坊 釉料配比\n\n釉料/ 按釉名存放现行配方，文件名就是釉名；配比单位为质量份。\n停用或重配中的釉不保留正文，只在 釉料/修订记录.md 登记。\n",
        "釉料/修订记录.md": "# 釉料修订记录\n\n| 釉名 | 版本 | 状态 | 说明 |\n|---|---|---|---|\n| 月白釉 | 2026 版 | 现行 | 2026-02-10 复核 |\n| 青灰釉 | 2026 版 | 现行 | 2026-03-22 复核 |\n| 天蓝釉 | 2026 版 | 现行 | 2026-04-15 复核 |\n| 天青釉 | 2025 版 | 停用 | 2026-07-12 铅析出超标，全批停用；釉料组重配中，新配方待复核，正文已按制度删除 |\n",
        "釉料/月白釉.yaml": "釉名: 月白釉\n长石: 30\n石英: 25\n方解石: 12\n砂泥: 33\n",
        "釉料/青灰釉.yaml": "釉名: 青灰釉\n长石: 26\n石英: 30\n方解石: 10\n砂泥: 34\n",
        "釉料/天蓝釉.yaml": "釉名: 天蓝釉\n长石: 18.5\n石英: 28\n方解石: 15\n砂泥: 38.5\n",
    },
    turns=[{
        "prompt": "鹿溪陶坊下周要复烧一批天青釉茶具，天青釉 现行配方的 长石 占比是多少？",
        "expect": {
            "output_contains": ["天青釉"],
            "output_contains_any": NEG_ZH + ["停用", "重配", "超标"],
            "output_excludes": ["18.5", "18.5%"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 釉料/天蓝釉.yaml ranks first (.yaml sorts before .md; 天 < 月 < 青).
assert files["釉料/天蓝釉.yaml"].splitlines()[0] == "釉名: 天蓝釉"
assert not any("天青釉" in p for p in files)
log = files["釉料/修订记录.md"]
row = [l for l in log.splitlines() if "天青釉" in l and "停用" in l]
assert row and "重配" in row[0] and "删除" in row[0]
blue = [l for l in files["釉料/天蓝釉.yaml"].splitlines() if l.startswith("长石:")]
assert blue and blue[0] == "长石: 18.5"
''' + zh_words(NEG_ZH + ["停用", "重配", "超标"]),
    notes='''
## Traps
- TR-ABSENT: 釉料/ 下没有 天青釉 的配方；釉料/修订记录.md 写明天青釉 2026-07-12 起铅析出超标全批停用，正文已按制度删除，釉料组重配中、新配方待复核。
- TR-DECOY: 釉料/天蓝釉.yaml 名字与天青釉只差一字，长石 18.5 份。把天蓝釉的长石占比当天青釉的，就是诱饵答案。

## Reference solution
1. 列出 釉料/：只有月白釉、青灰釉、天蓝釉三份现行配方和修订记录。
2. 读 釉料/修订记录.md：天青釉 7 月 12 日起停用、正文已删、新配方待复核。
3. 读 釉料/天蓝釉.yaml，确认它是另一支釉，不是天青釉。
终答（2–4 句）：天青釉 7 月 12 日起全批停用——铅析出超标，配方正文已按制度删除，釉料组重配的新配方还没复核，所以现在查不到它的现行长石占比；釉料/ 下名字相近的是天蓝釉、月白釉、青灰釉，都是别的釉。复烧建议等新配方复核通过，或者直接问釉料组要过渡配比。判据：包含「天青釉」和一个「停用/重配/超标」说法，不得出现 18.5。

## Why the answer is unique
诱饵 18.5 错在张冠李戴：天蓝釉是另一支现行釉，修订记录里四个釉名一一对应，天青釉一行写明停用且正文已删。月白釉、青灰釉同样是别的釉。README 规定停用釉不保留正文，所以工作区里不存在任何能读出天青釉配比的来源，唯一站得住的回答是说明停用原因、点出相近釉不是它、给出找釉料组的下一步。
''',
)

# ---------------------------------------------------------------- cfg-8014
write_case(
    "cfg-8014",
    desc="Asks the atomizing pressure of a wood kiln sealed in August with its parameter file deleted; the sealing record says its large work moved to the active wood kiln, whose pressure is the decoy",
    task_type="read_effective", family="fam-cfg-b10-kilnretire-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "0.32"},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 壶山陶业 窑炉参数\n\n各窑参数以 窑炉/ 下的 yaml 为准；封存窑不保留参数文件，封存情况见 设备/封存记录.md。\n",
        "窑炉/4号柴窑.yaml": "窑名: 4号柴窑\n燃料: 松柴\n雾化压力: 0.32 MPa\n最高保温温度: 1320\n",
        "窑炉/6号气窑.yaml": "窑名: 6号气窑\n燃料: 天然气\n烧成气氛: 氧化\n最高保温温度: 1260\n",
        "设备/封存记录.md": "# 窑炉封存记录\n\n| 窑名 | 日期 | 说明 |\n|---|---|---|\n| 2号柴窑 | 2026-08-20 | 窑体开裂封存，燃烧器已拆检，参数文件同日删除；大件烧成转移至 4号柴窑 |\n",
    },
    turns=[{
        "prompt": "壶山陶业这周要给老客户的大缸开窑，2号柴窑 的雾化压力设定是多少？",
        "expect": {
            "output_contains": ["2号柴窑", "柴窑"],
            "output_contains_any": NEG_ZH + ["封存", "停用", "拆检"],
            "output_excludes": ["0.32", "0.32 MPa", "0.32MPa"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 窑炉/4号柴窑.yaml ranks first among the yaml files ("4" < "6").
assert files["窑炉/4号柴窑.yaml"].splitlines()[0] == "窑名: 4号柴窑"
assert not any("2号柴窑" in p for p in files)
seal = files["设备/封存记录.md"]
row = [l for l in seal.splitlines() if "2号柴窑" in l]
assert row and "封存" in row[0] and "删除" in row[0] and "4号柴窑" in row[0]
''' + zh_words(NEG_ZH + ["封存", "停用", "拆检"]),
    notes='''
## Traps
- TR-ABSENT: 窑炉/ 下没有 2号柴窑 的参数文件；设备/封存记录.md 写明它 2026-08-20 窑体开裂封存、燃烧器拆检、参数文件同日删除。
- TR-DECOY: 窑炉/4号柴窑.yaml 接了它的活，雾化压力 0.32 MPa。把 4号柴窑 的压力当 2号柴窑 的设定，就是诱饵答案。

## Reference solution
1. 列出 窑炉/：只有 4号柴窑 和 6号气窑 两份参数。
2. 读 设备/封存记录.md：2号柴窑 8 月 20 日封存，参数文件同日删除，大件烧成转给 4号柴窑。
3. 读 窑炉/4号柴窑.yaml，确认它是接活的另一座窑。
终答（2–4 句）：2号柴窑 8 月 20 日起封存——窑体开裂、燃烧器已拆检，参数文件当天就删了，所以没有雾化压力可查；它的大件烧成已经转给在用的 4号柴窑，但那是另一座窑，参数不能混用。大缸建议改排 4号柴窑（需要的话我去查它的参数），或者等 2号柴窑 修复解封。判据：包含「2号柴窑」「柴窑」和一个「封存/停用/拆检」说法，不得出现 0.32。

## Why the answer is unique
诱饵 0.32 错在对象不对：它是 4号柴窑 的现值，封存记录写明两座窑是转移关系而不是同一座，接活不等于参数沿用。6号气窑 是气窑，没有雾化压力。README 规定封存窑不保留参数文件，记录也写明同日删除，所以工作区里没有 2号柴窑 的任何参数，唯一站得住的回答是说明封存、点出 4号柴窑 不是它、给出改排或等解封的下一步。
''',
)

# ---------------------------------------------------------------- cfg-8015
write_case(
    "cfg-8015",
    desc="Asks the glaze dwell delay of a glazing line; neither the base config nor the production override sets it, the docs say a firmware built-in default applies and changes between firmware versions, and the spray interval is the decoy",
    task_type="read_effective", family="fam-cfg-b10-glazeline-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 45},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 青崖陶艺 施釉线\n\n现行参数在 config/施釉线.yaml，按环境的覆盖在 config/env/，参数含义见 docs/施釉线说明.md。\n",
        "config/施釉线.yaml": "链速毫米秒: 25\n喷釉间隔秒: 45\n喷枪数: 6\n釉液粘度帕秒: 1.8\n",
        "config/env/量产.yaml": "链速毫米秒: 31\n喷釉间隔秒: 40\n",
        "docs/施釉线说明.md": "# 施釉线参数说明\n\n- 链速毫米秒: 链条每秒前进的距离。\n- 喷釉间隔秒: 相邻两把喷枪喷釉的间隔时间。\n- 流釉延时秒: 喷釉结束后釉液流平的延时。未设置时沿用固件内置默认值，固件内置值随固件版本变化，量产前建议在配置里写死。\n- 釉液粘度帕秒: 釉液粘度。\n",
    },
    turns=[{
        "prompt": "青崖陶艺在排查釉面流痕，施釉线 的流釉延时现在是多少？",
        "expect": {
            "output_contains": ["流釉延时"],
            "output_contains_any": NEG_ZH + ["未设置", "没有设置", "没设置", "未配置", "没有配置"],
            "output_excludes": ["45", "45 秒", "45秒", "45 s"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: config/env/量产.yaml sorts first among the yaml files.
assert files["config/env/量产.yaml"].splitlines()[0] == "链速毫米秒: 31"
for path in ("config/施釉线.yaml", "config/env/量产.yaml"):
    assert "流釉延时" not in files[path]
doc = files["docs/施釉线说明.md"]
line = [l for l in doc.splitlines() if l.startswith("- 流釉延时秒:")][0]
assert "未设置" in line and "固件" in line
''' + zh_words(NEG_ZH + ["未设置", "没有设置", "没设置", "未配置", "没有配置"]),
    notes='''
## Traps
- TR-ABSENT: config/施釉线.yaml 和 config/env/量产.yaml 都没有 流釉延时秒 这个键；docs/施釉线说明.md 写明未设置时沿用固件内置默认值，且随固件版本变化。
- TR-DECOY: 配置里的 喷釉间隔秒 45 是另一个参数。把 45 秒当流釉延时，就是诱饵答案。

## Reference solution
1. 读 config/施釉线.yaml：只有链速、喷釉间隔、喷枪数、粘度，没有流釉延时。
2. 读 config/env/量产.yaml：量产覆盖同样没有流釉延时。
3. 读 docs/施釉线说明.md：流釉延时秒未设置时用固件内置默认值，随固件版本变化。
终答（2–4 句）：施釉线没有设置流釉延时：基础配置和量产环境的覆盖里都没有这个键，说明文件写明未设置时用固件内置默认值、且随固件版本变化，所以现值查不到。排查流痕时注意喷釉间隔是另一个参数，不是它。要定下来可以在配置里写死，或先确认现用固件版本的内置值。判据：包含「流釉延时」和一个「未设置/没有设置」说法，不得把 45 秒当答案。

## Why the answer is unique
诱饵 45 错在参数不同：说明文件逐条定义了键名，喷釉间隔秒管的是喷枪间隔，流釉延时秒管的是喷后流平，两者无关；且量产覆盖只覆盖了链速和喷釉间隔，没有流釉延时。固件内置值工作区里没有记录，报任何数都是编造，所以唯一站得住的回答是说明未设置、指向固件默认值并建议写死。
''',
)

# ---------------------------------------------------------------- cfg-8016
write_case(
    "cfg-8016",
    desc="Energy audit asks the idle power draw of a newly purchased kiln that has not been commissioned; the ledger marks acceptance pending with the no-load test scheduled, and no power figure exists anywhere in the workspace",
    task_type="read_effective", family="fam-cfg-b10-kilnpower-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"},
    axes=["DEC"],
    files={
        "README.md": "# 素泥陶社 设备档案\n\n窑炉运行参数以 设备/窑炉台账.md 为准；台账未登记的参数以现场实测为准，未测的参数不预估。\n",
        "设备/窑炉台账.md": "# 窑炉台账\n\n| 窑名 | 状态 | 上次年检 | 备注 |\n|---|---|---|---|\n| 2号气窑 | 在用 | 2026-03-15 | |\n| 4号柴窑 | 在用 | 2026-05-08 | |\n| 6号电窑 | 新购未验收 | — | 空载测试安排在 2026-10-24，设备组完成并登记后才能排产 |\n",
        "设备/验收计划.md": "# 6号电窑 验收计划\n\n- 空载测试：2026-10-24，设备组负责，测得的数据直接登记进台账。\n- 负载试烧：空载测试通过后另行排期。\n- 测试完成前 6号电窑 不计入产能。\n",
    },
    turns=[{
        "prompt": "素泥陶社要给 6号电窑 做能效核算，6号电窑 的空载功耗是多少？",
        "expect": {
            "output_contains": ["6号电窑"],
            "output_contains_any": NEG_ZH + ["待测试", "未测试", "没有测试", "尚未测试", "还没测试", "未验收", "没有验收"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 素泥陶社 设备档案"
ledger = files["设备/窑炉台账.md"]
row = [l for l in ledger.splitlines() if "6号电窑" in l]
assert row and "未验收" in row[0] and "2026-10-24" in row[0]
assert "kW" not in ledger and "kW" not in files["设备/验收计划.md"]
''' + zh_words(NEG_ZH + ["待测试", "未测试", "没有测试", "尚未测试", "还没测试", "未验收", "没有验收"]),
    notes='''
## Traps
- TR-ABSENT: 设备/窑炉台账.md 里 6号电窑 是「新购未验收」，空载测试安排在 2026-10-24，数据要测完才登记；设备/验收计划.md 也是计划，没有实测值。工作区里没有任何功耗数值，没有相近诱饵，错误形态只有编造数值或裸答 UNKNOWN。

## Reference solution
1. 读 设备/窑炉台账.md：6号电窑 新购未验收，空载测试安排在 2026-10-24，完成后才登记。
2. 读 设备/验收计划.md：确认测试还没做、完成前不排产。
终答（2–4 句）：6号电窑 还没做空载测试：台账里它是新购未验收，测试安排在 10 月 24 日，由设备组完成后登记进台账，所以现在没有空载功耗可算。能效核算建议等测试数据出来再做，或者先只核算在用的几座窑。判据：包含「6号电窑」和一个「待测试/未验收/没有」说法；不得编造功耗数值。

## Why the answer is unique
工作区里唯一的 6号电窑 信息是台账与验收计划，两处都写明测试未做、数据未登记，也没有任何其他窑的功耗数值可以拿来顶替。README 规定未测的参数不预估，所以任何数值都是编造，唯一站得住的回答是说明未验收、指向 10 月 24 日的测试安排。
''',
)

# ---------------------------------------------------------------- cfg-8017
write_case(
    "cfg-8017",
    desc="Trial production asks the per-shift beat of a line still under construction; only the glaze-fired and packing lines have parameter files, and the ledger says the new line's parameters are pending submission",
    task_type="read_effective", family="fam-cfg-b10-kilnline-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 380},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 云岫陶瓷 产线参数\n\n各产线参数在 产线/ 下按线名一份 yaml；在建产线由工艺组提交参数后才建文件，产线状态见 设备/产线台账.md。\n",
        "产线/釉烧线.yaml": "线名: 釉烧线\n单班节拍: 380\n烧成温度: 1220\n",
        "产线/包装线.yaml": "线名: 包装线\n单班节拍: 220\n",
        "设备/产线台账.md": "# 产线台账\n\n| 产线 | 状态 | 说明 |\n|---|---|---|\n| 釉烧线 | 在产 | 2025-09 投产 |\n| 包装线 | 在产 | 2024-11 投产 |\n| 素烧线 | 在建 | 单班节拍待提交，工艺组负责，计划 2026-10-22 提交，提交前不排试产 |\n",
    },
    turns=[{
        "prompt": "云岫陶瓷的素烧线下周要试产，素烧线 的单班节拍是多少？",
        "expect": {
            "output_contains": ["素烧线"],
            "output_contains_any": NEG_ZH + ["待提交", "未提交", "没提交", "在建"],
            "output_excludes": ["380"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 产线/包装线.yaml sorts first among the yaml files (包 < 釉).
assert files["产线/包装线.yaml"].splitlines()[0] == "线名: 包装线"
assert not any(p.startswith("产线/素烧线") for p in files)
ledger = files["设备/产线台账.md"]
row = [l for l in ledger.splitlines() if "素烧线" in l]
assert row and "在建" in row[0] and "待提交" in row[0]
''' + zh_words(NEG_ZH + ["待提交", "未提交", "没提交", "在建"]),
    notes='''
## Traps
- TR-ABSENT: 产线/ 下没有 素烧线 的参数文件；设备/产线台账.md 写明素烧线在建、单班节拍待工艺组提交（计划 2026-10-22），提交前不排试产。
- TR-DECOY: 产线/釉烧线.yaml 名字与素烧线只差一字，单班节拍 380。把釉烧线的节拍当素烧线的，就是诱饵答案。

## Reference solution
1. 列出 产线/：只有釉烧线和包装线两份参数。
2. 读 设备/产线台账.md：素烧线在建，节拍待工艺组提交，提交前不排试产。
3. 读 产线/釉烧线.yaml，确认它是另一条在产线。
终答（2–4 句）：素烧线还在建，单班节拍由工艺组待提交（产线台账写明计划 10 月 22 日提交，提交前不排试产），所以现在没有可查的节拍值；产线/ 下只有釉烧线和包装线的参数，都不是它。试产排期要等参数提交后再定，或者找工艺组催一下进度。判据：包含「素烧线」和一个「待提交/在建/没有」说法，不得出现 380。

## Why the answer is unique
诱饵 380 错在对象不对：釉烧线是在产的另一条线，台账里三条线状态一一对应，素烧线写明在建。包装线的 220 同样是别的线。README 规定在建产线提交参数后才建文件，台账也证实还没提交，工作区里不存在素烧线的节拍来源，唯一站得住的回答是说明在建与待提交、点出釉烧线不是它、给出等提交或催工艺组的下一步。
''',
)

# ---------------------------------------------------------------- cfg-8018
write_case(
    "cfg-8018",
    desc="Launch call asks the cache TTL of the terrain tileset; tilesets/ has streets, outdoors and a QA-only terrain-sandbox but no terrain config, and the rollout plan lists terrain as pending submission from the imagery team",
    task_type="read_effective", family="fam-cfg-b10-tilettl-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 600},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# Mapworth Geospatial tile service configs\n\nEach tileset has one config under tilesets/, named after the tileset. Rollout state is tracked in deploy/rollout.md.\n",
        "tilesets/streets.toml": "max_age = 3600\nmin_zoom = 0\nmax_zoom = 20\n",
        "tilesets/outdoors.toml": "max_age = 86400\nmin_zoom = 0\nmax_zoom = 18\n",
        "tilesets/terrain-sandbox.toml": "max_age = 600\nmin_zoom = 5\nmax_zoom = 14\nnote = \"QA sandbox with synthetic tiles, not for customer traffic\"\n",
        "deploy/rollout.md": "# Tileset rollout\n\n| tileset | state | planned | owner |\n|---|---|---|---|\n| streets | live | - | platform |\n| outdoors | live | - | platform |\n| terrain | config pending submission | 2026-10-17 | imagery team |\n",
    },
    turns=[{
        "prompt": "Customer success wants the terrain tileset's cache TTL for Thursday's launch call. What max-age does terrain serve tiles with?",
        "expect": {
            "output_contains": ["terrain"],
            "output_contains_any": NEG_EN + ["pending", "not yet submitted", "awaiting", "hasn't been submitted"],
            "output_excludes": ["600"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md ranks first (.md sorts before .toml).
assert files["README.md"].splitlines()[0] == "# Mapworth Geospatial tile service configs"
assert not any(p == "tilesets/terrain.toml" for p in files)
sandbox = files["tilesets/terrain-sandbox.toml"]
assert "max_age = 600" in sandbox and "not for customer traffic" in sandbox
rollout = files["deploy/rollout.md"]
row = [l for l in rollout.splitlines() if l.startswith("| terrain ")]
assert row and "pending" in row[0]
''' + en_words(NEG_EN + ["pending", "not yet submitted", "awaiting", "hasn't been submitted"]),
    notes='''
## Traps
- TR-ABSENT: tilesets/ has no terrain.toml; deploy/rollout.md lists terrain as "config pending submission" from the imagery team, planned 2026-10-17.
- TR-DECOY: tilesets/terrain-sandbox.toml is the only terrain-named config, max_age = 600. Quoting the sandbox's 600 as terrain's cache TTL is the decoy answer.

## Reference solution
1. List tilesets/: configs for streets, outdoors and terrain-sandbox, no terrain.
2. Read tilesets/terrain-sandbox.toml: QA sandbox with synthetic tiles, not for customer traffic.
3. Read deploy/rollout.md: terrain is config pending submission, imagery team, planned 2026-10-17.
Final answer (2-4 sentences): there is no max-age to read for terrain — tilesets/ has streets and outdoors plus a terrain-sandbox, but no terrain config, and the rollout plan lists terrain as config pending submission from the imagery team (planned 2026-10-17). The sandbox tileset is QA-only with synthetic tiles, so its values do not apply to the launch. For Thursday's call, either ask the imagery team whether the config lands in time or present the rollout plan. Criteria: mentions terrain and a pending/not-submitted phrase; must not present 600 as the TTL.

## Why the answer is unique
The sandbox config fails on both object and traffic: its note marks it QA-only with synthetic tiles, not for customer traffic, so it is not the production terrain tileset the launch call is about. streets and outdoors are other tilesets. The rollout plan is the authoritative rollout state and shows terrain has no config yet, so any max-age would be invented; the only defensible reply points to the imagery team's pending submission.
''',
)

# ---------------------------------------------------------------- cfg-8019
write_case(
    "cfg-8019",
    desc="Latency tuning asks the production request timeout of wms-gateway; neither the base nor the production config sets request_timeout_ms, the docs say the mapkit client library default applies, and the health-probe interval is the decoy",
    task_type="read_effective", family="fam-cfg-b10-wmstimeout-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 90},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# wms-gateway settings\n\nBase config in config/wms-gateway.toml; per-environment overrides in config/env/. Parameter reference in docs/wms-config.md.\n",
        "config/wms-gateway.toml": "[server]\nworkers = 4\n\n[cache]\nmax_entries = 4096\n\n[probe]\npath = \"/healthz\"\ninterval_s = 90\n",
        "config/env/production.toml": "[server]\nworkers = 12\n\n[cache]\nmax_entries = 8192\n\n[logging]\nlevel = \"warn\"\n",
        "docs/wms-config.md": "# wms-gateway parameters\n\n- request_timeout_ms: per-request timeout. When unset, the gateway uses the timeout built into the mapkit client library, which has changed between mapkit releases. Pin it explicitly for production.\n- probe.interval_s: how often the orchestrator re-probes /healthz after a failed probe. Unrelated to request timeouts.\n- cache.max_entries: tile cache size in entries.\n",
    },
    turns=[{
        "prompt": "After last night's WMS latency spike we are tuning the gateway. What request timeout does wms-gateway use in production?",
        "expect": {
            "output_contains": ["mapkit"],
            "output_contains_any": ["not set", "isn't set", "not configured", "isn't configured", "not defined", "doesn't set", "does not set", "no request_timeout_ms", "unset", "neither"],
            "output_excludes": ["90", "90 seconds", "90s", "90-second"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first (.md before .toml).
assert files["README.md"].splitlines()[0] == "# wms-gateway settings"
for path in ("config/wms-gateway.toml", "config/env/production.toml"):
    assert "request_timeout_ms" not in files[path]
probe = [l for l in files["config/wms-gateway.toml"].splitlines() if l.startswith("interval_s")]
assert probe and probe[0] == "interval_s = 90"
doc = files["docs/wms-config.md"]
line = [l for l in doc.splitlines() if l.startswith("- request_timeout_ms:")][0]
lib = line.split("built into the ")[1].split(" ")[0]
print(json.dumps({"expected_string": lib}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/wms-gateway.toml nor config/env/production.toml sets request_timeout_ms. docs/wms-config.md says the unset value falls back to the timeout built into the mapkit client library, which has changed between mapkit releases.
- TR-DECOY: config/wms-gateway.toml has [probe] interval_s = 90. Reporting a 90-second request timeout is the decoy answer; the docs state the probe interval is how often /healthz is re-probed and is unrelated to request timeouts.

## Reference solution
1. Read config/wms-gateway.toml: no request_timeout_ms; only the probe interval_s.
2. Read config/env/production.toml: overrides workers, cache size and logging only.
3. Read docs/wms-config.md: unset request_timeout_ms means the mapkit library's built-in timeout, which varies by release; the probe interval is unrelated.
Final answer (2-4 sentences): request_timeout_ms is not set in either the base config or the production override, so production runs on the timeout built into the mapkit client library, and the repo does not record what that is for the mapkit release you deploy. The interval setting in the config is the /healthz re-probe interval, not a request timeout. Check the mapkit release notes, or pin request_timeout_ms in config/env/production.toml as the docs recommend. Criteria: mentions mapkit and that the setting is not set; must not present the probe interval as the timeout.

## Why the answer is unique
The only interval number in the configs belongs to the probe block, and the docs state it is unrelated to request timeouts, so quoting it answers a different question. The request_timeout_ms key appears in neither file, so the effective value is the library default, which the workspace does not contain; any number would be invented.
''',
)

# ---------------------------------------------------------------- cfg-8020
write_case(
    "cfg-8020",
    desc="Fleet devices still point at a tile style retired in August; its config was removed from tilesets/, the style catalog records the retirement and migration, and the live successor's cache setting is the decoy",
    task_type="read_effective", family="fam-cfg-b10-styleretire-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 7200},
    axes=["DEC", "OBS"],
    files={
        "styles/catalog.csv": "style,status,since,note\nbasemap-1.9,retired,2026-02-28,superseded by basemap-2.0\nbasemap-2.0,retired,2026-08-31,traffic migrated to basemap-3.0\nbasemap-3.0,live,2026-08-31,current default\n",
        "tilesets/basemap-3.0.toml": "max_age = 7200\nmin_zoom = 0\nmax_zoom = 19\n",
        "README.md": "# Ostley Geospatial tile styles\n\nEach live style has one config under tilesets/, named after the style. Retired styles are removed from tilesets/; style state is tracked in styles/catalog.csv.\n",
    },
    turns=[{
        "prompt": "The field devices in the delivery fleet still point at basemap-2.0. What cache max-age does basemap-2.0 serve with?",
        "expect": {
            "output_contains": ["basemap-2.0"],
            "output_contains_any": ["retired", "no longer", "decommissioned", "removed", "migrated", "no config"],
            "output_excludes": ["7200"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: styles/catalog.csv ranks first (.csv sorts before .toml/.md);
# pin its header line.
assert files["styles/catalog.csv"].splitlines()[0] == "style,status,since,note"
rows = list(csv.DictReader(io.StringIO(files["styles/catalog.csv"])))
state = {r["style"]: r["status"] for r in rows}
assert state["basemap-2.0"] == "retired" and state["basemap-3.0"] == "live"
assert not any(p.startswith("tilesets/basemap-2.0") for p in files)
assert "max_age = 7200" in files["tilesets/basemap-3.0.toml"]
''' + en_words(["retired", "no longer", "decommissioned", "removed", "migrated", "no config"]),
    notes='''
## Traps
- TR-ABSENT: tilesets/ has no basemap-2.0 config; styles/catalog.csv marks basemap-2.0 retired since 2026-08-31, and the README says retired styles are removed from tilesets/.
- TR-DECOY: tilesets/basemap-3.0.toml max_age = 7200 is the live successor's value. Quoting 7200 as basemap-2.0's cache max-age is the decoy answer.

## Reference solution
1. List tilesets/: only basemap-3.0.toml, no basemap-2.0.
2. Read styles/catalog.csv: basemap-2.0 retired 2026-08-31, traffic migrated to basemap-3.0.
3. Read tilesets/basemap-3.0.toml, confirming it is the other, live style.
Final answer (2-4 sentences): basemap-2.0 was retired on 2026-08-31 and its config was removed from tilesets/, so there is no max-age to read for it. The style catalog notes its traffic migrated to basemap-3.0, which is the only style with a config now; that successor's settings are a different style's, not basemap-2.0's. Move the fleet devices to basemap-3.0, or ask the platform team to restore an archived config if the old value is really needed. Criteria: mentions basemap-2.0 and a retired/migrated phrase; must not present 7200 as its max-age.

## Why the answer is unique
The 7200 value belongs to basemap-3.0, a different style: the catalog's status column separates the two, and the README states retired styles lose their config, so nothing in the workspace can yield basemap-2.0's max-age. basemap-1.9 is retired as well and carries no config. The only defensible reply is that the style is retired and migrated, with the device migration as the next step.
''',
)

# ---------------------------------------------------------------- cfg-8021
write_case(
    "cfg-8021",
    desc="Migration plan asks the polygon buffer of tile schema v3; the template is unpublished (changelog says draft, review planned), the current v2 template and another schema's v3 template are the decoys",
    task_type="read_effective", family="fam-cfg-b10-tileschema-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": 48},
    axes=["DEC", "ERR"],
    files={
        "README.md": "# Ridgemoor Mapping map schemas\n\nPublished schema templates live in schemas/, one JSON file per schema and version. Draft versions are only logged in schemas/CHANGELOG.md.\n",
        "schemas/CHANGELOG.md": "# Schema changelog\n\n## tile schema\n- v3: draft. Polygon buffer rework led by the imagery team, review planned 2026-11-05, template not published yet.\n- v2: published 2025-12-08, current.\n\n## legend schema\n- v3: published 2026-06-30, current.\n",
        "schemas/tile-schema-v2.json": '{"name": "tile-schema", "version": 2, "clip": {"buffer_px": 24, "simplify_px": 1}, "label_spacing_px": 90}\n',
        "schemas/legend-schema-v3.json": '{"name": "legend-schema", "version": 3, "swatch_px": 48, "stroke_px": 2}\n',
    },
    turns=[{
        "prompt": "The map team needs the default polygon buffer from tile schema v3 for the migration plan. What buffer does v3 use?",
        "expect": {
            "output_contains": ["v3"],
            "output_contains_any": NEG_EN + ["draft", "not published", "hasn't been published", "not yet published", "unpublished"],
            "output_excludes": ["48"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: schemas/legend-schema-v3.json ranks first among the .json
# files (legend < tile); deleting its first line breaks the JSON parsed below.
legend = json.loads(files["schemas/legend-schema-v3.json"])
assert legend["name"] == "legend-schema" and legend["version"] == 3
v2 = json.loads(files["schemas/tile-schema-v2.json"])
assert v2["version"] == 2 and v2["clip"]["buffer_px"] == 24
assert not any(p.startswith("schemas/tile-schema-v3") for p in files)
log = files["schemas/CHANGELOG.md"]
assert "draft" in log and "template not published" in log
''' + en_words(NEG_EN + ["draft", "not published", "hasn't been published", "not yet published", "unpublished"]),
    notes='''
## Traps
- TR-ABSENT: schemas/ has no tile-schema-v3.json; schemas/CHANGELOG.md logs tile schema v3 as draft (polygon buffer rework, review planned 2026-11-05, template not published yet). The v2 template is the current published one, not v3's buffer.
- TR-NEARNAME: schemas/legend-schema-v3.json is also a "v3", with swatch_px 48. Reading the legend schema's 48 as tile schema v3's polygon buffer is the decoy answer.

## Reference solution
1. List schemas/: tile-schema-v2.json and legend-schema-v3.json, no tile-schema-v3.
2. Read schemas/CHANGELOG.md: tile schema v3 is draft, template not published; v2 is current.
3. Read schemas/legend-schema-v3.json, confirming it is a different schema.
Final answer (2-4 sentences): tile schema v3 is still a draft — the changelog logs the polygon buffer rework with review planned 2026-11-05 and the template not published yet, and schemas/ has no tile-schema-v3.json. The v3 file on disk is the legend schema, a different schema, so its numbers do not answer this; the current published tile template is v2, whose buffer is not the migration target. Ask the imagery team for the draft value or schedule the migration after the review. Criteria: mentions v3 and a draft/not-published phrase; must not present 48 as the buffer.

## Why the answer is unique
The legend schema's 48 fails on both name and meaning: it is swatch_px in legend-schema, not a polygon clip buffer, and the changelog keeps the two schemas in separate sections with different states. The v2 template is published but is explicitly the predecessor, so its buffer is not what the migration plan asked for. No tile-schema-v3 template exists in the workspace, so any buffer value would be invented.
''',
)

# ---------------------------------------------------------------- doc-8006
write_case(
    "doc-8006",
    desc="Weekend study plan asks the seat count of a third-floor rare-books reading room that is under renovation; only other reading rooms and the similarly named stacks room are documented, and the facilities plan says the reopening time is pending",
    task_type="policy_lookup", family="fam-doc-b10-readingroom-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "16 人"},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 望舒图书馆 阅览区开放\n\n每个阅览室在 阅览室/ 下放一份说明，文件名就是阅览室名；馆内库房不在此列。开放安排以 后勤/开放安排.md 为准。\n",
        "阅览室/二楼综合阅览室.md": "# 二楼综合阅览室\n\n座位数: 120\n开放时间: 08:00-21:30\n备注: 自习与普通阅览\n",
        "阅览室/四楼期刊阅览室.md": "# 四楼期刊阅览室\n\n座位数: 60\n开放时间: 09:00-20:00\n备注: 期刊只阅不外借\n",
        "阅览室/古籍书库.md": "# 古籍书库\n\n性质: 库房调阅，不是阅览室，无散座\n预约: 需提前一个工作日申请\n单日接待: 16 人\n备注: 只接待古籍查阅，不接受自习\n",
        "后勤/开放安排.md": "# 阅览区开放安排\n\n| 区域 | 状态 | 说明 |\n|---|---|---|\n| 二楼综合阅览室 | 正常开放 | |\n| 四楼期刊阅览室 | 正常开放 | |\n| 三楼古籍阅览室 | 装修改造中 | 开放时间待后勤处确定，预计 2026-11-10 重新开放 |\n",
    },
    turns=[{
        "prompt": "周六想去望舒图书馆三楼古籍阅览室自习，古籍阅览室的座位数是多少？",
        "expect": {
            "output_contains": ["古籍阅览室"],
            "output_contains_any": NEG_ZH + ["装修", "改造", "未开放", "没有开放", "还没开放", "尚未开放", "暂停开放"],
            "output_excludes": ["16 人", "16人", "接待 16"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 望舒图书馆 阅览区开放"
assert not any("三楼" in p for p in files)
stacks = files["阅览室/古籍书库.md"]
assert "库房" in stacks and "不接受自习" in stacks
plan = files["后勤/开放安排.md"]
row = [l for l in plan.splitlines() if "三楼古籍阅览室" in l]
assert row and "装修" in row[0]
''' + zh_words(NEG_ZH + ["装修", "改造", "未开放", "没有开放", "还没开放", "尚未开放", "暂停开放"]),
    notes='''
## Traps
- TR-ABSENT: 阅览室/ 下没有三楼古籍阅览室的说明；后勤/开放安排.md 写明它装修改造中、开放时间待后勤处确定，预计 2026-11-10 重新开放。
- TR-DECOY: 阅览室/古籍书库.md 名字里也有「古籍」，单日接待 16 人。把古籍书库的接待量当古籍阅览室的座位数，就是诱饵答案。

## Reference solution
1. 列出 阅览室/：只有二楼综合阅览室、四楼期刊阅览室、古籍书库三份说明。
2. 读 阅览室/古籍书库.md：它是库房调阅，不是阅览室，也不接受自习。
3. 读 后勤/开放安排.md：三楼古籍阅览室装修改造中，预计 11 月 10 日重开。
终答（2–4 句）：三楼古籍阅览室还在装修改造，没有座位数可查——阅览室/ 下没有它的说明文件，开放安排写它装修中、预计 11 月 10 日重新开放。名字相近的古籍书库是库房调阅，不是阅览室，也不接受自习。周六自习建议先去二楼综合阅览室，重开时间可以问后勤处。判据：包含「古籍阅览室」和一个「装修/未开放/没有」说法，不得把 16 人当座位数。

## Why the answer is unique
诱饵 16 人错在对象和性质都错：古籍书库的说明写明它是库房调阅、无散座、不接受自习，「单日接待」是调阅接待量而不是阅览座位数；二楼、四楼阅览室是别的楼层。开放安排证实三楼古籍阅览室尚未重开，工作区里没有它的座位说明，唯一站得住的回答是说明装修中、点出书库不是它、给出替代阅览室和问后勤处的下一步。
''',
)

# ---------------------------------------------------------------- doc-8007
write_case(
    "doc-8007",
    desc="System inspection asks who is on duty for the digital resources team in a given week; the shared rota has no such row, the team moved to the consortium's joint duty system, and a decommissioned old-name row with engineers is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-pagerota-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "池晚晴"},
    axes=["DEC", "OBS"],
    files={
        "值班/2026-Q4.md": "# 澜山图书馆 2026 年第四季度值班表（周一起算）\n\n| 组别 | 10 月 12 日当周 | 10 月 19 日当周 | 10 月 26 日当周 |\n|---|---|---|---|\n| 流通组 | 宋知微 | 阮清越 | 宋知微 |\n| 参考咨询组 | 裴松年 | 宋知微 | 裴松年 |\n| 数字资源组-旧 | 池晚晴 | 裴松年 | 池晚晴 |\n| 阅读推广组 | 阮清越 | 池晚晴 | 阮清越 |\n",
        "值班/README.md": "值班表列出本季度仍有馆内轮值的组；组别调整以 部门/目录.md 为准。\n",
        "部门/目录.md": "# 部门目录\n\n- 流通组：馆内轮值，见 值班/。\n- 参考咨询组：馆内轮值，见 值班/。\n- 数字资源组：2026-09-01 起改在市学会联合值班系统排班，不再进馆内值班表。\n- 数字资源组-旧：更名前的旧组名，2026-08-15 撤销；轮值暂留至季度值班表重新生成，不再响应馆内请求。\n- 阅读推广组：馆内轮值，见 值班/。\n",
    },
    turns=[{
        "prompt": "澜山图书馆的系统巡检安排在 10 月 12 日那周，数字资源组那周由谁值班？",
        "expect": {
            "output_contains": ["数字资源组"],
            "output_contains_any": NEG_ZH + ["联合值班", "不在", "没有排班"],
            "output_excludes": ["池晚晴", "裴松年"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 值班/2026-Q4.md sorts first; pin its first line.
assert files["值班/2026-Q4.md"].splitlines()[0].startswith("# 澜山图书馆 2026 年第四季度值班表")
rota = files["值班/2026-Q4.md"]
groups = [l.split("|")[1].strip() for l in rota.splitlines()
          if l.startswith("| ") and not l.startswith("| 组别")]
assert "数字资源组" not in groups and "数字资源组-旧" in groups
cat = [l for l in files["部门/目录.md"].splitlines() if l.startswith("- 数字资源组：")]
assert cat and "联合值班" in cat[0]
''' + zh_words(NEG_ZH + ["联合值班", "不在", "没有排班"]),
    notes='''
## Traps
- TR-ABSENT: 值班/2026-Q4.md 没有「数字资源组」这一行；部门/目录.md 写明数字资源组 2026-09-01 起改在市学会联合值班系统排班，不再进馆内值班表。
- TR-DECOY: 值班表里有「数字资源组-旧」，10 月 12 日当周是池晚晴。把旧组名的人当数字资源组值班人，就是诱饵答案。

## Reference solution
1. 读 值班/2026-Q4.md：组别里没有数字资源组，只有数字资源组-旧。
2. 读 部门/目录.md：数字资源组 9 月起在市学会联合值班系统排班；数字资源组-旧 8 月中撤销，不再响应馆内请求。
3. 核对值班表那一周的旧组名一栏，确认不能采用。
终答（2–4 句）：馆内值班表里没有数字资源组——它 9 月起改在市学会联合值班系统排班，不再进这张表；表里的数字资源组-旧是撤销的旧组名，那一栏的人不再响应馆内请求。巡检要联系值班的人，去联合值班系统查，或者直接问数字资源组组长。判据：包含「数字资源组」和一个「联合值班/没有/不在」说法；不得点旧组名一栏的人名。

## Why the answer is unique
诱饵的人名错在对象已撤销：目录写明数字资源组-旧是 8 月中撤销的旧组名，轮值只是暂留到值班表重新生成，不响应馆内请求，给巡检排它的人会找不到人。流通组、参考咨询组、阅读推广组是别的组。数字资源组本身已离开共享值班表，工作区里没有任何它的馆内轮值记录，唯一站得住的回答是说明不在表内并指向联合值班系统。
''',
)

# ---------------------------------------------------------------- doc-8008
write_case(
    "doc-8008",
    desc="Cataloguing question asks the call-number length limit in the fifth edition of a cataloguing rule that is still in draft; the published fourth edition and another rule's fifth edition are the reference and the decoy",
    task_type="policy_lookup", family="fam-doc-b10-catalogrules-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "32 字符"},
    axes=["DEC", "ERR"],
    files={
        "README.md": "# 栖云书院 编目制度库\n\n编目/ 只放已发布的版本；修订中的版本只在 编目/修订记录.md 登记，不放正文。\n",
        "编目/修订记录.md": "# 修订记录\n\n| 文档 | 版本 | 状态 | 说明 |\n|---|---|---|---|\n| 图书编目规则 | 第四版 | 已发布 2025-10-20 | 现行 |\n| 图书编目规则 | 第五版 | 起草中 | 编目部牵头，预计 2026-11-18 评审，正文未定稿 |\n| 古籍著录规则 | 第五版 | 已发布 2026-07-02 | 现行 |\n",
        "编目/图书编目规则-第四版.md": "# 图书编目规则（第四版）\n\n## 5 索书号\n5.1 索书号总长不超过 28 字符。\n5.2 分类号与种次号之间用 / 分隔。\n\n## 6 馆藏项\n6.1 每种馆藏单独建条目。\n",
        "编目/古籍著录规则-第五版.md": "# 古籍著录规则（第五版）\n\n## 3 索书号\n3.1 古籍索书号总长不超过 32 字符。\n3.2 卷次号单独一行。\n",
    },
    turns=[{
        "prompt": "栖云书院要按《图书编目规则》第五版著录新到图书，第五版里索书号的最大长度是多少？",
        "expect": {
            "output_contains": ["第五版"],
            "output_contains_any": ["起草", "未发布", "没有发布", "尚未发布", "还没发布", "未定稿", "没有定稿"],
            "output_excludes": ["32", "32 字符", "32字符"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 栖云书院 编目制度库"
assert not any("图书编目规则-第五版" in p for p in files)
log = files["编目/修订记录.md"]
rows = [l for l in log.splitlines() if l.startswith("| 图书编目规则")]
status = {r.split("|")[2].strip(): r.split("|")[3].strip() for r in rows}
assert status["第五版"] == "起草中" and status["第四版"].startswith("已发布")
assert "32 字符" in files["编目/古籍著录规则-第五版.md"]
''' + zh_words(["起草", "未发布", "没有发布", "尚未发布", "还没发布", "未定稿", "没有定稿"]),
    notes='''
## Traps
- TR-ABSENT: 编目/ 下没有《图书编目规则》第五版正文；编目/修订记录.md 登记第五版「起草中，编目部牵头，预计 2026-11-18 评审，正文未定稿」。
- TR-NEARNAME: 编目/古籍著录规则-第五版.md 也叫「第五版」，古籍索书号总长不超过 32 字符。把它当成《图书编目规则》第五版的长度，就是诱饵答案。

## Reference solution
1. 列出 编目/：《图书编目规则》只有第四版，第五版只有《古籍著录规则》。
2. 读 编目/修订记录.md：图书编目规则第五版起草中、未定稿。
3. 读 编目/图书编目规则-第四版.md，现行索书号上限可作参考口径。
终答（2–4 句）：《图书编目规则》第五版还在起草——修订记录写明编目部牵头、预计 11 月 18 日评审、正文未定稿，编目/ 下没有它的正文，给不出第五版的索书号上限；名字带第五版的是《古籍著录规则》，管古籍著录，口径不适用于普通图书。现行第四版规定索书号总长不超过 28 字符，新书上架是否先按第四版，需要和编目部确认。判据：包含「第五版」和一个「起草/未发布」说法，不得把 32 字符当答案。

## Why the answer is unique
诱饵 32 字符错在文档不同：它是《古籍著录规则》第五版里古籍索书号的上限，标题和章节都写明是古籍，不适用于普通图书的《图书编目规则》；修订记录里两份文档的第五版状态一行现行、一行起草中，并不相同。第四版的 28 字符是现行值而不是第五版的值，只能作参考。所以「第五版的上限」在工作区里不存在，唯一站得住的回答是说明起草中并给出与编目部确认的下一步。
''',
)

# ---------------------------------------------------------------- doc-8009
write_case(
    "doc-8009",
    desc="Asks when the revised visitor rules take effect; the revision ledger says they await the council's signature with the date to be announced, the draft file is marked not in force, and the current interim edition's effective date is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-visitorrules-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "2025-09-01"},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 汀兰图书馆 制度文本库\n\n制度/ 只放现行有效的文本；修订稿的状态在 制度/修订台账.md 登记。\n",
        "制度/修订台账.md": "# 修订台账\n\n| 文本 | 状态 | 说明 |\n|---|---|---|\n| 入馆须知（暂行版） | 现行 | 2025-09-01 起施行 |\n| 入馆须知（修订版） | 待馆务会签署 | 定稿已交签，生效日期签署后另行通知；签署前按暂行版执行 |\n",
        "制度/入馆须知-暂行版.md": "# 入馆须知（暂行版）\n\n（现行有效，2025-09-01 起施行）\n\n1. 占座保留 30 分钟。\n2. 闭馆前 15 分钟停止入馆。\n",
        "制度/入馆须知-修订稿.md": "# 入馆须知（修订稿）\n\n（修订稿，未生效，签署前不得作为执行依据）\n\n1. 占座保留 20 分钟。\n2. 闭馆前 15 分钟停止入馆。\n",
    },
    turns=[{
        "prompt": "汀兰图书馆的入馆须知修订版什么时候生效？",
        "expect": {
            "output_contains": ["修订"],
            "output_contains_any": NEG_ZH + ["待签", "未签", "还没签", "尚未签署", "没有签署", "未生效", "没有生效", "待定", "未定", "另行通知"],
            "output_excludes": ["修订版 2025-09-01", "修订版自 2025-09-01", "修订版于 2025-09-01", "修订版从 2025-09-01", "修订版将于 2025-09-01", "修订版生效日期是 2025-09-01", "修订版生效日期为 2025-09-01"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 汀兰图书馆 制度文本库"
ledger = files["制度/修订台账.md"]
row = [l for l in ledger.splitlines() if "修订版" in l]
assert row and "待馆务会签署" in row[0] and "另行通知" in row[0]
draft = files["制度/入馆须知-修订稿.md"]
assert "未生效" in draft
assert "2025-09-01" in files["制度/入馆须知-暂行版.md"]
''' + zh_words(NEG_ZH + ["待签", "未签", "还没签", "尚未签署", "没有签署", "未生效", "没有生效", "待定", "未定", "另行通知"]),
    notes='''
## Traps
- TR-ABSENT: 制度/修订台账.md 写明入馆须知（修订版）待馆务会签署、生效日期签署后另行通知；制度/入馆须知-修订稿.md 也标注未生效。生效日期在工作区里不存在。
- TR-DECOY: 台账里现行暂行版的施行日期是 2025-09-01。把暂行版的生效日期当成修订版的生效日期，就是诱饵答案。

## Reference solution
1. 读 制度/修订台账.md：修订版待馆务会签署，生效日期签署后另行通知；暂行版现行。
2. 读 制度/入馆须知-修订稿.md：文头标注未生效、不得作为执行依据。
3. 读 制度/入馆须知-暂行版.md，确认它才是现行文本。
终答（2–4 句）：修订版还没有生效：修订台账写它待馆务会签署，生效日期签署后另行通知，所以现在没有确定的生效日期；修订稿文头也标注未生效、不得作为执行依据。签署前馆里按暂行版执行，建议等签署通知，或者直接问馆务会的签披安排。判据：包含「修订」和一个「待签/未生效/另行通知」说法；不得把暂行版的施行日期当修订版的生效日期。

## Why the answer is unique
诱饵日期错在文本不同：台账两行分别登记暂行版与修订版，2025-09-01 只属于暂行版那一行，修订版一行的日期栏写的是签署后另行通知；修订稿文头也自我标注未生效。工作区里没有任何地方给出修订版的生效日期，唯一站得住的回答是说明待签署、日期未定并指向馆务会。
''',
)

# ---------------------------------------------------------------- doc-8010
write_case(
    "doc-8010",
    desc="Returns audit asks the daily intake cap of a book-return point closed at the end of August; the point's file was archived away, the catalog records the closure and merge, and the front desk's cap is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-bookreturn-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": 600},
    axes=["DEC", "OBS"],
    files={
        "README.md": "# 禾丰区图书馆 还书服务\n\n还书点在 服务点/ 下按点各一份说明；撤销的还书点不保留说明文件，只在 服务点/目录.md 登记。\n",
        "服务点/目录.md": "# 还书点目录\n\n| 还书点 | 状态 | 说明 |\n|---|---|---|\n| 总服务台 | 启用 | 08:30-18:00 |\n| 自助还书箱 | 启用 | 24 小时，只收普通图书 |\n| 老馆还书处 | 停用 | 2026-08-31 起撤销，还书业务并入总服务台，说明文件同日归档删除 |\n",
        "服务点/总服务台.md": "# 总服务台\n\n开放时间: 08:30-18:00\n每日接收上限: 600 册\n超限转翌日入库。\n",
        "服务点/自助还书箱.md": "# 自助还书箱\n\n开放时间: 全天\n备注: 只收普通图书，古籍与视听资料请走总服务台。\n",
    },
    turns=[{
        "prompt": "禾丰区图书馆的老馆还书处现在每天最多能收多少册还书？",
        "expect": {
            "output_contains": ["老馆还书处"],
            "output_contains_any": NEG_ZH + ["停用", "撤销", "并入", "合并"],
            "output_excludes": ["600"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 禾丰区图书馆 还书服务"
assert not any("老馆还书处.md" in p for p in files)
catalog = files["服务点/目录.md"]
row = [l for l in catalog.splitlines() if "老馆还书处" in l]
assert row and "停用" in row[0] and "总服务台" in row[0]
assert "600" in files["服务点/总服务台.md"]
''' + zh_words(NEG_ZH + ["停用", "撤销", "并入", "合并"]),
    notes='''
## Traps
- TR-ABSENT: 服务点/ 下没有老馆还书处的说明；服务点/目录.md 写明它 2026-08-31 起撤销、业务并入总服务台、说明文件同日归档删除。
- TR-DECOY: 服务点/总服务台.md 接了它的业务，每日接收上限 600 册。把总服务台的上限当老馆还书处的，就是诱饵答案。

## Reference solution
1. 列出 服务点/：只有总服务台和自助还书箱两份说明。
2. 读 服务点/目录.md：老馆还书处 8 月 31 日起撤销并入总服务台，文件同日归档删除。
3. 读 服务点/总服务台.md，确认 600 是接业务的另一个点。
终答（2–4 句）：老馆还书处 8 月 31 日起撤销，还书业务并入总服务台，说明文件也归档删除了，所以没有它自己的每日接收册数可查；现在在用的是总服务台和自助还书箱，要还书走这两处就行。如果要对账原老馆那部分业务，可以改看总服务台的接收记录。判据：包含「老馆还书处」和一个「停用/撤销/并入」说法，不得把 600 当它的上限。

## Why the answer is unique
诱饵 600 错在对象不对：它是总服务台的每日接收上限，目录写明老馆还书处已撤销并入、文件已删，撤销点的上限无从谈起；自助还书箱是另一个在用点。README 规定撤销的还书点不保留说明文件，工作区里不存在老馆还书处的任何参数，唯一站得住的回答是说明撤销并入并给出改看总服务台记录的下一步。
''',
)

# ---------------------------------------------------------------- doc-8011
write_case(
    "doc-8011",
    desc="Asks the 2026 interlibrary-loan fee schedule; the consortium has not issued one yet, the 2025 edition was voided and destroyed, and no fee figure exists anywhere in the workspace",
    task_type="policy_lookup", family="fam-doc-b10-loanguide-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"},
    axes=["DEC"],
    files={
        "README.md": "# 沚水图书馆 馆际互借\n\n馆际互借的收费标准由 市图工委 统一印发；我馆收到后在 制度/ 归档，未印发的年份不自行定价。\n",
        "制度/馆际互借说明.md": "# 馆际互借说明\n\n收费标准：按市图工委当年印发的标准执行。\n2025 年版已于 2026-01-01 作废，纸质件按档案规定销毁。\n2026 年版截至目前未收到，收到前馆际互借只收实际邮寄费，服务费免收。\n",
        "制度/申请流程.md": "# 申请流程\n\n1. 检索本馆与他馆馆藏，确认对方馆可借。\n2. 提交馆际互借申请单，注明书名与索取号。\n3. 到馆通知后凭读者证领取，阅后按期归还。\n",
    },
    turns=[{
        "prompt": "沚水图书馆馆际互借 2026 年的收费标准是什么？",
        "expect": {
            "output_contains": ["馆际互借"],
            "output_contains_any": NEG_ZH + ["未收到", "没有收到", "还没收到", "尚未收到", "作废", "未印发", "没有印发"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0] == "# 沚水图书馆 馆际互借"
note = files["制度/馆际互借说明.md"]
assert "未收到" in note and "作废" in note
assert "元" not in note
''' + zh_words(NEG_ZH + ["未收到", "没有收到", "还没收到", "尚未收到", "作废", "未印发", "没有印发"]),
    notes='''
## Traps
- TR-ABSENT: 制度/馆际互借说明.md 写明 2026 年版市图工委尚未收到，2025 年版已作废销毁；制度/申请流程.md 只讲流程。工作区里没有任何金额，没有相近诱饵，错误形态只有编造标准或裸答 UNKNOWN。

## Reference solution
1. 读 制度/馆际互借说明.md：2026 年版未收到，2025 年版已作废销毁，收到前只收实际邮寄费。
2. 读 制度/申请流程.md：确认它不含收费标准。
终答（2–4 句）：2026 年的收费标准现在查不到：说明文件写明市图工委的 2026 年版还没收到，2025 年版已作废销毁，我馆在收到新版前不自行定价，目前馆际互借只收实际邮寄费。要正式标准可以问市图工委，或者等我们收到新版后我再帮你查。判据：包含「馆际互借」和一个「未收到/作废/未印发」说法；不得编造金额。

## Why the answer is unique
工作区里唯一的收费相关文字是说明文件，它明确 2026 年版未收到、2025 年版作废销毁，且 README 规定未印发的年份不自行定价；申请流程里没有金额。所以任何收费标准都是编造，唯一站得住的回答是说明未收到与作废、给出问市图工委的下一步。
''',
)

# ---------------------------------------------------------------- doc-8012
write_case(
    "doc-8012",
    desc="Mapping style question asks the minimum label size in version 4 of the tile style guide, which is still in draft; the published v3 and the legend style guide's v4 are the reference and the decoy",
    task_type="policy_lookup", family="fam-doc-b10-styleguide-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "11.5"},
    axes=["DEC", "ERR"],
    files={
        "README.md": "# Saltmarsh Cartography style guides\n\nPublished guides live in docs/, one file per guide and version. Draft versions are only logged in docs/STYLE-LOG.md.\n",
        "docs/STYLE-LOG.md": "# Style guide log\n\n| Guide | Version | Status | Note |\n|---|---|---|---|\n| tile style guide | v3 | published 2026-04-14 | current |\n| tile style guide | v4 | draft | cartography team, review planned 2026-11-20, text not final |\n| legend style guide | v4 | published 2026-08-30 | current |\n",
        "docs/tile-style-guide-v3.md": "# Tile style guide (v3)\n\n## Labels\n- Minimum label size: 10 pt.\n- Collision distance: 2 px.\n",
        "docs/legend-style-guide-v4.md": "# Legend style guide (v4)\n\n## Swatches\n- Minimum label size: 11.5 pt.\n- Swatch size: 16 px.\n",
    },
    turns=[{
        "prompt": "What minimum label size does version 4 of the tile style guide specify?",
        "expect": {
            "output_contains": ["v4"],
            "output_contains_any": ["draft", "not published", "hasn't been published", "not yet published", "unpublished", "not final", "pending"],
            "output_excludes": ["11.5", "11.5 pt", "11.5pt"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: README.md sorts first among the .md files.
assert files["README.md"].splitlines()[0].startswith("# Saltmarsh Cartography")
assert not any("tile-style-guide-v4" in p for p in files)
log = files["docs/STYLE-LOG.md"]
rows = [l for l in log.splitlines() if l.startswith("| tile style guide")]
status = {r.split("|")[2].strip(): r.split("|")[3].strip() for r in rows}
assert status["v4"] == "draft" and status["v3"].startswith("published")
assert "11.5 pt" in files["docs/legend-style-guide-v4.md"]
''' + en_words(["draft", "not published", "hasn't been published", "not yet published",
                "unpublished", "not final", "pending"]),
    notes='''
## Traps
- TR-ABSENT: docs/ has no tile style guide v4 file; docs/STYLE-LOG.md lists tile style guide v4 as draft (cartography team, review planned 2026-11-20, text not final).
- TR-NEARNAME: docs/legend-style-guide-v4.md is also a "v4" with minimum label size 11.5 pt. Reading the legend guide's v4 value as the tile guide's is the decoy answer.

## Reference solution
1. List docs/: tile-style-guide-v3 and legend-style-guide-v4, no tile style guide v4.
2. Read docs/STYLE-LOG.md: tile style guide v4 is draft with text not final; v3 is the published current one.
3. Read docs/legend-style-guide-v4.md, confirming it is a different guide.
Final answer (2-4 sentences): version 4 of the tile style guide hasn't been published — STYLE-LOG.md lists it as draft with the text not final (cartography team, review planned 2026-11-20), and docs/ has no tile style guide v4 file. The v4 guide on disk is the legend style guide, a different guide, so its label size does not answer this. The current published tile guide is v3, which sets the minimum label size at 10 pt; whether to keep using that for the release is the cartography team's call. Criteria: mentions v4 and a draft/not-published phrase; must not present 11.5 pt as the tile guide's value.

## Why the answer is unique
The legend guide's 11.5 pt fails on both guide and scope: its title and section mark it as the legend style guide's swatch labels, while the log's rows keep the two guides apart with different statuses (published vs draft). The v3 tile guide's 10 pt is the current published value, not v4's, so it can only be offered as a reference. No tile style guide v4 text exists in the workspace, so any figure for it would be invented.
''',
)

# ---------------------------------------------------------------- doc-8013
write_case(
    "doc-8013",
    desc="Nightly job escalation asks who is on call for the tile-cache service in a given week; the shared rota has no tile-cache row, the catalogue says it moved to the Platform pager, and the decommissioned tile-cache-legacy row's engineers are the decoy",
    task_type="policy_lookup", family="fam-doc-b10-gisrota-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "Kwame Osei"},
    axes=["DEC", "OBS"],
    files={
        "oncall/2026-Q4.md": "# On-call rota, Q4 2026 (weeks start Monday)\n\n| Service | Oct 12 | Oct 19 | Oct 26 |\n|---|---|---|---|\n| streets-renderer | Petra Salminen | Diego Aramburu | Petra Salminen |\n| mosaic-scheduler | Anouk Verhoeven | Yusuf Demirel | Anouk Verhoeven |\n| tile-cache-legacy | Rosa Lindeman | Kwame Osei | Rosa Lindeman |\n| gazetteer-api | Diego Aramburu | Petra Salminen | Diego Aramburu |\n",
        "oncall/README.md": "The rota lists every service with a pager rotation this quarter. Swaps go through the #oncall-swaps channel.\n",
        "services/catalogue.md": "# Service catalogue - Tarnwater GIS\n\n- streets-renderer: owned by Carto Platform, pager rotation in oncall/.\n- mosaic-scheduler: owned by Carto Platform, pager rotation in oncall/.\n- tile-cache: owned by Platform Infrastructure. Moved to the Platform pager tool on 2026-09-01; not in the shared rota.\n- tile-cache-legacy: decommissioned 2026-08-15, rotation kept until the Q4 rota is regenerated.\n- gazetteer-api: owned by Search, pager rotation in oncall/.\n",
    },
    turns=[{
        "prompt": "The nightly mosaicking job runs against tile-cache during the week of October 19. Who is on call for tile-cache that week?",
        "expect": {
            "output_contains": ["tile-cache"],
            "output_contains_any": ["Platform Infrastructure", "not listed", "no entry", "isn't in", "not in the", "doesn't cover", "no row"],
            "output_excludes": ["Rosa Lindeman", "Kwame Osei"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: oncall/2026-Q4.md sorts first; pin its first line.
assert files["oncall/2026-Q4.md"].splitlines()[0].startswith("# On-call rota")
rota = files["oncall/2026-Q4.md"]
services = [l.split("|")[1].strip() for l in rota.splitlines()
            if l.startswith("| ") and not l.startswith("| Service")]
assert "tile-cache" not in services and "tile-cache-legacy" in services
cat = [l for l in files["services/catalogue.md"].splitlines() if l.startswith("- tile-cache:")]
owner = cat[0].split("owned by ", 1)[1].split(".")[0]
words = [owner] + ["not listed", "no entry", "isn't in", "not in the", "doesn't cover", "no row"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: oncall/2026-Q4.md has no tile-cache row; services/catalogue.md says tile-cache moved to the Platform Infrastructure pager tool on 2026-09-01 and is not in the shared rota.
- TR-DECOY: the rota does have a tile-cache-legacy row, and its Oct 19 entry is Kwame Osei. tile-cache-legacy was decommissioned on 2026-08-15, so naming Kwame Osei (or Rosa Lindeman from the same row) is the decoy answer.

## Reference solution
1. Read oncall/2026-Q4.md: no tile-cache row, only tile-cache-legacy.
2. Read services/catalogue.md: tile-cache is owned by Platform Infrastructure and paged from their own tool since 2026-09-01; tile-cache-legacy is decommissioned.
3. Cross-check the Oct 19 column of the legacy row, confirming it cannot be used.
Final answer (2-4 sentences): the shared Q4 rota has no tile-cache row, so it cannot say who is on call for tile-cache the week of Oct 19; the tile-cache-legacy row belongs to a service decommissioned in August, so those engineers are not on call for the live service. Per the service catalogue, tile-cache is owned by Platform Infrastructure and has been paged from their own tool since Sep 1 — check with Platform Infrastructure or their pager schedule. Criteria: mentions tile-cache and Platform Infrastructure (or a not-in-the-rota phrase); must not name the legacy row's engineers.

## Why the answer is unique
The legacy row's engineers are the decoy on object and status: the catalogue marks tile-cache-legacy decommissioned with its rotation only kept until the rota is regenerated, so its pager no longer answers for the live service. streets-renderer, mosaic-scheduler and gazetteer-api are other services. The catalogue states tile-cache left the shared rota, and nothing else in the workspace lists a tile-cache rotation, so the only correct reply is that the rota does not cover it and Platform Infrastructure does.
''',
)
