"""b10a (v1.4 §3.3) M3 part A: two-turn recap, turn 2 forbids tools.

40 cases: cfg-8032..cfg-8039, fs-8023..fs-8028, log-8034..log-8041,
tab-8042..tab-8051, doc-8023..doc-8030. Shape follows the b10 pilot
fs-8002 / cfg-8003 / log-8002 / tab-8003: turn 1 reads a file for one
field, turn 2 forbids tools and asks another field of the same file or a
one-step conversion of the same number, answered from what turn 1 already
read. Domains: auto-repair chains and appliance after-sales (zh), print
shops (en); proper names are new and unique across this file. verify.py
pins the first line of the file `bank verify`'s sabotage test deletes
first (ext order .csv < .tsv < .txt < .jsonl < .log < .json < .yaml
< .yml < .md, then path) and recomputes both turns' answers from
case["files"].

Run: cd bench/distill/tools/b10a && python3 m3a.py
"""
from common import revised

write_case = revised({'tab-8045': 'README 改为「数量一律按支计，火花塞整盒进货、每盒 4 支」：原文「火花塞按盒管理」使数量列可读成盒，三遍老师都按 12 盒 = 48 支作答，与题意（12 支、折合 3 盒）矛盾，题目缺陷。', 'tab-8050': '工时写法加「60.0 小时」：老师照 CSV 的一位小数写 60.0 小时被误判。', 'cfg-8034': 'kiosk 数加「Two —」等句首写法：老师答「Two — branches/high-street.yaml lists …」被误判。'})

NOCALL = {"tools": [], "require_active_no_call": True}

EXT_ORDER = (".csv", ".tsv", ".txt", ".jsonl", ".log", ".json", ".yaml", ".yml", ".md")


def sab_target(files):
    """(path, first non-empty line) of the file the sabotage test deletes from first."""
    def rank(p):
        base = p.rsplit("/", 1)[-1].lower()
        for i, ext in enumerate(EXT_ORDER):
            if base.endswith(ext):
                return i
        return len(EXT_ORDER)
    path = sorted(files, key=lambda p: (rank(p), p))[0]
    return path, next(l for l in files[path].split("\n") if l.strip())


def vhead(files):
    """Common verify prologue: pins the sabotage target's first line."""
    path, first = sab_target(files)
    return ('import json\n\ncase = json.load(open("case.json"))\nfiles = case["files"]\n'
            "# Sabotage target: %s sorts first in the corruption order; pin its first line.\n"
            "assert files[%r].splitlines()[0] == %r\n" % (path, path, first))


def echo(forms, zh):
    """verify.py tail echoing the acceptable surface forms (set-equal to the
    union of the turns' output_contains_any lists)."""
    words = list(dict.fromkeys(forms))
    if zh:
        return ('words = %r\n'
                'print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))\n' % (words,))
    return ('words = %r\n'
            'print(json.dumps({"expected_contains_any": words}))\n' % (words,))


def zh_date(iso):
    """Surface forms of a date the way a Chinese reply may write it."""
    _, m, d = (int(x) for x in iso.split("-"))
    return [iso, "%d 月 %d 日" % (m, d), "%d月%d日" % (m, d), "%d 月 %d 号" % (m, d), "%d月%d号" % (m, d)]


def money_forms(x):
    """Bare and thousands-grouped spellings of a 2-decimal amount."""
    bare = "%.2f" % x
    grouped = "{:,.2f}".format(x)
    return [bare] if bare == grouped else [bare, grouped]


def int_forms(n):
    """Bare and grouped spellings of an integer >= 1000."""
    grouped = "{:,}".format(n)
    return [str(n)] if grouped == str(n) else [str(n), grouped]

def zh_count(n, unit):
    """A small count with its unit, spaced and unspaced; a bare "19" would also
    match "2026-10-19" or "14" in a longer reply."""
    return ["%s %s" % (n, unit), "%s%s" % (n, unit)]


KIOSK_FORMS = ["2 self-service", "2 kiosk", "two self-service", "two kiosk", "Two self-service", "Two kiosk",
               "Two —", "Two.", "Two,", "Two:"]

# ---------------------------------------------------------------- cfg-8032
cfg32_files = {
    "门店/滨江店.yaml": "门店编码: HJ-BJ\n工位数: 6\n举升机: 4\n开门时间: 08:30\n闭店时间: 19:30\n值班技师: 沈国栋\n代步车: 3\n",
    "门店/城西店.yaml": "门店编码: HJ-CX\n工位数: 4\n举升机: 2\n开门时间: 08:30\n闭店时间: 18:00\n值班技师: 韩丽娟\n代步车: 2\n",
    "README.md": "# 恒捷养车 连锁门店参数\n\n各门店参数以 门店/ 下的 yaml 为准，文件名就是门店名。\n",
}
write_case(
    "cfg-8032",
    desc="Turn 1 reads a branch config for its closing time; turn 2 forbids tools and asks the same branch's opening hours per day",
    task_type="read_effective", family="fam-cfg-b10-chainbranch-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg32_files,
    turns=[
        {"prompt": "恒捷养车滨江店晚上几点闭店？",
         "expect": {"output_contains": ["19:30"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具了，就按刚才读到的滨江店参数说：滨江店一天营业多少个小时？",
         "expect": dict(NOCALL, output_contains_any=["11 小时", "11小时", "11 个小时", "11个小时"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg32_files) + '''
shop = files["门店/滨江店.yaml"]
close = [l for l in shop.splitlines() if l.startswith("闭店时间:")][0].split(":", 1)[1].strip()
open_ = [l for l in shop.splitlines() if l.startswith("开门时间:")][0].split(":", 1)[1].strip()
assert close == "19:30" and open_ == "08:30"
assert (19 - 8) * 60 + (30 - 30) == 660
print(json.dumps({"expected_string": close}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 2 轮考的是用户明确说不要调用工具时，直接用第 1 轮读到的门店参数作答：开门和闭店时间都在第 1 轮读过的那份 yaml 里。

## Reference solution
1. 第 1 轮列出 门店/ 并读 门店/滨江店.yaml：闭店时间 19:30。终答一句话：滨江店 19:30 闭店（门店参数里的闭店时间）。
第 2 轮不调用任何工具：08:30 开门、19:30 闭店，全天营业 11 个小时。终答一句话，例如「滨江店每天从 08:30 开到 19:30，一天营业 11 个小时。」判据：第 1 轮含 19:30；第 2 轮零调用并给出 11（任一写法）。

## Why the answer is unique
开门时间与闭店时间在滨江店配置里各只有一个值，19:30 − 08:30 = 11 小时没有第二种算法；第 2 轮需要的两个数都已在第 1 轮的读取结果里，用户又明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- cfg-8033
cfg33_files = {
    "网点/朝晖站.yaml": "站点编号: XW-CHZ\n覆盖城区: 拱墅区\n上门费: 30\n师傅人数: 8\n服务时间: 08:00-20:00\n站长: 罗启铭\n",
    "网点/祥符站.yaml": "站点编号: XW-XF\n覆盖城区: 西湖区\n上门费: 30\n师傅人数: 6\n服务时间: 09:00-18:00\n站长: 姜曼如\n",
    "README.md": "# 迅维家电服务 网点参数\n\n上门费按次收取，以 网点/ 下各站的 yaml 为准。\n",
}
write_case(
    "cfg-8033",
    desc="Turn 1 reads a service-station config for its call-out fee; turn 2 forbids tools and asks who runs the same station",
    task_type="read_effective", family="fam-cfg-b10-calloutfee-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg33_files,
    turns=[
        {"prompt": "迅维家电朝晖站的上门费收多少？",
         "expect": {"output_contains_any": ["30 元", "30元", "30"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "先别调工具，就用刚才读到的朝晖站信息回答：朝晖站的站长叫什么？",
         "expect": dict(NOCALL, output_contains_any=["罗启铭"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg33_files) + '''
post = files["网点/朝晖站.yaml"]
fee = [l for l in post.splitlines() if l.startswith("上门费:")][0].split(":", 1)[1].strip()
chief = [l for l in post.splitlines() if l.startswith("站长:")][0].split(":", 1)[1].strip()
assert fee == "30" and chief == "罗启铭"
assert files["网点/祥符站.yaml"].splitlines()[0] == "站点编号: XW-XF"
''' + echo(["30 元", "30元", "30", "罗启铭"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的朝晖站配置（站长罗启铭）作答，用户明确要求先别调工具；祥符站的站长姜曼如不是这一站的。

## Reference solution
1. 第 1 轮列出 网点/ 并读 网点/朝晖站.yaml：上门费 30 元/次。终答一句话给出 30 元与依据。
第 2 轮零调用：同一份配置里 站长: 罗启铭。终答一句话，例如「朝晖站的站长是罗启铭，就是刚才那份站点配置里登记的。」判据：第 1 轮含 30；第 2 轮零调用并含罗启铭。

## Why the answer is unique
站长在朝晖站配置里只有一个值；祥符站是另一个站点，站长不同。第 2 轮需要的信息已在第 1 轮读过的文件里，用户又明确禁止再调工具，所以直接答罗启铭是唯一正确做法。
''',
)

# ---------------------------------------------------------------- cfg-8034
cfg34_files = {
    "branches/high-street.yaml": "branch code: QT-HS\ncounter opens: 08:30\ncounter closes: 17:30\nself-service kiosks: 2\nmanager: Nell Farrow\n",
    "branches/mill-lane.yaml": "branch code: QT-ML\ncounter opens: 09:00\ncounter closes: 18:00\nself-service kiosks: 3\nmanager: Dexter Alonzo\n",
    "README.md": "# Quilltree Press branch settings\n\nEach branch has one config under branches/, named after the street it sits on.\n",
}
write_case(
    "cfg-8034",
    desc="Turn 1 reads a print-shop branch config for its counter closing time; turn 2 forbids tools and asks the same branch's kiosk count",
    task_type="read_effective", family="fam-cfg-b10-frontcounter-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg34_files,
    turns=[
        {"prompt": "What time does the counter at Quilltree Press's High Street branch close?",
         "expect": {"output_contains": ["17:30"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "Don't call any more tools — going by the High Street settings you already read: how many self-service kiosks does that branch run?",
         "expect": dict(NOCALL, output_contains_any=KIOSK_FORMS, max_output_chars=300)},
    ],
    verify='' + vhead(cfg34_files) + '''
high = files["branches/high-street.yaml"]
closes = [l for l in high.splitlines() if l.startswith("counter closes:")][0].split(":", 1)[1].strip()
kiosks = [l for l in high.splitlines() if l.startswith("self-service kiosks:")][0].split(":", 1)[1].strip()
assert closes == "17:30" and kiosks == "2"
assert "Dexter Alonzo" in files["branches/mill-lane.yaml"]
print(json.dumps({"expected_string": closes}))
''',
    notes='''
## Traps
- None. Turn 2 must be answered from the High Street config read in turn 1; the mill-lane branch's 3 kiosks belong to a different branch.

## Reference solution
1. Turn 1: list branches/ and read branches/high-street.yaml: the counter closes at 17:30. Final answer in one sentence: the High Street counter closes at 17:30.
Turn 2, no tool call: the same config sets self-service kiosks: 2. Final answer in one sentence: that branch runs 2 kiosks. Criteria: turn 1 contains 17:30; turn 2 is zero-call and says 2 kiosks (digit or word, next to "kiosk" or "self-service").

## Why the answer is unique
The kiosk count appears once in the High Street config; mill-lane's 3 is a different branch. Both facts were in the turn-1 read, and the user forbade further tool calls, so answering 2 directly is the only correct move.
''',
)

# ---------------------------------------------------------------- cfg-8035
cfg35_files = {
    "套餐/大保养.yaml": "套餐名: 大保养\n适用: 燃油车\n工时定额: 3.5\n含项: 小保养全部项目、空气滤芯、空调滤芯\n建议间隔: 40000 公里或 24 个月\n",
    "套餐/小保养.yaml": "套餐名: 小保养\n适用: 燃油车\n工时定额: 1.5\n机油规格: 5W-30\n含项: 机油、机滤、18 项检查\n建议间隔: 10000 公里或 12 个月\n",
    "README.md": "# 骏驰汽修 保养套餐\n\n套餐工时与含项以 套餐/ 下的 yaml 为准。\n",
}
write_case(
    "cfg-8035",
    desc="Turn 1 reads a service-package config for its labour-time allowance; turn 2 forbids tools and asks the same package's mileage interval",
    task_type="read_effective", family="fam-cfg-b10-maintplan-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg35_files,
    turns=[
        {"prompt": "骏驰汽修的小保养套餐工时定额是多少？",
         "expect": {"output_contains": ["1.5"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别动工具，就按刚才读到的套餐配置说：小保养建议多少公里做一次？",
         "expect": dict(NOCALL, output_contains_any=["10000 公里", "10000公里", "10000"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg35_files) + '''
plan = files["套餐/小保养.yaml"]
hours = float([l for l in plan.splitlines() if l.startswith("工时定额:")][0].split(":", 1)[1].strip())
interval = [l for l in plan.splitlines() if l.startswith("建议间隔:")][0].split(":", 1)[1].strip()
assert hours == 1.5
assert interval == "10000 公里或 12 个月"
assert "40000 公里或 24 个月" in files["套餐/大保养.yaml"]
print(json.dumps({"expected_number": hours}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的小保养配置（建议间隔 10000 公里或 12 个月）作答，不能再调工具；大保养的 40000 公里是另一个套餐。

## Reference solution
1. 第 1 轮列出 套餐/ 并读 套餐/小保养.yaml：工时定额 1.5。终答一句话给出 1.5 与依据。
第 2 轮零调用：同一份配置的 建议间隔 是 10000 公里或 12 个月。终答一句话，例如「小保养建议每 10000 公里或 12 个月做一次，按刚才读到的套餐配置。」判据：第 1 轮含 1.5；第 2 轮零调用并含 10000 公里。

## Why the answer is unique
小保养配置里工时定额与建议间隔各只有一个值；大保养是另一个套餐，间隔不同。第 2 轮需要的信息已在第 1 轮的读取结果里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- cfg-8036
cfg36_files = {
    "服务规范/挂机安装.yaml": "机型: 分体挂机\n预约响应: 24 小时内联系\n免费辅材: 管卡、膨胀螺栓\n高空作业费: 100\n保用期: 90 天\n",
    "服务规范/柜机安装.yaml": "机型: 分体柜机\n预约响应: 24 小时内联系\n免费辅材: 管卡、底座螺栓\n高空作业费: 150\n保用期: 90 天\n",
    "README.md": "# 蓝澄电器售后 安装服务规范\n\n分体挂机与柜机分别按 服务规范/ 下对应文件执行。\n",
}
write_case(
    "cfg-8036",
    desc="Turn 1 reads an AC-installation spec for the high-work fee of the floor-standing unit; turn 2 forbids tools and asks the same spec's warranty period",
    task_type="read_effective", family="fam-cfg-b10-installsop-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg36_files,
    turns=[
        {"prompt": "蓝澄售后给分体柜机做安装，高空作业费是多少？",
         "expect": {"output_contains_any": ["150", "150 元", "150元"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的柜机安装规范回答：安装完成后保用期是多少天？",
         "expect": dict(NOCALL, output_contains_any=["90 天", "90天", "90"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg36_files) + '''
floor = files["服务规范/柜机安装.yaml"]
fee = [l for l in floor.splitlines() if l.startswith("高空作业费:")][0].split(":", 1)[1].strip()
cover = [l for l in floor.splitlines() if l.startswith("保用期:")][0].split(":", 1)[1].strip()
assert fee == "150" and cover == "90 天"
assert "高空作业费: 100" in files["服务规范/挂机安装.yaml"]
''' + echo(["150", "150 元", "150元", "90 天", "90天", "90"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的柜机安装规范（保用期 90 天）作答；挂机规范的高空作业费 100 是另一份文件的值。

## Reference solution
1. 第 1 轮列出 服务规范/ 并读 服务规范/柜机安装.yaml：高空作业费 150 元。终答一句话给出 150 元与依据。
第 2 轮零调用：同一份规范的 保用期: 90 天。终答一句话，例如「柜机安装完成后保用 90 天，写在你刚才让我看的安装规范里。」判据：第 1 轮含 150；第 2 轮零调用并含 90 天。

## Why the answer is unique
柜机规范里高空作业费与保用期各只有一个值；挂机规范虽然保用期也是 90 天，但高空作业费是 100，两份文件不混淆。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- cfg-8037
cfg37_files = {
    "pressroom/digital-row.yaml": "unit: digital-row\nrated speed: 3200 sheets/h\nshift ends: 18:00\noperator: Hana Yoshimoto\n",
    "pressroom/offset-line.yaml": "unit: offset-line\nplates per day: 40\nwash-up: 25 min\nmake-ready: 45 min\nshift ends: 16:30\noperator: Oskar Brandt\n",
    "README.md": "# Fogbound Printworks pressroom settings\n\nOne config per press unit under pressroom/.\n",
}
write_case(
    "cfg-8037",
    desc="Turn 1 reads a press-unit config for its shift end; turn 2 forbids tools and asks the make-ready and wash-up gap for the same unit",
    task_type="read_effective", family="fam-cfg-b10-pressroom-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg37_files,
    turns=[
        {"prompt": "When does the shift on Fogbound's offset-line press end?",
         "expect": {"output_contains": ["16:30"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "No more tool calls — from the offset-line settings you already read: how much longer is its make-ready than its wash-up?",
         "expect": dict(NOCALL, output_contains_any=["20 min", "20 minutes", "20min", "20"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg37_files) + '''
unit = files["pressroom/offset-line.yaml"]
ends = [l for l in unit.splitlines() if l.startswith("shift ends:")][0].split(":", 1)[1].strip()
wash = int([l for l in unit.splitlines() if l.startswith("wash-up:")][0].split(":", 1)[1].strip().split()[0])
ready = int([l for l in unit.splitlines() if l.startswith("make-ready:")][0].split(":", 1)[1].strip().split()[0])
assert ends == "16:30" and ready - wash == 20 and wash == 25 and ready == 45
assert "operator: Hana Yoshimoto" in files["pressroom/digital-row.yaml"]
print(json.dumps({"expected_string": ends}))
''',
    notes='''
## Traps
- None. Turn 2 works from the offset-line config read in turn 1: make-ready 45 min minus wash-up 25 min is 20 min. The digital-row unit has no such fields.

## Reference solution
1. Turn 1: read pressroom/offset-line.yaml: shift ends at 16:30. Final answer in one sentence: the offset-line shift ends at 16:30.
Turn 2, no tool call: the same config lists wash-up 25 min and make-ready 45 min, so make-ready runs 20 minutes longer. Final answer in one sentence. Criteria: turn 1 contains 16:30; turn 2 is zero-call and says 20 (with or without the unit).

## Why the answer is unique
The two durations appear once each in the offset-line config, and their difference is a single subtraction; the digital-row config carries neither field. Both numbers were in the turn-1 read, and the user forbade more tool calls.
''',
)

# ---------------------------------------------------------------- cfg-8038
cfg38_files = {
    "钣喷/1号喷漆房.yaml": "编号: QL-P01\n升温上限: 60\n烘烤温度: 60\n烘烤时长: 30\n过滤棉更换: 每 100 台\n",
    "钣喷/2号喷漆房.yaml": "编号: QL-P02\n升温上限: 55\n烘烤温度: 60\n烘烤时长: 40\n过滤棉更换: 每 120 台\n",
    "README.md": "# 千里汽修 钣喷参数\n\n喷漆房参数以 钣喷/ 下的 yaml 为准。\n",
}
write_case(
    "cfg-8038",
    desc="Turn 1 reads a paint-booth config for its bake duration; turn 2 forbids tools and asks how many cars the same booth's filter lasts for",
    task_type="read_effective", family="fam-cfg-b10-paintbooth-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=cfg38_files,
    turns=[
        {"prompt": "千里汽修 钣喷/2号喷漆房.yaml 里写的烘烤时长是多少分钟？",
         "expect": {"output_contains_any": ["40 分钟", "40分钟", "40 分", "40分", "40"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具，就用刚才读到的 2 号喷漆房参数说：它的过滤棉累计喷多少台车就要换？",
         "expect": dict(NOCALL, output_contains_any=["120 台", "120台", "每 120 台", "120"], max_output_chars=300)},
    ],
    verify='' + vhead(cfg38_files) + '''
two = files["钣喷/2号喷漆房.yaml"]
bake = [l for l in two.splitlines() if l.startswith("烘烤时长:")][0].split(":", 1)[1].strip()
filt = [l for l in two.splitlines() if l.startswith("过滤棉更换:")][0].split(":", 1)[1].strip()
assert bake == "40" and filt == "每 120 台"
assert "过滤棉更换: 每 100 台" in files["钣喷/1号喷漆房.yaml"]
''' + echo(["40 分钟", "40分钟", "40 分", "40分", "40", "120 台", "120台", "每 120 台", "120"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读过的 钣喷/2号喷漆房.yaml 作答：过滤棉更换是每 120 台；1 号房的「每 100 台」是另一间房，不能混。

## Reference solution
1. 第 1 轮读 钣喷/2号喷漆房.yaml：烘烤时长 40 分钟。终答一句话给出 40 分钟与依据。
第 2 轮零调用：同一份参数的 过滤棉更换: 每 120 台。终答一句话，例如「2 号房的过滤棉每喷 120 台车换一次，参数里写的是每 120 台。」判据：第 1 轮含 40；第 2 轮零调用并含 120。

## Why the answer is unique
2 号喷漆房参数里烘烤时长与过滤棉更换各只有一个值；1 号房是另一间房，过滤棉口径不同。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- cfg-8039
cfg39_files = {
    "制度/延保订购.yaml": "品类: 冰箱\n延保年限: 2 年\n生效: 整机包修到期次日\n",
    "制度/以旧换新.yaml": "品类: 冰箱\n换新补贴上限: 800\n旧机回收: 上门拖走\n测评报告: 需要\n有效期: 至 2026-12-31\n",
    "README.md": "# 洁邻家电服务 以旧换新与延保\n\n制度/ 下按业务分别存放规则文件。\n",
}
write_case(
    "cfg-8039",
    desc="Turn 1 reads the trade-in rules for the fridge subsidy cap; turn 2 forbids tools and asks when the same programme ends",
    task_type="read_effective", family="fam-cfg-b10-tradeinsop-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=cfg39_files,
    turns=[
        {"prompt": "洁邻家电冰箱以旧换新的补贴上限是多少？",
         "expect": {"output_contains_any": ["800", "800 元", "800元"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "先别动工具，就按刚才读到的以旧换新规则说：这个活动到哪天截止？",
         "expect": dict(NOCALL, output_contains_any=zh_date("2026-12-31"), max_output_chars=300)},
    ],
    verify='' + vhead(cfg39_files) + '''
trade = files["制度/以旧换新.yaml"]
cap = [l for l in trade.splitlines() if l.startswith("换新补贴上限:")][0].split(":", 1)[1].strip()
end = [l for l in trade.splitlines() if l.startswith("有效期:")][0].split(":", 1)[1].strip()
assert cap == "800" and end == "至 2026-12-31"
assert "延保年限: 2 年" in files["制度/延保订购.yaml"]
''' + echo(["800", "800 元", "800元"] + zh_date("2026-12-31"), zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的以旧换新规则作答：有效期至 2026-12-31；延保订购是另一份文件，没有截止日期。

## Reference solution
1. 第 1 轮列出 制度/ 并读 制度/以旧换新.yaml：换新补贴上限 800 元。终答一句话给出 800 元与依据。
第 2 轮零调用：同一份规则写明 有效期至 2026-12-31。终答一句话，例如「以旧换新活动到 2026 年 12 月 31 日截止，规则文件里写的。」判据：第 1 轮含 800；第 2 轮零调用并给出 2026-12-31（任一写法）。

## Why the answer is unique
以旧换新规则里补贴上限与有效期各只有一个值；延保订购文件管的是另一项业务。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- fs-8023
fs23_files = {
    "配件/库存台账.md": "# 配件库存台账（2026-09-30 盘点）\n\n| 配件 | 编号 | 在库 | 货位 | 到货批次 |\n|---|---|---|---|---|\n| 机油滤清器 | PJ-3301 | 42 | A-03 | 2026-09-12 |\n| 前刹车片 | PJ-3287 | 18 | B-11 | 2026-09-05 |\n| 空调滤芯 | PJ-3140 | 63 | A-07 | 2026-08-28 |\n| 火花塞 | PJ-3092 | 120 | C-02 | 2026-09-18 |\n",
    "配件/缺货登记.md": "# 缺货登记\n\n- PJ-3301 机油滤清器：9 月 28 日缺货 6 只，已补齐。\n",
    "README.md": "# 顺达汽修 配件资料\n\n库存以 配件/库存台账.md 为准。\n",
}
write_case(
    "fs-8023",
    desc="Turn 1 reads the parts ledger for a brake-pad set's bin location; turn 2 forbids tools and asks the same row's on-hand quantity",
    task_type="find_file", family="fam-fs-b10-partledger-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=fs23_files,
    turns=[
        {"prompt": "帮我看一下 配件/库存台账.md 里前刹车片放在哪个货位？",
         "expect": {"output_contains": ["B-11"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具了，就用刚才读到的台账回答：前刹车片在库多少片？",
         "expect": dict(NOCALL, output_contains_any=["18 片", "18片", "18 副", "18副", "18"], max_output_chars=300)},
    ],
    verify='' + vhead(fs23_files) + '''
row = [l for l in files["配件/库存台账.md"].splitlines() if "前刹车片" in l][0].split("|")
cell, stock = row[4].strip(), row[3].strip()
assert cell == "B-11" and stock == "18"
assert "缺货 6 只" in files["配件/缺货登记.md"]
print(json.dumps({"expected_string": cell}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的台账行作答：前刹车片 PJ-3287 在库 18 片；缺货登记里补的是机油滤清器，与它无关。

## Reference solution
1. 第 1 轮读 配件/库存台账.md：前刹车片 PJ-3287 的货位是 B-11。终答一句话：前刹车片放在 B-11 货位（台账编号 PJ-3287）。
第 2 轮零调用：同一行的在库数是 18。终答一句话，例如「台账里前刹车片在库 18 片，就放在 B-11 那格。」判据：第 1 轮含 B-11；第 2 轮零调用并给出 18。

## Why the answer is unique
台账里前刹车片只有一行，货位与在库数都在这一行；第 2 轮需要的信息已在第 1 轮的读取结果里，用户又明确禁止再调工具，所以直接答 18 片是唯一正确做法。
''',
)

# ---------------------------------------------------------------- fs-8024
fs24_files = {
    "工单/2026-09/上门工单-0926.md": "# 上门工单 WX-09261\n\n机型: 沄溪滚筒洗衣机\n故障: 排水缓慢\n上门日期: 2026-09-26\n师傅: 尹晓岚\n处理: 清理排水泵过滤网\n用时: 50 分钟\n",
    "工单/2026-09/上门工单-0922.md": "# 上门工单 WX-09224\n\n机型: 澈泉燃气热水器\n故障: 打不着火\n上门日期: 2026-09-22\n师傅: 佟国斌\n处理: 更换点火器\n用时: 70 分钟\n",
    "README.md": "# 暖山家电服务 上门工单归档\n\n按月归档在 工单/ 下，文件名含工单日期。\n",
}
write_case(
    "fs-8024",
    desc="Turn 1 locates the Sep 22 service ticket and reads the machine type; turn 2 forbids tools and asks what fix was applied on that ticket",
    task_type="find_file", family="fam-fs-b10-ticketarchive-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=fs24_files,
    turns=[
        {"prompt": "暖山家电 9 月 22 日上门的那一单，修的是什么机型？",
         "expect": {"output_contains_any": ["澈泉燃气热水器", "燃气热水器", "热水器"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按你刚才读到的 9 月 22 日那单说：师傅是怎么处理的？",
         "expect": dict(NOCALL, output_contains_any=["更换点火器", "换了点火器"], max_output_chars=300)},
    ],
    verify='' + vhead(fs24_files) + '''
t = files["工单/2026-09/上门工单-0922.md"]
assert "机型: 澈泉燃气热水器" in t and "处理: 更换点火器" in t and "佟国斌" in t
other = files["工单/2026-09/上门工单-0926.md"]
assert "沄溪滚筒洗衣机" in other and "2026-09-26" in other
''' + echo(["澈泉燃气热水器", "燃气热水器", "热水器", "更换点火器", "换了点火器"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的 9 月 22 日工单作答：处理措施是更换点火器；9 月 26 日那单是另一台洗衣机，不能混。

## Reference solution
1. 第 1 轮在 工单/2026-09/ 下找到 上门工单-0922.md 并读：机型是澈泉燃气热水器（故障：打不着火）。终答一句话给出机型与依据。
第 2 轮零调用：同一张工单写明 处理: 更换点火器。终答一句话，例如「那单是燃气热水器打不着火，师傅更换了点火器。」判据：第 1 轮含热水器（或澈泉）；第 2 轮零调用并含更换点火器。

## Why the answer is unique
归档里 9 月 22 日只有一张工单，机型与处理各只有一个值；9 月 26 日是另一台机器的另一单。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- fs-8025
fs25_files = {
    "stock/paper-cabinet.md": "# Paper cabinet - counted Sep 30\n\n| Stock | Code | Sheets on hand | Shelf |\n|---|---|---|---|\n| Uncoated 100 gsm | PC-118 | 4500 | B2 |\n| Silk-coated 150 gsm | PC-204 | 2800 | B4 |\n| Carbonless pink | PC-330 | 900 | C1 |\n| Board 300 gsm | PC-377 | 640 | D3 |\n",
    "stock/order-book.md": "# Standing orders\n\n- PC-330 carbonless: reordered every second Monday.\n",
    "README.md": "Ledgerside Print Co. stock notes. The paper cabinet listing is authoritative.\n",
}
write_case(
    "fs-8025",
    desc="Turn 1 reads the paper cabinet for the shelf holding the carbonless stock; turn 2 forbids tools and asks that stock's sheet count",
    task_type="find_file", family="fam-fs-b10-papercab-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=fs25_files,
    turns=[
        {"prompt": "Which shelf in stock/paper-cabinet.md holds the carbonless pink stock?",
         "expect": {"output_contains": ["C1"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "Don't reach for any tools — from the cabinet listing you already have: how many sheets of that carbonless pink are on hand?",
         "expect": dict(NOCALL, output_contains_any=["900", "nine hundred", "Nine hundred"], max_output_chars=300)},
    ],
    verify='' + vhead(fs25_files) + '''
row = [l for l in files["stock/paper-cabinet.md"].splitlines() if "Carbonless pink" in l][0].split("|")
shelf, sheets = row[4].strip(), row[3].strip()
assert shelf == "C1" and sheets == "900"
assert "every second Monday" in files["stock/order-book.md"]
print(json.dumps({"expected_string": shelf}))
''',
    notes='''
## Traps
- None. Turn 2 must be answered from the cabinet row read in turn 1: carbonless pink, 900 sheets on shelf C1. The order book covers the same code but carries no counts.

## Reference solution
1. Turn 1: read stock/paper-cabinet.md: carbonless pink sits on shelf C1. Final answer in one sentence: the carbonless pink stock is on shelf C1.
Turn 2, no tool call: the same row lists 900 sheets on hand. Final answer in one sentence. Criteria: turn 1 contains C1; turn 2 is zero-call and says 900 (digit or spelled out).

## Why the answer is unique
The cabinet has one row per stock, so shelf and sheet count for carbonless pink are unambiguous; the other shelves hold different stocks. Both facts were in the turn-1 read, and the user forbade further tool calls.
''',
)

# ---------------------------------------------------------------- fs-8026
fs26_files = {
    "质检/竣工检验单-20260928.md": "# 竣工检验单 GJ-0928\n\n车牌: 浙A·7K3F9\n项目: 更换前轮两支减振器\n路试: 绕场 3 圈，无异响\n检验员: 盛可欣\n交车时间: 2026-09-28 17:40\n",
    "质检/竣工检验单-20260925.md": "# 竣工检验单 GJ-0925\n\n车牌: 浙A·F2D81\n项目: 四轮定位\n路试: 绕场 2 圈，合格\n检验员: 庄启帆\n交车时间: 2026-09-25 16:05\n",
    "README.md": "# 立信汽修 质检归档\n\n竣工检验单按日期归档在 质检/ 下。\n",
}
write_case(
    "fs-8026",
    desc="Turn 1 locates the Sep 28 road-test sheet and reads its verdict; turn 2 forbids tools and asks the same sheet's hand-over time",
    task_type="find_file", family="fam-fs-b10-roadtest-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=fs26_files,
    turns=[
        {"prompt": "立信汽修 9 月 28 日那台车的竣工检验单，路试结果写的是什么？",
         "expect": {"output_contains_any": ["无异响", "绕场 3 圈", "3 圈"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别翻文件了，就按刚才那份检验单回答：这台车是几点交车的？",
         "expect": dict(NOCALL, output_contains=["17:40"], max_output_chars=300)},
    ],
    verify='' + vhead(fs26_files) + '''
t = files["质检/竣工检验单-20260928.md"]
assert "路试: 绕场 3 圈，无异响" in t and "交车时间: 2026-09-28 17:40" in t and "盛可欣" in t
other = files["质检/竣工检验单-20260925.md"]
assert "绕场 2 圈，合格" in other and "16:05" in other
print(json.dumps({"expected_string": "17:40"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的 9 月 28 日检验单作答：交车时间 17:40；9 月 25 日那单的 16:05 是另一台车。

## Reference solution
1. 第 1 轮在 质检/ 下找到 竣工检验单-20260928.md 并读：路试绕场 3 圈、无异响。终答一句话给出路试结果与依据。
第 2 轮零调用：同一张单写明 交车时间 2026-09-28 17:40。终答一句话，例如「17:40 交的车，检验单上写的就是这个时间。」判据：第 1 轮含无异响（或 3 圈）；第 2 轮零调用并含 17:40。

## Why the answer is unique
9 月 28 日的检验单只有一张，路试与交车时间各只有一个值；9 月 25 日是另一台车的单。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再翻文件。
''',
)

# ---------------------------------------------------------------- fs-8027
fs27_files = {
    "回执/回执-20261005.md": "# 上门回执 VH-1005\n\n地址: 春波小区 6 栋 2 单元\n品类: 分体挂机（澄风）\n项目: 加氟与清洗滤网\n师傅: 白若云\n收费: 上门费 40、辅材费 45\n",
    "回执/回执-20261003.md": "# 上门回执 VH-1003\n\n地址: 石桥路 88 号\n品类: 焙语嵌入式烤箱\n项目: 更换发热管\n师傅: 冀成蹊\n收费: 上门费 40、配件费 260\n",
    "README.md": "# 康邻家电服务 上门回执\n\n回执按日期存于 回执/。\n",
}
write_case(
    "fs-8027",
    desc="Turn 1 locates the Oct 5 visit receipt and reads the technician's name; turn 2 forbids tools and asks the same receipt's appliance category",
    task_type="find_file", family="fam-fs-b10-visitnote-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=fs27_files,
    turns=[
        {"prompt": "康邻家电 10 月 5 日那单上门回执，是哪位师傅去的？",
         "expect": {"output_contains": ["白若云"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的回执说：那单修的是什么电器？",
         "expect": dict(NOCALL, output_contains_any=["澄风", "分体挂机", "挂机"], max_output_chars=300)},
    ],
    verify='' + vhead(fs27_files) + '''
t = files["回执/回执-20261005.md"]
assert "师傅: 白若云" in t and "品类: 分体挂机（澄风）" in t
other = files["回执/回执-20261003.md"]
assert "焙语嵌入式烤箱" in other and "冀成蹊" in other
print(json.dumps({"expected_string": "白若云"}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的 10 月 5 日回执作答：品类是分体挂机（澄风）；10 月 3 日那单是烤箱，师傅也不同。

## Reference solution
1. 第 1 轮在 回执/ 下找到 回执-20261005.md 并读：师傅白若云。终答一句话给出师傅姓名与依据。
第 2 轮零调用：同一张回执写明 品类: 分体挂机（澄风）。终答一句话，例如「修的是澄风的分体挂机，回执上登记的就是它。」判据：第 1 轮含白若云；第 2 轮零调用并含挂机（或澄风）。

## Why the answer is unique
10 月 5 日的回执只有一张，师傅与品类各只有一个值；10 月 3 日是另一单。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- fs-8028
fs28_files = {
    "服务台/钥匙寄存.md": "# 客户钥匙寄存\n\n| 车牌 | 挂钥匙牌 | 车型 | 寄存日期 | 经手 |\n|---|---|---|---|---|\n| 浙A·9Q2L6 | KS-31 | 银色 MPV | 2026-10-08 | 蔺春梅 |\n| 浙A·5H8T2 | KS-32 | 白色轿车 | 2026-10-08 | 齐若楠 |\n| 浙A·3D6V1 | KS-33 | 灰色 SUV | 2026-10-09 | 蔺春梅 |\n",
    "服务台/代步车登记.md": "# 代步车借用\n\n- 10 月 8 日：浙A·5H8T2 的客户借代步车 1 天。\n",
    "README.md": "# 恒通汽修 服务台\n\n钥匙寄存以 服务台/钥匙寄存.md 为准。\n",
}
write_case(
    "fs-8028",
    desc="Turn 1 reads the key-shelf register for the grey SUV's key tag; turn 2 forbids tools and asks when that car was checked in",
    task_type="find_file", family="fam-fs-b10-keyshelf-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=fs28_files,
    turns=[
        {"prompt": "看一下 服务台/钥匙寄存.md：寄存的灰色 SUV 那把钥匙挂的是什么牌号？",
         "expect": {"output_contains": ["KS-33"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具，就用刚才读到的寄存表回答：KS-33 那台车是哪天寄存的？",
         "expect": dict(NOCALL, output_contains_any=zh_date("2026-10-09"), max_output_chars=300)},
    ],
    verify='' + vhead(fs28_files) + '''
row = [l for l in files["服务台/钥匙寄存.md"].splitlines() if "KS-33" in l].pop().split("|")
model, day = row[3].strip(), row[4].strip()
assert model == "灰色 SUV" and day == "2026-10-09"
assert "KS-31" in files["服务台/钥匙寄存.md"] and "借代步车 1 天" in files["服务台/代步车登记.md"]
print(json.dumps({"expected_string": "KS-33"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的寄存表行作答：KS-33 那行写明寄存日期 2026-10-09；KS-31、KS-32 是另外两台车。

## Reference solution
1. 第 1 轮读 服务台/钥匙寄存.md：灰色 SUV 浙A·3D6V1 挂 KS-33。终答一句话给出牌号与依据。
第 2 轮零调用：同一行的寄存日期是 2026-10-09。终答一句话，例如「KS-33 那台是 10 月 9 日寄存的，就在寄存表那一行。」判据：第 1 轮含 KS-33；第 2 轮零调用并给出 2026-10-09（任一写法）。

## Why the answer is unique
寄存表里 KS-33 只出现一次，车型与寄存日期都在这一行；第 2 轮需要的信息已在第 1 轮的读取结果里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8034
log34 = """2026-10-09 08:12 浙A·D59K2 进入 3 号工位，项目：更换右前减振器
2026-10-09 09:40 浙A·D59K2 3 号工位完工出厂
2026-10-09 10:05 浙A·B77M3 进入 1 号工位，项目：小保养
2026-10-09 11:02 浙A·B77M3 1 号工位完工出厂
2026-10-09 13:26 浙A·E20P8 进入 2 号工位，项目：空调检漏
2026-10-09 14:18 浙A·E20P8 2 号工位补氮气后复检合格
2026-10-09 15:03 浙A·E20P8 2 号工位完工出厂
"""
log34_files = {
    "作业日志/工位日志-20261008.log": "2026-10-08 08:31 浙A·K11R4 进入 2 号工位，项目：更换电瓶\n2026-10-08 09:55 浙A·K11R4 2 号工位完工出厂\n",
    "作业日志/工位日志-20261009.log": log34,
    "README.md": "腾跃汽修 工位作业日志，时间均为北京时间，一行一件事。\n",
}
write_case(
    "log-8034",
    desc="Turn 1 reads the bay log for when one car entered a bay; turn 2 forbids tools and asks when the same car left",
    task_type="time_window", family="fam-log-b10-baylog-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log34_files,
    turns=[
        {"prompt": "腾跃汽修 作业日志/工位日志-20261009.log 里，浙A·B77M3 那台车几点进的工位？",
         "expect": {"output_contains": ["10:05"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的日志说：那台车什么时候完工出厂的？",
         "expect": dict(NOCALL, output_contains=["11:02"], max_output_chars=300)},
    ],
    verify='' + vhead(log34_files) + '''
log = files["作业日志/工位日志-20261009.log"]
enter = [l for l in log.splitlines() if "浙A·B77M3" in l and "进入" in l][0]
leave = [l for l in log.splitlines() if "浙A·B77M3" in l and "完工出厂" in l][0]
assert enter.startswith("2026-10-09 10:05") and leave.startswith("2026-10-09 11:02")
assert len([l for l in log.splitlines() if "浙A·B77M3" in l]) == 2
print(json.dumps({"expected_string": "11:02"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的工位日志作答：浙A·B77M3 完工出厂是 11:02；09:40 完工的是另一台车。

## Reference solution
1. 第 1 轮读 作业日志/工位日志-20261009.log：浙A·B77M3 于 10:05 进入 1 号工位。终答一句话给出进位时间与依据。
第 2 轮零调用：同一份日志里它 11:02 完工出厂。终答一句话，例如「11:02 完工出厂，日志里它的两条记录就是进和出。」判据：第 1 轮含 10:05；第 2 轮零调用并含 11:02。

## Why the answer is unique
这份日志里浙A·B77M3 只有进、出两条记录，时间各只有一个值；09:40 完工的是浙A·D59K2。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8035
log35 = """2026-10-07 09:12 WX-10211 师傅岑立诚出发，工单：洗衣机不脱水
2026-10-07 10:40 WX-10211 完成，更换皮带
2026-10-07 11:05 WX-10212 师傅尚雅琴出发，工单：冰箱制冷差
2026-10-07 12:31 WX-10212 完成，补焊管路
2026-10-07 14:02 WX-10213 师傅岑立诚出发，工单：油烟机不启动
2026-10-07 15:20 WX-10213 完成，更换电容
2026-10-07 16:44 WX-10214 师傅尚雅琴出发，工单：燃气灶熄火
2026-10-07 18:05 WX-10214 完成，更换热电偶
"""
log35_files = {
    "日志/上门-20261006.log": "2026-10-06 10:20 WX-10205 师傅尚雅琴出发，工单：空调移机\n2026-10-06 12:05 WX-10205 完成，加装支架\n",
    "日志/上门-20261007.log": log35,
    "README.md": "邻安家电 上门服务日志，时间均为北京时间。\n",
}
write_case(
    "log-8035",
    desc="Turn 1 reads the visit log for the fridge call's departure time; turn 2 forbids tools and asks how many jobs the same technician ran that day",
    task_type="time_window", family="fam-log-b10-visitlog-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=log35_files,
    turns=[
        {"prompt": "邻安家电 10 月 7 日的上门日志里，冰箱制冷差那单是几点出发的？",
         "expect": {"output_contains": ["11:05"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "先别调工具，就按刚才读到的日志说：岑立诚 10 月 7 日一共跑了几单？",
         "expect": dict(NOCALL, output_contains_any=["2 单", "2单", "两单"], max_output_chars=300)},
    ],
    verify='' + vhead(log35_files) + '''
log = files["日志/上门-20261007.log"]
fridge = [l for l in log.splitlines() if "冰箱制冷差" in l][0]
assert fridge.startswith("2026-10-07 11:05")
runs = [l for l in log.splitlines() if "师傅岑立诚出发" in l]
assert len(runs) == 2 and "WX-10211" in runs[0] and "WX-10213" in runs[1]
assert "冰箱制冷差" not in files["日志/上门-20261006.log"]
print(json.dumps({"expected_string": "11:05"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的日志数出来：岑立诚当天出发记录有两条（WX-10211、WX-10213）；尚雅琴也是两单但不是问的人。

## Reference solution
1. 第 1 轮读 日志/上门-20261007.log：冰箱制冷差是 WX-10212，11:05 由尚雅琴出发。终答一句话给出时间与依据。
第 2 轮零调用：同一天日志里「师傅岑立诚出发」出现两次（09:12 洗衣机、14:02 油烟机）。终答一句话，例如「岑立诚那天跑了两单，一次 9 点多一次下午两点。」判据：第 1 轮含 11:05；第 2 轮零调用并给出 2（数字或「两」）。

## Why the answer is unique
出发记录逐行可数，岑立诚 10 月 7 日恰好两条；冰箱制冷差那单只有一条出发记录。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8036
log36 = """2026-10-06 08:20 JOB-4417 make-ready, silk 150 gsm, 2 plates
2026-10-06 08:55 JOB-4417 run start, 12,000 sheets
2026-10-06 11:37 JOB-4417 run complete, 12,000 sheets
2026-10-06 11:52 JOB-4418 make-ready, board 300 gsm, 1 plate
2026-10-06 12:26 JOB-4418 run start, 3,500 sheets
2026-10-06 13:41 JOB-4418 run complete, 3,500 sheets
2026-10-06 14:10 JOB-4419 make-ready, uncoated 100 gsm, 4 plates
2026-10-06 14:39 JOB-4419 run start, 8,200 sheets
2026-10-06 15:58 JOB-4419 run complete, 8,200 sheets
2026-10-06 16:30 wash-up, all units
"""
log36_files = {
    "logs/press-log-2026-10-06.log": log36,
    "README.md": "Copperplate & Co. press log, one line per event, local time.\n",
}
write_case(
    "log-8036",
    desc="Turn 1 reads the press log for a job's run start; turn 2 forbids tools and asks the run's duration in minutes",
    task_type="time_window", family="fam-log-b10-pressrun-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log36_files,
    turns=[
        {"prompt": "When did the press run for JOB-4419 start on October 6?",
         "expect": {"output_contains": ["14:39"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "No more tool calls — from the same log you already read: how long did that JOB-4419 run take, in minutes?",
         "expect": dict(NOCALL, output_contains_any=["79", "79 minutes", "79min"], max_output_chars=300)},
    ],
    verify='' + vhead(log36_files) + '''
log = files["logs/press-log-2026-10-06.log"]
start = [l for l in log.splitlines() if "JOB-4419 run start" in l][0]
done = [l for l in log.splitlines() if "JOB-4419 run complete" in l][0]
assert start.startswith("2026-10-06 14:39") and done.startswith("2026-10-06 15:58")
mins = (15 - 14) * 60 + (58 - 39)
assert mins == 79
print(json.dumps({"expected_string": "14:39"}))
''',
    notes='''
## Traps
- None. Turn 2 works from the JOB-4419 lines read in turn 1: 14:39 to 15:58 is 79 minutes.

## Reference solution
1. Turn 1: read logs/press-log-2026-10-06.log: JOB-4419's run starts at 14:39. Final answer in one sentence: the run started at 14:39.
Turn 2, no tool call: the same log shows run complete at 15:58, so the run took 79 minutes. Final answer in one sentence. Criteria: turn 1 contains 14:39; turn 2 is zero-call and says 79.

## Why the answer is unique
JOB-4419 has exactly one run start and one run complete line; 15:58 − 14:39 = 79 minutes has no second reading. Both lines were in the turn-1 read, and the user forbade more tool calls.
''',
)

# ---------------------------------------------------------------- log-8037
log37 = """2026-10-06 21:47 派单 RS-6112 浙A·T30K9 电瓶亏电，天目山路
2026-10-06 22:05 RS-6112 到达，搭电启动
2026-10-06 22:31 RS-6112 收队
2026-10-06 23:58 派单 RS-6113 浙A·M15C4 爆胎，古墩路
2026-10-07 00:22 RS-6113 到达，换备胎
2026-10-07 00:58 RS-6113 收队
"""
log37_files = {
    "救援/夜间救援-20261005.log": "2026-10-05 22:40 派单 RS-6098 浙A·P6W3 无法启动，文一西路\n2026-10-05 23:35 RS-6098 收队，现场能启动\n",
    "救援/夜间救援-20261006.log": log37,
    "README.md": "广诚汽修 夜间救援记录，时间均为北京时间。\n",
}
write_case(
    "log-8037",
    desc="Turn 1 reads the night-rescue log for when the tyre job was dispatched; turn 2 forbids tools and asks that job's total minutes from dispatch to close",
    task_type="time_window", family="fam-log-b10-nighttow-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=log37_files,
    turns=[
        {"prompt": "广诚汽修夜间救援记录里，爆胎那单是几点派的单？",
         "expect": {"output_contains": ["23:58"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别动工具，就按刚才读到的记录说：RS-6113 那单从派单到收队一共用了多少分钟？",
         "expect": dict(NOCALL, output_contains_any=["60", "60 分钟", "60分钟", "一小时", "1 小时", "1小时"], max_output_chars=300)},
    ],
    verify='' + vhead(log37_files) + '''
log = files["救援/夜间救援-20261006.log"]
disp = [l for l in log.splitlines() if "派单 RS-6113" in l][0]
done = [l for l in log.splitlines() if "RS-6113 收队" in l][0]
assert disp.startswith("2026-10-06 23:58") and done.startswith("2026-10-07 00:58")
assert (0 * 60 + 58) + (24 * 60 - (23 * 60 + 58)) == 60
assert "爆胎" not in files["救援/夜间救援-20261005.log"]
print(json.dumps({"expected_string": "23:58"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的记录作答：RS-6113 派单 23:58、收队次日 00:58，跨过午夜正好 60 分钟；电瓶那单 RS-6112 用时更短，不是问的对象。

## Reference solution
1. 第 1 轮读 救援/夜间救援-20261006.log：爆胎 RS-6113 于 23:58 派单。终答一句话给出派单时间与依据。
第 2 轮零调用：同一份记录里它 00:58 收队，23:58 到次日 00:58 共 60 分钟。终答一句话，例如「从 23:58 派单到第二天凌晨 00:58 收队，一共 60 分钟。」判据：第 1 轮含 23:58；第 2 轮零调用并给出 60。

## Why the answer is unique
RS-6113 的派单、到达、收队各只有一条记录，起止时间唯一；跨午夜相减 60 分钟没有第二种算法。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8038
log38 = """09:03 来电 C-2101 洗衣机异响 转维修组
09:17 来电 C-2102 冰箱门封条老化 预约更换
09:52 来电 C-2103 空调不制冷 转维修组
10:26 来电 C-2104 热水器漏水 转维修组
10:41 来电 C-2105 微波炉不加热 转维修组
11:15 来电 C-2106 洗碗机不进水 改约周五
13:02 来电 C-2107 空调噪音 转维修组
14:37 来电 C-2108 冰箱制冷差 转维修组
15:12 来电 C-2109 油烟机按键失灵 转维修组
16:48 来电 C-2110 燃气灶打不着火 转维修组
"""
log38_files = {
    "日志/客服来电-20261004.log": log38,
    "README.md": "邦宁家电服务 客服来电记录，一行一通电话。\n",
}
write_case(
    "log-8038",
    desc="Turn 1 reads the call log for what complaint C-2105 was about; turn 2 forbids tools and asks when that call came in",
    task_type="time_window", family="fam-log-b10-callqueue-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log38_files,
    turns=[
        {"prompt": "邦宁家电 10 月 4 日的来电记录里，C-2105 那通电话反映的是什么问题？",
         "expect": {"output_contains": ["微波炉"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的记录说：那通电话是几点接进来的？",
         "expect": dict(NOCALL, output_contains=["10:41"], max_output_chars=300)},
    ],
    verify='' + vhead(log38_files) + '''
line = [l for l in files["日志/客服来电-20261004.log"].splitlines() if "C-2105" in l][0]
assert line == "10:41 来电 C-2105 微波炉不加热 转维修组"
assert len([l for l in files["日志/客服来电-20261004.log"].splitlines() if "来电" in l]) == 10
print(json.dumps({"expected_string": "10:41"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的来电记录作答：C-2105 在 10:41 接入；每通电话的时间和问题在同一行。

## Reference solution
1. 第 1 轮读 日志/客服来电-20261004.log：C-2105 反映微波炉不加热。终答一句话给出问题与依据。
第 2 轮零调用：同一行写明 10:41 来电。终答一句话，例如「那通微波炉的电话是 10:41 接进来的。」判据：第 1 轮含微波炉；第 2 轮零调用并含 10:41。

## Why the answer is unique
每通电话一行，C-2105 只出现一次，时间与问题都在这一行；第 2 轮需要的信息已在第 1 轮的读取结果里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8039
log39 = """08:22 入库 机油滤清器 x40 批次 B-0912
09:15 出库 前刹车片 x2 工单 WX-3310
10:02 入库 空调滤芯 x60 批次 B-0915
10:47 出库 火花塞 x8 工单 WX-3311
11:30 出库 机油滤清器 x3 工单 WX-3312
13:41 出库 前刹车片 x4 工单 WX-3314
14:26 入库 雨刮片 x30 批次 B-0921
15:33 出库 空调滤芯 x1 工单 WX-3315
16:50 出库 机油滤清器 x5 工单 WX-3316
"""
log39_files = {
    "仓库/配件流水-20261009.log": log39,
    "README.md": "驰远汽修 配件出入库流水，一行一笔。\n",
}
write_case(
    "log-8039",
    desc="Turn 1 reads the parts flow for the last cabin-filter issue time; turn 2 forbids tools and asks how many the B-0915 intake held",
    task_type="time_window", family="fam-log-b10-partinout-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log39_files,
    turns=[
        {"prompt": "驰远汽修 配件流水里，空调滤芯最后一次出库是几点？",
         "expect": {"output_contains": ["15:33"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调工具了，就按刚才读到的流水说：B-0915 那批空调滤芯入库了多少个？",
         "expect": dict(NOCALL, output_contains_any=["60", "60 个", "60个"], max_output_chars=300)},
    ],
    verify='' + vhead(log39_files) + '''
log = files["仓库/配件流水-20261009.log"]
out = [l for l in log.splitlines() if "出库 空调滤芯" in l]
assert out and out[-1].startswith("15:33")
inrow = [l for l in log.splitlines() if "B-0915" in l][0]
assert inrow == "10:02 入库 空调滤芯 x60 批次 B-0915"
print(json.dumps({"expected_string": "15:33"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的流水作答：B-0915 批次入库 60 个空调滤芯；15:33 那笔出库只有 1 个，是另一码事。

## Reference solution
1. 第 1 轮读 仓库/配件流水-20261009.log：空调滤芯只有 15:33 一笔出库。终答一句话给出时间与依据。
第 2 轮零调用：同一份流水里 10:02 入库 空调滤芯 x60 批次 B-0915。终答一句话，例如「B-0915 那批进了 60 个空调滤芯，10:02 入库的。」判据：第 1 轮含 15:33；第 2 轮零调用并给出 60。

## Why the answer is unique
流水里空调滤芯的入库与出库各只有一行，时间与数量唯一；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8040
log40 = """2026-10-07 09:10 cutter setup, JOB-4390, 12-up grid
2026-10-07 09:31 cutter run, JOB-4390, 14,400 cuts
2026-10-07 10:05 fold queue, JOB-4390, letter fold
2026-10-07 10:48 cutter setup, JOB-4391, 6-up grid
2026-10-07 11:12 blade change, guard interlock test ok
2026-10-07 11:20 cutter run, JOB-4391, 6,600 cuts
2026-10-07 12:02 fold queue, JOB-4391, gate fold
2026-10-07 13:34 stitcher run, JOB-4392, 2 staples, 800 books
"""
log40_files = {
    "logs/finishing-2026-10-07.log": log40,
    "README.md": "Marginalia Press finishing-room log, local time, one event per line.\n",
}
write_case(
    "log-8040",
    desc="Turn 1 reads the finishing log for the blade-change time; turn 2 forbids tools and asks the grid the next job was cut on",
    task_type="time_window", family="fam-log-b10-cutterlog-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log40_files,
    turns=[
        {"prompt": "When did the blade change happen in the finishing log for October 7?",
         "expect": {"output_contains": ["11:12"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "Without calling any tools, going by what you already read: what grid was JOB-4391 cut on?",
         "expect": dict(NOCALL, output_contains_any=["6-up", "6 up", "6up"], max_output_chars=300)},
    ],
    verify='' + vhead(log40_files) + '''
log = files["logs/finishing-2026-10-07.log"]
blade = [l for l in log.splitlines() if "blade change" in l][0]
grid = [l for l in log.splitlines() if "JOB-4391" in l and "grid" in l][0]
assert blade.startswith("2026-10-07 11:12")
assert grid.endswith("6-up grid")
assert len([l for l in log.splitlines() if "grid" in l]) == 2
print(json.dumps({"expected_string": "11:12"}))
''',
    notes='''
## Traps
- None. Turn 2 must be answered from the log read in turn 1: JOB-4391's setup line says 6-up grid; JOB-4390's 12-up is the other job.

## Reference solution
1. Turn 1: read logs/finishing-2026-10-07.log: the blade change is logged at 11:12. Final answer in one sentence: the blade change happened at 11:12.
Turn 2, no tool call: the same log's cutter setup line for JOB-4391 reads 6-up grid. Final answer in one sentence. Criteria: turn 1 contains 11:12; turn 2 is zero-call and says 6-up.

## Why the answer is unique
The log has one blade-change line and one setup line per job, so both answers are single-valued; 12-up belongs to JOB-4390. Both lines were in the turn-1 read, and the user forbade more tool calls.
''',
)

# ---------------------------------------------------------------- log-8041
log41 = """2026-10-02 10:15 JB-8011 挂机 KF-35 延保 2 年
2026-10-06 14:40 JB-8012 滚筒洗衣机 XQG-80 延保 1 年
2026-10-09 09:22 JB-8013 对开门冰箱 BCD-520 延保 2 年
2026-10-11 16:05 JB-8014 燃气热水器 JSQ-25 延保 3 年
"""
log41_files = {
    "延保/开通流水-202610.log": log41,
    "README.md": "泰和家电售后 延保开通流水，一行一笔。\n",
}
write_case(
    "log-8041",
    desc="Turn 1 reads the extended-warranty flow for the fridge's reference number; turn 2 forbids tools and asks the date that cover was activated",
    task_type="time_window", family="fam-log-b10-coverflow-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=log41_files,
    turns=[
        {"prompt": "泰和家电 10 月的延保开通流水里，对开门冰箱那笔的单号是什么？",
         "expect": {"output_contains": ["JB-8013"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "先别调用工具，就按刚才读到的流水说：JB-8013 那笔延保是哪天开通的？",
         "expect": dict(NOCALL, output_contains_any=zh_date("2026-10-09"), max_output_chars=300)},
    ],
    verify='' + vhead(log41_files) + '''
row = [l for l in files["延保/开通流水-202610.log"].splitlines() if "JB-8013" in l][0]
assert row.startswith("2026-10-09") and "对开门冰箱 BCD-520" in row
assert len([l for l in files["延保/开通流水-202610.log"].splitlines() if l.startswith("2026-10-")]) == 4
print(json.dumps({"expected_string": "JB-8013"}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的流水行作答：JB-8013 开通日期是 2026-10-09；其余三笔是别的家电和日期。

## Reference solution
1. 第 1 轮读 延保/开通流水-202610.log：对开门冰箱 BCD-520 那笔单号 JB-8013。终答一句话给出单号与依据。
第 2 轮零调用：同一行开头就是开通日期 2026-10-09。终答一句话，例如「JB-8013 是 10 月 9 日开通的，流水那一行写着。」判据：第 1 轮含 JB-8013；第 2 轮零调用并给出 2026-10-09（任一写法）。

## Why the answer is unique
流水一行一笔，JB-8013 只出现一次，单号与开通日期都在这一行；第 2 轮需要的信息已在第 1 轮的读取结果里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- tab-8042
import random
rng = random.Random(42002)
_stores = ["城北店", "开发区店", "老城店"]
_rows = []
for _i in range(96):
    _rows.append(("WO-72%03d" % (100 + _i), "2026-09-%02d" % rng.randint(1, 30),
                  _stores[_i % 3] if _i % 4 else rng.choice(_stores), "%.2f" % rng.uniform(140, 2600)))
_rows.sort(key=lambda r: r[1])
kf = round(sum(float(r[3]) for r in _rows if r[2] == "开发区店"), 2)
wan = "%.2f" % (kf / 10000)
tab42_files = {
    "产值/9月维修产值.csv": "工单号,日期,门店,产值\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "# 永固汽修 经营数据\n\n产值为已收工费与配件收入合计，单位元，含税。\n",
}
write_case(
    "tab-8042",
    desc="Turn 1 totals one branch's September repair revenue; turn 2 forbids tools and asks the same total expressed in units of ten thousand yuan",
    task_type="aggregate", family="fam-tab-b10-repairrev-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab42_files,
    turns=[
        {"prompt": "统计一下永固汽修 9 月开发区店的维修产值合计是多少元？",
         "expect": {"output_contains_any": money_forms(kf), "max_output_chars": 300}},
        {"prompt": "先别调工具，就按刚才那个数换算：开发区店 9 月的产值是多少万元？保留两位小数。",
         "expect": dict(NOCALL, output_contains_any=[wan], max_output_chars=300)},
    ],
    verify='' + vhead(tab42_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["产值/9月维修产值.csv"])))
total = round(sum(float(r["产值"]) for r in rows if r["门店"] == "开发区店"), 2)
assert total == %r
wan2 = "%%.2f" %% (total / 10000)
assert wan2 == %r
''' % (kf, wan) + echo(money_forms(kf) + [wan], zh=True),
    notes='''
## Traps
- None. 第 2 轮是对第 1 轮的合计做一步换算（除以一万、保留两位），用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 产值/9月维修产值.csv 按 门店=开发区店 求和 产值（或整读后合计）：%s 元。终答一句话给出金额与口径（含税）。
第 2 轮零调用：%s ÷ 10000 = %s 万元。终答一句话，例如「开发区店 9 月产值 %s 元，折合 %s 万元。」判据：第 1 轮含 %s（或千分位写法）；第 2 轮零调用并含 %s。

## Why the answer is unique
产值只有一个口径（元、含税），开发区店的行由门店列唯一确定；第 2 轮只是把同一个数除以一万并保留两位。
''' % ("%.2f" % kf, "%.2f" % kf, wan, "%.2f" % kf, wan, "%.2f" % kf, wan),
)

# ---------------------------------------------------------------- tab-8043
rng = random.Random(43003)
_sites = ["翠苑站", "拱宸站", "留下站"]
_rows = []
_n = 0
for _d in range(1, 11):
    for _k in range(rng.randint(3, 6)):
        _n += 1
        _rows.append(("GD-4%03d" % (200 + _n), "2026-10-%02d" % _d, rng.choice(_sites)))
_g = sum(1 for r in _rows if r[2] == "拱宸站")
_avg = _g / 10
_avg_forms = [str(int(round(_avg)))] if abs(_avg - round(_avg)) < 1e-9 else ["%.1f" % _avg]
tab43_files = {
    "回访/10月上旬上门明细.csv": "工单号,日期,站点\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "# 海月家电服务 上门明细\n\n每行一张已完成的上门工单，10 月 1 日至 10 日。\n",
}
write_case(
    "tab-8043",
    desc="Turn 1 counts one service station's completed home visits over ten days; turn 2 forbids tools and asks the same count as a per-day average",
    task_type="filter_count", family="fam-tab-b10-visitcount-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab43_files,
    turns=[
        {"prompt": "海月家电 10 月 1 日到 10 日，拱宸站一共完成了多少单上门？",
         "expect": {"output_contains_any": zh_count(_g, "单"), "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才那个数：平均每天完成多少单？",
         "expect": dict(NOCALL, output_contains_any=_avg_forms, max_output_chars=300)},
    ],
    verify='' + vhead(tab43_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["回访/10月上旬上门明细.csv"])))
n = sum(1 for r in rows if r["站点"] == "拱宸站")
assert n == %d
avg = n / 10
assert ("%%.1f" %% avg).rstrip("0").rstrip(".") == %r
''' % (_g, ("%.1f" % _avg).rstrip("0").rstrip(".")) + echo(zh_count(_g, "单") + _avg_forms, zh=True),
    notes='''
## Traps
- None. 第 2 轮是把第 1 轮的单数除以 10 天，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 统计 回访/10月上旬上门明细.csv 里 站点=拱宸站 的行数（或整读后数）：%d 单。终答一句话给出单数与时间范围。
第 2 轮零调用：%d ÷ 10 = %s 单/天。终答一句话，例如「拱宸站 10 天做了 %d 单，平均每天 %s 单。」判据：第 1 轮含 %d；第 2 轮零调用并含 %s。

## Why the answer is unique
每行一张工单，拱宸站的行由站点列唯一确定；第 2 轮只是把同一个数除以 10。
''' % (_g, _g, _avg_forms[0], _g, _avg_forms[0], _g, _avg_forms[0]),
)

# ---------------------------------------------------------------- tab-8044
rng = random.Random(44004)
_stocks = ["Uncoated 100 gsm", "Silk-coated 150 gsm", "Board 300 gsm"]
_rows = []
for _d in range(1, 15):
    for _k in range(rng.randint(2, 3)):
        _rows.append(("2026-10-%02d" % _d, rng.choice(_stocks), rng.choice([400, 600, 800, 1200, 1600, 2600])))
_silk = [r for r in _rows if r[1] == "Silk-coated 150 gsm"]
assert len(_silk) >= 3
_r = sum(r[2] for r in _silk) % 250
if _r:
    _rows[_rows.index(_silk[0])] = (_silk[0][0], _silk[0][1], _silk[0][2] - _r)
S = sum(r[2] for r in _rows if r[1] == "Silk-coated 150 gsm")
assert S % 250 == 0 and S >= 1000
_reams = S / 500.0
_ream_forms = [str(int(_reams))] if abs(_reams - round(_reams)) < 1e-9 else ["%.1f" % _reams]
tab44_files = {
    "usage/october-usage.csv": "date,stock,sheets\n" + "".join(",".join((r[0], r[1], str(r[2]))) + "\n" for r in _rows),
    "README.md": "Broadleaf Printroom stock usage, one row per job date. Reams are 500 sheets.\n",
}
write_case(
    "tab-8044",
    desc="Turn 1 totals one paper stock's sheet usage for early October; turn 2 forbids tools and asks the same total converted to reams",
    task_type="aggregate", family="fam-tab-b10-reamuse-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab44_files,
    turns=[
        {"prompt": "How many sheets of the silk-coated 150 gsm stock did Broadleaf use from October 1 through 14?",
         "expect": {"output_contains_any": int_forms(S), "max_output_chars": 300}},
        {"prompt": "No more tool calls — going by what you already read: how many reams does that silk stock come to, at 500 sheets to a ream?",
         "expect": dict(NOCALL, output_contains_any=[f + " ream" for f in _ream_forms], max_output_chars=300)},
    ],
    verify='' + vhead(tab44_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["usage/october-usage.csv"])))
total = sum(int(r["sheets"]) for r in rows if r["stock"] == "Silk-coated 150 gsm")
assert total == %d
reams = total / 500.0
assert ("%%.1f" %% reams).rstrip("0").rstrip(".") == %r
''' % (S, ("%.1f" % _reams).rstrip("0").rstrip(".")) + echo(int_forms(S) + [f + " ream" for f in _ream_forms], zh=False),
    notes='''
## Traps
- None. Turn 2 is one step from the turn-1 total: divide by 500 sheets per ream, with no further tool calls.

## Reference solution
1. Turn 1: total the silk-coated 150 gsm rows of usage/october-usage.csv for Oct 1-14 (data_query filter, or read and add): %s sheets. Final answer in one sentence with the date range.
Turn 2, no tool call: %s / 500 = %s reams. Final answer in one sentence. Criteria: turn 1 contains %s (either spelling); turn 2 is zero-call and contains %s.

## Why the answer is unique
Each row is one job's sheet count and the stock column pins the rows; reams follow from the single division by 500 that the README states.
''' % (int_forms(S)[0], int_forms(S)[0], _ream_forms[0], int_forms(S)[0], _ream_forms[0]),
)

# ---------------------------------------------------------------- tab-8045
rng = random.Random(45005)
_parts = ["机油滤清器", "空调滤芯", "火花塞", "雨刮片", "刹车油"]
_rows = []
for _d in range(1, 29):
    if rng.random() < 0.75:
        _rows.append(("2026-09-%02d" % _d, rng.choice(_parts), rng.randint(1, 8), "WX-40%02d" % (10 + len(_rows))))
_plugs = [r for r in _rows if r[1] == "火花塞"]
assert len(_plugs) >= 3
_r = sum(r[2] for r in _plugs) % 4
if _r:
    for _j, _p in enumerate(_plugs):
        if _p[2] > _r:
            _rows[_rows.index(_p)] = (_p[0], _p[1], _p[2] - _r, _p[3])
            break
    else:
        _rows[_rows.index(_plugs[-1])] = (_plugs[-1][0], _plugs[-1][1], _plugs[-1][2] + 4 - _r, _plugs[-1][3])
P = sum(r[2] for r in _rows if r[1] == "火花塞")
assert P % 4 == 0 and P >= 12
_boxes = P // 4
tab45_files = {
    "仓库/9月出库明细.csv": "日期,配件,数量,工单号\n" + "".join(",".join((r[0], r[1], str(r[2]), r[3])) + "\n" for r in _rows),
    "README.md": "# 八方汽修 配件出库\n\n每行一张维修工单的出库，数量一律按支计。火花塞整盒进货，每盒 4 支。\n",
}
write_case(
    "tab-8045",
    desc="Turn 1 totals September spark-plug issues by piece; turn 2 forbids tools and asks the same quantity converted to boxes of four",
    task_type="aggregate", family="fam-tab-b10-partboxes-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab45_files,
    turns=[
        {"prompt": "八方汽修 9 月火花塞一共出库了多少支？",
         "expect": {"output_contains_any": zh_count(P, "支"), "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才那个数：火花塞每盒 4 支，折合多少盒？",
         "expect": dict(NOCALL, output_contains_any=zh_count(_boxes, "盒"), max_output_chars=300)},
    ],
    verify='' + vhead(tab45_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["仓库/9月出库明细.csv"])))
plugs = sum(int(r["数量"]) for r in rows if r["配件"] == "火花塞")
assert plugs == %d and plugs %% 4 == 0
assert plugs // 4 == %d
''' % (P, _boxes) + echo(zh_count(P, "支") + zh_count(_boxes, "盒"), zh=True),
    notes='''
## Traps
- None. 第 2 轮是把第 1 轮的支数除以每盒 4 支，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 仓库/9月出库明细.csv 按 配件=火花塞 求和 数量（或整读后合计）：%d 支。终答一句话给出支数。
第 2 轮零调用：%d ÷ 4 = %d 盒。终答一句话，例如「9 月火花塞出了 %d 支，按每盒 4 支正好 %d 盒。」判据：第 1 轮含 %d；第 2 轮零调用并含 %d。

## Why the answer is unique
每行一张工单的出库数量，火花塞的行由配件列唯一确定，合计能被 4 整除；第 2 轮只是同一个数除以 4。
''' % (P, P, _boxes, P, _boxes, P, _boxes),
)

# ---------------------------------------------------------------- tab-8046
rng = random.Random(46006)
_ch = ["热线", "小程序", "门店"]
_ty = ["报修", "咨询", "投诉"]
_rows = []
for _d in range(1, 31):
    for _k in range(rng.randint(4, 7)):
        _rows.append(("2026-09-%02d" % _d, rng.choice(_ch), rng.choice(_ty)))
A = sum(1 for r in _rows if r[1] == "热线" and r[2] == "报修")
B = sum(1 for r in _rows if r[1] == "小程序" and r[2] == "报修")
if A < B:
    _rows = [(d, {"热线": "小程序", "小程序": "热线"}.get(c, c), t) for d, c, t in _rows]
    A, B = B, A
if A == B:
    _j = next(i for i, r in enumerate(_rows) if r[1] == "小程序" and r[2] == "报修")
    _rows[_j] = (_rows[_j][0], "门店", _rows[_j][2])
    B -= 1
assert A > B >= 2, (A, B)
tab46_files = {
    "客服/9月来电台账.csv": "日期,渠道,类型\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "# 云汀家电服务 来电与留言台账\n\n每行一笔进线，类型按受理口径登记。\n",
}
write_case(
    "tab-8046",
    desc="Turn 1 counts September repair requests on two channels; turn 2 forbids tools and asks the gap between the two counts",
    task_type="filter_count", family="fam-tab-b10-callsplit-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab46_files,
    turns=[
        {"prompt": "云汀家电 9 月的来电记录里，热线和小程序各自进了多少笔报修？",
         "expect": {"output_contains": [str(A), str(B)], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的两个数说：热线报修比小程序报修多多少笔？",
         "expect": dict(NOCALL, output_contains_any=zh_count(A - B, "笔"), max_output_chars=300)},
    ],
    verify='' + vhead(tab46_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["客服/9月来电台账.csv"])))
hot = sum(1 for r in rows if r["渠道"] == "热线" and r["类型"] == "报修")
mini = sum(1 for r in rows if r["渠道"] == "小程序" and r["类型"] == "报修")
assert hot == %d and mini == %d and hot - mini == %d
''' % (A, B, A - B) + echo(zh_count(A - B, "笔"), zh=True),
    notes='''
## Traps
- None. 第 2 轮是对第 1 轮的两个数做一步减法，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 统计 客服/9月来电台账.csv 里 渠道=热线、类型=报修 与 渠道=小程序、类型=报修 的行数（或整读后数）：热线 %d 笔、小程序 %d 笔。终答一句话给出两个数。
第 2 轮零调用：%d − %d = %d 笔。终答一句话，例如「热线 %d 笔、小程序 %d 笔，热线多 %d 笔。」判据：第 1 轮同时含 %d 和 %d；第 2 轮零调用并含 %d。

## Why the answer is unique
每行一笔进线，渠道与类型两列唯一确定两组计数；第 2 轮只是两个数相减。
''' % (A, B, A, B, A - B, A, B, A - B, A, B, A - B),
)

# ---------------------------------------------------------------- tab-8047
rng = random.Random(47007)
_rows = []
for _d in range(1, 21):
    if rng.random() < 0.75:
        _rows.append(("2026-10-%02d" % _d, rng.choice(["冰箱", "洗衣机", "空调"]), rng.randint(1, 2)))
C = sum(r[2] for r in _rows if r[1] == "洗衣机")
for _j, _row in enumerate(_rows):
    if C >= 12:
        break
    if _row[1] == "冰箱":
        _rows[_j] = (_row[0], "洗衣机", _row[2])
        C += _row[2]
assert C >= 12
AMT = C * 300
tab47_files = {
    "补贴/10月洗衣机补贴.csv": "日期,品类,台数\n" + "".join(",".join((r[0], r[1], str(r[2]))) + "\n" for r in _rows),
    "README.md": "# 悦庭家电服务 换新补贴发放\n\n每行一个门店当日的发放登记；洗衣机品类按每台 300 元标准发放。\n",
}
write_case(
    "tab-8047",
    desc="Turn 1 totals October washer trade-in payouts by unit; turn 2 forbids tools and asks the same total in yuan at the 300-yuan standard",
    task_type="aggregate", family="fam-tab-b10-standardpay-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab47_files,
    turns=[
        {"prompt": "悦庭家电 10 月洗衣机品类的换新补贴一共发了多少台？",
         "expect": {"output_contains_any": zh_count(C, "台"), "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才那个数：按每台 300 元的标准，补贴金额合计是多少元？",
         "expect": dict(NOCALL, output_contains_any=int_forms(AMT), max_output_chars=300)},
    ],
    verify='' + vhead(tab47_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["补贴/10月洗衣机补贴.csv"])))
units = sum(int(r["台数"]) for r in rows if r["品类"] == "洗衣机")
assert units == %d
assert units * 300 == %d
''' % (C, AMT) + echo(zh_count(C, "台") + int_forms(AMT), zh=True),
    notes='''
## Traps
- None. 第 2 轮是把第 1 轮的台数乘以每台 300 元的标准，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 补贴/10月洗衣机补贴.csv 按 品类=洗衣机 求和 台数（或整读后合计）：%d 台。终答一句话给出台数。
第 2 轮零调用：%d × 300 = %s 元。终答一句话，例如「洗衣机补贴发了 %d 台，按每台 300 元是 %s 元。」判据：第 1 轮含 %d；第 2 轮零调用并含 %s。

## Why the answer is unique
每行一个门店当日的发放登记，洗衣机的行由品类列唯一确定；每台 300 元的标准写在台账说明里，第 2 轮只是同一个数乘以 300。
''' % (C, C, int_forms(AMT)[0], C, int_forms(AMT)[0], C, int_forms(AMT)[0]),
)

# ---------------------------------------------------------------- tab-8048
rng = random.Random(48008)
_depots = ["城南站", "未来站", "塘栖站"]
_rows = []
for _i in range(84):
    _rows.append(("TR-63%02d" % (10 + _i), "2026-09-%02d" % rng.randint(1, 30),
                  _depots[_i % 3] if _i % 4 else rng.choice(_depots), "%.2f" % rng.uniform(180, 1500)))
_rows.sort(key=lambda r: r[1])
M = round(sum(float(r[3]) for r in _rows if r[2] == "未来站"), 2)
_wan = "%.2f" % (M / 10000)
tab48_files = {
    "救援/9月拖车收入.csv": "单号,日期,网点,金额\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "# 凯驰汽修 救援拖车收入\n\n金额为每单实收，单位元。\n",
}
write_case(
    "tab-8048",
    desc="Turn 1 totals one depot's September tow revenue; turn 2 forbids tools and asks the same total in units of ten thousand yuan",
    task_type="aggregate", family="fam-tab-b10-towtally-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab48_files,
    turns=[
        {"prompt": "凯驰汽修 9 月未来站的拖车收入合计是多少元？",
         "expect": {"output_contains_any": money_forms(M), "max_output_chars": 300}},
        {"prompt": "别再调工具了，就刚才那个数：折合成万元是多少？保留两位小数。",
         "expect": dict(NOCALL, output_contains_any=[_wan], max_output_chars=300)},
    ],
    verify='' + vhead(tab48_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["救援/9月拖车收入.csv"])))
total = round(sum(float(r["金额"]) for r in rows if r["网点"] == "未来站"), 2)
assert total == %r
assert ("%%.2f" %% (total / 10000)) == %r
''' % (M, _wan) + echo(money_forms(M) + [_wan], zh=True),
    notes='''
## Traps
- None. 第 2 轮是对第 1 轮的合计做一步换算（除以一万、保留两位），用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 救援/9月拖车收入.csv 按 网点=未来站 求和 金额（或整读后合计）：%s 元。终答一句话给出金额与时间范围。
第 2 轮零调用：%s ÷ 10000 = %s 万元。终答一句话，例如「未来站 9 月拖车收入 %s 元，折合 %s 万元。」判据：第 1 轮含 %s（或千分位写法）；第 2 轮零调用并含 %s。

## Why the answer is unique
金额只有一个口径（每单实收、元），未来站的行由网点列唯一确定；第 2 轮只是把同一个数除以一万并保留两位。
''' % ("%.2f" % M, "%.2f" % M, _wan, "%.2f" % M, _wan, "%.2f" % M, _wan),
)

# ---------------------------------------------------------------- tab-8049
rng = random.Random(49009)
_cat = ["冰箱", "洗衣机", "热水器"]
_rows = []
for _d in range(1, 15):
    for _k in range(rng.randint(1, 3)):
        _rows.append(("2026-10-%02d" % _d, rng.choice(_cat)))
W1 = sum(1 for r in _rows if r[0] <= "2026-10-07")
W2 = sum(1 for r in _rows if r[0] >= "2026-10-08")
assert W1 >= 3 and W2 >= 3
tab49_files = {
    "补贴/10月上半月.csv": "日期,品类\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "# 同风家电服务 换新补贴发放\n\n每行一台完成补贴发放的机器，上半月台账。\n",
}
write_case(
    "tab-8049",
    desc="Turn 1 counts trade-in subsidy payouts in each of two weeks; turn 2 forbids tools and asks the two-week total",
    task_type="filter_count", family="fam-tab-b10-subsidysum-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab49_files,
    turns=[
        {"prompt": "同风家电 10 月的换新补贴，第 1 周（1 到 7 日）和第 2 周（8 到 14 日）各发了多少台？",
         "expect": {"output_contains": [str(W1), str(W2)], "max_output_chars": 300}},
        {"prompt": "先别调工具，就按刚才读到的两个数说：两周加起来一共多少台？",
         "expect": dict(NOCALL, output_contains_any=zh_count(W1 + W2, "台"), max_output_chars=300)},
    ],
    verify='' + vhead(tab49_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["补贴/10月上半月.csv"])))
w1 = sum(1 for r in rows if r["日期"] <= "2026-10-07")
w2 = sum(1 for r in rows if r["日期"] >= "2026-10-08")
assert w1 == %d and w2 == %d and w1 + w2 == %d
assert w1 + w2 == len(rows)
''' % (W1, W2, W1 + W2) + echo(zh_count(W1 + W2, "台"), zh=True),
    notes='''
## Traps
- None. 第 2 轮是对第 1 轮的两个数做一步加法，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 统计 补贴/10月上半月.csv 里 日期 在 1–7 日与 8–14 日的行数（或整读后按日期分堆数）：第 1 周 %d 台、第 2 周 %d 台。终答一句话给出两个数。
第 2 轮零调用：%d + %d = %d 台。终答一句话，例如「两周一共发了 %d 台。」判据：第 1 轮同时含 %d 和 %d；第 2 轮零调用并含 %d。

## Why the answer is unique
每行一台，日期列唯一确定两周的归属，14 天全覆盖；第 2 轮只是两个数相加。
''' % (W1, W2, W1, W2, W1 + W2, W1 + W2, W1, W2, W1 + W2),
)

# ---------------------------------------------------------------- tab-8050
rng = random.Random(50010)
_crew = ["钣金组", "机修组", "电工组"]
_rows = []
for _d in range(1, 31):
    if rng.random() < 0.8:
        _rows.append(("2026-09-%02d" % _d, rng.choice(_crew), rng.choice([4.0, 4.5, 5.0, 6.0, 7.0, 7.5, 8.0, 9.0])))
_part = sum(r[2] for r in _rows if r[1] == "钣金组")
_close = ((4 - _part % 4) % 4) + 4
_rows.append(("2026-09-30", "钣金组", _close))
H = round(sum(r[2] for r in _rows if r[1] == "钣金组"), 1)
assert H % 4 == 0 and 4 <= _close < 8
_days = H / 8.0
_hbare = ("%.1f" % H).rstrip("0").rstrip(".")
_dbare = ("%.1f" % _days).rstrip("0").rstrip(".")
tab50_files = {
    "考勤/9月工时.csv": "日期,班组,工时\n" + "".join(",".join((r[0], r[1], "%.1f" % r[2])) + "\n" for r in _rows),
    "README.md": "# 望江汽修 9 月班组工时\n\n工时按半天（0.5）计，单位小时。\n",
}
write_case(
    "tab-8050",
    desc="Turn 1 totals the sheet-metal crew's September hours; turn 2 forbids tools and asks the same total converted to 8-hour man-days",
    task_type="aggregate", family="fam-tab-b10-hoursheet-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab50_files,
    turns=[
        {"prompt": "望江汽修 9 月钣金组的工时合计是多少小时？",
         "expect": {"output_contains_any": zh_count(_hbare, "小时") + zh_count(_hbare, "个小时") + zh_count(_hbare + ".0", "小时"), "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才那个数：按每班 8 小时折算，是多少个人日？",
         "expect": dict(NOCALL, output_contains_any=[_dbare, "%s 人日" % _dbare, "%s人日" % _dbare], max_output_chars=300)},
    ],
    verify='' + vhead(tab50_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["考勤/9月工时.csv"])))
hours = round(sum(float(r["工时"]) for r in rows if r["班组"] == "钣金组"), 1)
assert hours == %r
assert ("%%.1f" %% (hours / 8)).rstrip("0").rstrip(".") == %r
''' % (H, _dbare) + echo(zh_count(_hbare, "小时") + zh_count(_hbare, "个小时") + zh_count(_hbare + ".0", "小时") + [_dbare, "%s 人日" % _dbare, "%s人日" % _dbare], zh=True),
    notes='''
## Traps
- None. 第 2 轮是把第 1 轮的工时除以每班 8 小时，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 考勤/9月工时.csv 按 班组=钣金组 求和 工时（或整读后合计）：%s 小时。终答一句话给出小时数。
第 2 轮零调用：%s ÷ 8 = %s 人日。终答一句话，例如「钣金组 9 月共 %s 小时，折合 %s 个人日。」判据：第 1 轮含 %s；第 2 轮零调用并含 %s。

## Why the answer is unique
每行一个班组半天的工时，钣金组的行由班组列唯一确定，合计恰能整除 8；第 2 轮只是同一个数除以 8。
''' % (_hbare, _hbare, _dbare, _hbare, _dbare, _hbare, _dbare),
)

# ---------------------------------------------------------------- tab-8051
rng = random.Random(51011)
_fin = ["lamination", "spiral-coil", "hardcover"]
_rows = []
for _i in range(48):
    _rows.append(("2026-09-%02d" % rng.randint(1, 30), rng.choice(_fin), "%.2f" % rng.uniform(35, 420)))
L = round(sum(float(r[2]) for r in _rows if r[1] == "lamination"), 2)
S2 = round(sum(float(r[2]) for r in _rows if r[1] == "spiral-coil"), 2)
DIFF = round(L - S2, 2)
for _j, _row in enumerate(_rows):
    if DIFF > 0:
        break
    if _row[1] == "spiral-coil":
        _rows[_j] = (_row[0], "lamination", _row[2])
        L = round(sum(float(r[2]) for r in _rows if r[1] == "lamination"), 2)
        S2 = round(sum(float(r[2]) for r in _rows if r[1] == "spiral-coil"), 2)
        DIFF = round(L - S2, 2)
assert DIFF > 0 and S2 > 0
tab51_files = {
    "finishing/september-finishing.csv": "date,finish,revenue\n" + "".join(",".join(r) + "\n" for r in _rows),
    "README.md": "Truegrain Press September finishing revenue, one row per job. USD.\n",
}
write_case(
    "tab-8051",
    desc="Turn 1 totals September revenue for lamination and spiral-coil; turn 2 forbids tools and asks the gap between the two",
    task_type="aggregate", family="fam-tab-b10-finishcost-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=tab51_files,
    turns=[
        {"prompt": "What did Truegrain Press make from lamination and from spiral-coil finishing in September, each total?",
         "expect": {"output_contains_any": money_forms(L), "max_output_chars": 300}},
        {"prompt": "No more tool calls — from those two totals you already have: how much more did lamination bring in than spiral-coil, to the cent?",
         "expect": dict(NOCALL, output_contains_any=money_forms(DIFF), max_output_chars=300)},
    ],
    verify='' + vhead(tab51_files) + '''
import csv
import io

rows = list(csv.DictReader(io.StringIO(files["finishing/september-finishing.csv"])))
lam = round(sum(float(r["revenue"]) for r in rows if r["finish"] == "lamination"), 2)
coil = round(sum(float(r["revenue"]) for r in rows if r["finish"] == "spiral-coil"), 2)
assert lam == %r and coil == %r
assert round(lam - coil, 2) == %r
''' % (L, S2, DIFF) + echo(money_forms(L) + money_forms(DIFF), zh=False),
    notes='''
## Traps
- None. Turn 2 is one subtraction over the two totals from turn 1, with no further tool calls.

## Reference solution
1. Turn 1: total the lamination and spiral-coil rows of finishing/september-finishing.csv (data_query filter per finish, or read and add): lamination $%s, spiral-coil $%s. Final answer in one sentence giving both.
Turn 2, no tool call: %s − %s = $%s. Final answer in one sentence. Criteria: turn 1 contains the lamination total (either spelling); turn 2 is zero-call and contains %s, which also pins the spiral-coil total.

## Why the answer is unique
Each row is one job's revenue and the finish column pins the rows; the gap is a single subtraction of the two turn-1 totals.
''' % (money_forms(L)[0], money_forms(S2)[0], money_forms(L)[0], money_forms(S2)[0], money_forms(DIFF)[0], money_forms(DIFF)[0]),
)

# ---------------------------------------------------------------- doc-8023
doc23_files = {
    "手册/整机包修细则.md": "# 整机包修细则\n\n## 包修期限\n- 冰箱、洗衣机：整机包修 3 年。\n- 空调：整机包修 6 年。\n- 热水器：整机包修 3 年。\n- 主要部件（压缩机、电机、电脑板）：包修 10 年。\n\n## 不予包修\n- 自行拆机、进水、鼠咬造成的损坏。\n",
    "README.md": "# 青禾家电售后 制度文本\n\n包修口径以 手册/整机包修细则.md 为准。\n",
}
write_case(
    "doc-8023",
    desc="Turn 1 reads the warranty rule for a fridge's whole-machine cover; turn 2 forbids tools and asks the major-component term in the same rule",
    task_type="policy_lookup", family="fam-doc-b10-coverterm-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc23_files,
    turns=[
        {"prompt": "青禾售后的冰箱整机包修几年？",
         "expect": {"output_contains_any": ["3 年", "3年", "三年"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具了，就按刚才读到的包修细则说：压缩机这类主要部件包修几年？",
         "expect": dict(NOCALL, output_contains_any=["10 年", "10年", "十年"], max_output_chars=300)},
    ],
    verify='' + vhead(doc23_files) + '''
rule = files["手册/整机包修细则.md"]
assert "整机包修 3 年" in rule and "包修 10 年" in rule
assert "整机包修 6 年" in rule
''' + echo(["3 年", "3年", "三年", "10 年", "10年", "十年"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的包修细则作答：主要部件包修 10 年；整机的 3 年是另一个口径。

## Reference solution
1. 第 1 轮读 手册/整机包修细则.md：冰箱整机包修 3 年。终答一句话给出年限与依据。
第 2 轮零调用：同一份细则里主要部件（压缩机、电机、电脑板）包修 10 年。终答一句话，例如「压缩机按主要部件算，包修 10 年，细则里单列了一条。」判据：第 1 轮含 3 年（或三年）；第 2 轮零调用并含 10 年。

## Why the answer is unique
细则里整机与主要部件的年限各只有一个值，空调的 6 年是别的品类；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8024
doc24_files = {
    "作业/保养指导书.md": "# 保养作业指导书\n\n## 里程与间隔\n- 首保：新车 5000 公里或 6 个月，先到为准。\n- 常规保养：每 10000 公里或 12 个月。\n\n## 工位要求\n- 举升作业必须加保险凳。\n",
    "README.md": "# 天工汽修 作业制度\n\n保养口径见 作业/保养指导书.md。\n",
}
write_case(
    "doc-8024",
    desc="Turn 1 reads the maintenance guide for the first-service mileage; turn 2 forbids tools and asks the routine interval in the same guide",
    task_type="policy_lookup", family="fam-doc-b10-maintguide-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc24_files,
    turns=[
        {"prompt": "天工汽修的首保里程是多少公里？",
         "expect": {"output_contains_any": ["5000 公里", "5000公里", "5000"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的指导书说：常规保养的间隔是多少？",
         "expect": dict(NOCALL, output_contains_any=["10000 公里", "10000公里", "每 10000 公里", "10000"], max_output_chars=300)},
    ],
    verify='' + vhead(doc24_files) + '''
guide = files["作业/保养指导书.md"]
assert "首保：新车 5000 公里或 6 个月" in guide
assert "常规保养：每 10000 公里或 12 个月" in guide
''' + echo(["5000 公里", "5000公里", "5000", "10000 公里", "10000公里", "每 10000 公里", "10000"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的指导书作答：常规保养每 10000 公里或 12 个月；首保的 5000 公里是另一条。

## Reference solution
1. 第 1 轮读 作业/保养指导书.md：首保 5000 公里或 6 个月。终答一句话给出首保里程与依据。
第 2 轮零调用：同一份指导书写明常规保养每 10000 公里或 12 个月。终答一句话，例如「常规保养每 10000 公里或 12 个月做一次，指导书里和首保是分开两条。」判据：第 1 轮含 5000；第 2 轮零调用并含 10000 公里。

## Why the answer is unique
指导书里首保与常规保养分列两条，间隔各只有一个值；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8025
doc25_files = {
    "制度/交车时效承诺.md": "# 交车时效承诺\n\n## 时限\n- 保养与小修：当日 17:30 前交车。\n- 钣喷单：3 个工作日交车。\n- 加急单：次日交车，加收工时费 25%。\n\n## 顺延\n- 等件期间时效顺延，前台会提前告知。\n",
    "README.md": "# 峰驰汽修 服务承诺\n\n交车口径见 制度/交车时效承诺.md。\n",
}
write_case(
    "doc-8025",
    desc="Turn 1 reads the delivery-promise sheet for the panel-and-paint lead time; turn 2 forbids tools and asks the rush surcharge in the same sheet",
    task_type="policy_lookup", family="fam-doc-b10-turnaround-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc25_files,
    turns=[
        {"prompt": "峰驰汽修的钣喷单多久能交车？",
         "expect": {"output_contains_any": ["3 个工作日", "3个工作日"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具了，就按刚才读到的承诺说：加急单要加收多少？",
         "expect": dict(NOCALL, output_contains_any=["25%", "25％", "百分之二十五"], max_output_chars=300)},
    ],
    verify='' + vhead(doc25_files) + '''
sheet = files["制度/交车时效承诺.md"]
assert "钣喷单：3 个工作日交车" in sheet
assert "加收工时费 25%" in sheet
assert "当日 17:30 前交车" in sheet
''' + echo(["3 个工作日", "3个工作日", "25%", "25％", "百分之二十五"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的交车承诺作答：加急单加收工时费 25%；钣喷的 3 个工作日是另一条。

## Reference solution
1. 第 1 轮读 制度/交车时效承诺.md：钣喷单 3 个工作日交车。终答一句话给出时限与依据。
第 2 轮零调用：同一份承诺写明加急单次日交车、加收工时费 25%。终答一句话，例如「加急要加收 25% 的工时费，可以次日交车。」判据：第 1 轮含 3 个工作日；第 2 轮零调用并含 25%。

## Why the answer is unique
承诺里保养小修、钣喷、加急分列三条，时限与加收比例各只有一个值；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8026
doc26_files = {
    "制度/代步车借用须知.md": "# 代步车借用须知\n\n- 借用上限：每次 3 天。\n- 押金：500 元，还车时无损坏全额退还。\n- 用车范围：市内，跨市需报服务台批准。\n- 还车油量：不低于借出时油量。\n",
    "README.md": "# 国顺汽修 服务制度\n\n代步车管理见 制度/代步车借用须知.md。\n",
}
write_case(
    "doc-8026",
    desc="Turn 1 reads the courtesy-car notice for the borrowing cap; turn 2 forbids tools and asks the deposit in the same notice",
    task_type="policy_lookup", family="fam-doc-b10-courtesyrules-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc26_files,
    turns=[
        {"prompt": "国顺汽修的代步车一次最多能借几天？",
         "expect": {"output_contains_any": ["3 天", "3天", "三天"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别动工具，就按刚才读到的借用须知说：借代步车要交多少押金？",
         "expect": dict(NOCALL, output_contains_any=["500 元", "500元", "500"], max_output_chars=300)},
    ],
    verify='' + vhead(doc26_files) + '''
notice = files["制度/代步车借用须知.md"]
assert "借用上限：每次 3 天" in notice
assert "押金：500 元" in notice
assert "跨市需报服务台批准" in notice
''' + echo(["3 天", "3天", "三天", "500 元", "500元", "500"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的借用须知作答：押金 500 元；借用的 3 天是另一条。

## Reference solution
1. 第 1 轮读 制度/代步车借用须知.md：每次借用上限 3 天。终答一句话给出天数与依据。
第 2 轮零调用：同一份须知写明押金 500 元、无损坏全额退还。终答一句话，例如「押金 500 元，还车没损坏会全额退，须知里写的。」判据：第 1 轮含 3 天（或三天）；第 2 轮零调用并含 500。

## Why the answer is unique
须知里借用上限与押金各只有一个值；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8027
doc27_files = {
    "承诺/安装服务承诺.md": "# 安装服务承诺\n\n- 预约响应：下单后 24 小时内联系。\n- 上门时限：预约时段前后 30 分钟。\n- 安装保用：安装项目保用 90 天。\n- 辅材：管卡、螺栓免费，支架按公示价。\n",
    "README.md": "# 初阳家电服务 服务承诺\n\n安装与维修承诺见 承诺/安装服务承诺.md。\n",
}
write_case(
    "doc-8027",
    desc="Turn 1 reads the installation pledge for the contact-back window; turn 2 forbids tools and asks the same pledge's workmanship cover",
    task_type="policy_lookup", family="fam-doc-b10-installpromise-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc27_files,
    turns=[
        {"prompt": "初阳家电下单装空调，多久会有人联系我？",
         "expect": {"output_contains_any": ["24 小时", "24小时", "24 个小时"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "先别调用工具，就按刚才读到的承诺说：安装保用期是多少天？",
         "expect": dict(NOCALL, output_contains_any=["90 天", "90天", "90"], max_output_chars=300)},
    ],
    verify='' + vhead(doc27_files) + '''
pledge = files["承诺/安装服务承诺.md"]
assert "下单后 24 小时内联系" in pledge
assert "安装项目保用 90 天" in pledge
assert "前后 30 分钟" in pledge
''' + echo(["24 小时", "24小时", "24 个小时", "90 天", "90天", "90"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的承诺作答：安装保用 90 天；24 小时是响应时限，不是保用期。

## Reference solution
1. 第 1 轮读 承诺/安装服务承诺.md：下单后 24 小时内联系。终答一句话给出时限与依据。
第 2 轮零调用：同一份承诺写明安装项目保用 90 天。终答一句话，例如「安装保用 90 天，承诺里单独列了一条。」判据：第 1 轮含 24 小时；第 2 轮零调用并含 90 天。

## Why the answer is unique
承诺里响应时限与保用期各只有一个值，上门时限的 30 分钟是另一条；第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8028
doc28_files = {
    "条款/配件质保条款.md": "# 配件质保条款\n\n- 原厂件：质保 12 个月或 2 万公里，先到为准。\n- 品牌副厂件：质保 6 个月或 1 万公里。\n- 油液类：开封后不退不换。\n\n## 索赔\n- 凭工单与付款记录到前台登记。\n",
    "README.md": "# 临海汽修 配件条款\n\n质保口径见 条款/配件质保条款.md。\n",
}
write_case(
    "doc-8028",
    desc="Turn 1 reads the parts-warranty clause for OEM parts; turn 2 forbids tools and asks the aftermarket term in the same clause",
    task_type="policy_lookup", family="fam-doc-b10-partsclause-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc28_files,
    turns=[
        {"prompt": "临海汽修的原厂配件质保多久？",
         "expect": {"output_contains_any": ["12 个月", "12个月", "一年", "2 万公里"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不要调用工具，就按刚才读到的条款说：品牌副厂件质保多久？",
         "expect": dict(NOCALL, output_contains_any=["6 个月", "6个月", "半年", "1 万公里"], max_output_chars=300)},
    ],
    verify='' + vhead(doc28_files) + '''
clause = files["条款/配件质保条款.md"]
assert "原厂件：质保 12 个月或 2 万公里" in clause
assert "品牌副厂件：质保 6 个月或 1 万公里" in clause
assert "开封后不退不换" in clause
''' + echo(["12 个月", "12个月", "一年", "2 万公里", "6 个月", "6个月", "半年", "1 万公里"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的条款作答：品牌副厂件 6 个月或 1 万公里；原厂件的 12 个月是另一条。

## Reference solution
1. 第 1 轮读 条款/配件质保条款.md：原厂件质保 12 个月或 2 万公里，先到为准。终答一句话给出条款与依据。
第 2 轮零调用：同一份条款写明品牌副厂件质保 6 个月或 1 万公里。终答一句话，例如「副厂件短一些，质保 6 个月或 1 万公里。」判据：第 1 轮含 12 个月（或 2 万公里）；第 2 轮零调用并含 6 个月（或 1 万公里）。

## Why the answer is unique
条款里原厂件与副厂件分列两条，期限各只有一个值；油液类那条与期限无关。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8029
doc29_files = {
    "流程/退换机流程.md": "# 退换机流程\n\n## 期限\n- 退货：签收后 7 天内，外观与附件齐全。\n- 换机：签收后 15 天内，同一型号。\n- 折旧：超期按每天千分之五计。\n\n## 办理\n- 凭发票与包修卡到原购买门店办理。\n",
    "README.md": "# 若邻家电 售后流程\n\n退换口径见 流程/退换机流程.md。\n",
}
write_case(
    "doc-8029",
    desc="Turn 1 reads the return-and-swap flow for the return window; turn 2 forbids tools and asks the swap window in the same flow",
    task_type="policy_lookup", family="fam-doc-b10-swapwindow-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc29_files,
    turns=[
        {"prompt": "若邻家电买的冰箱几天内可以退？",
         "expect": {"output_contains_any": ["7 天", "7天", "七天"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调工具了，就按刚才读到的流程说：换机的期限是几天？",
         "expect": dict(NOCALL, output_contains_any=["15 天", "15天", "十五天"], max_output_chars=300)},
    ],
    verify='' + vhead(doc29_files) + '''
flow = files["流程/退换机流程.md"]
assert "退货：签收后 7 天内" in flow
assert "换机：签收后 15 天内" in flow
assert "每天千分之五" in flow
''' + echo(["7 天", "7天", "七天", "15 天", "15天", "十五天"], zh=True),
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的流程作答：换机 15 天；退货的 7 天是另一条。

## Reference solution
1. 第 1 轮读 流程/退换机流程.md：签收后 7 天内可退货。终答一句话给出期限与依据。
第 2 轮零调用：同一份流程写明换机在签收后 15 天内、同一型号。终答一句话，例如「换机期限是 15 天，比退货的 7 天长。」判据：第 1 轮含 7 天（或七天）；第 2 轮零调用并含 15 天。

## Why the answer is unique
流程里退货与换机分列两条，期限各只有一个值；折旧条款不涉及期限起算。第 2 轮需要的信息已在第 1 轮读过的文件里，用户明确禁止再调工具。
''',
)

# ---------------------------------------------------------------- doc-8030
doc30_files = {
    "specs/paper-spec.md": "# House paper specs\n\n## Text stocks\n- House uncoated: 100 gsm, FSC mix.\n- House silk: 150 gsm, twin-wire.\n\n## Cover boards\n- House cover: 300 gsm, one-side cast coated.\n\n## Ordering\n- Anything below 80 gsm goes to the mill on special order.\n",
    "README.md": "Foolscap & Sons specification library. The paper spec sheet is authoritative.\n",
}
write_case(
    "doc-8030",
    desc="Turn 1 reads the paper spec for the house uncoated weight; turn 2 forbids tools and asks the house cover weight in the same sheet",
    task_type="policy_lookup", family="fam-doc-b10-mediaguide-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=doc30_files,
    turns=[
        {"prompt": "What's the grammage of Foolscap & Sons' house uncoated text stock?",
         "expect": {"output_contains_any": ["100 gsm", "100gsm", "100 g/m2", "100 g/m²"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "No more tool calls — from the spec sheet you already read: what's the house cover board's weight?",
         "expect": dict(NOCALL, output_contains_any=["300 gsm", "300gsm", "300 g/m2", "300 g/m²"], max_output_chars=300)},
    ],
    verify='' + vhead(doc30_files) + '''
spec = files["specs/paper-spec.md"]
assert "House uncoated: 100 gsm" in spec
assert "House cover: 300 gsm" in spec
assert "House silk: 150 gsm" in spec
''' + echo(["100 gsm", "100gsm", "100 g/m2", "100 g/m²", "300 gsm", "300gsm", "300 g/m2", "300 g/m²"], zh=False),
    notes='''
## Traps
- None. Turn 2 must be answered from the spec sheet read in turn 1: the house cover board is 300 gsm; the silk stock's 150 gsm is the other text stock.

## Reference solution
1. Turn 1: read specs/paper-spec.md: house uncoated is 100 gsm. Final answer in one sentence with the source.
Turn 2, no tool call: the same sheet lists house cover at 300 gsm. Final answer in one sentence. Criteria: turn 1 contains 100 gsm (any spelling); turn 2 is zero-call and contains 300 gsm.

## Why the answer is unique
The sheet lists one weight per stock, and the cover board has its own section; both lines were in the turn-1 read, and the user forbade more tool calls.
''',
)
