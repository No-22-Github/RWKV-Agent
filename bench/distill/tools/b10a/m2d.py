"""M2 (v1.4 §3.2) b10a batch D: 40 "absent data" cases (cfg/log/tab/doc/fs),
mirroring the b10 pilot shapes cfg-8002 (key not set, library default, near-name
decoy) and log-8001 (collection gap covering the whole window, unknown is not 0).

  cd bench/distill/tools/b10a && python3 m2d.py
"""
import random
import re
from common import revised

write_case = revised({'cfg-8023': '未设置说法加「都没有」「查不到」：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'cfg-8022': '未设置说法加「都没有」「查不到」（与 cfg-8023 共用词表）：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'cfg-8024': '未设置说法加「都没有」「查不到」（与 cfg-8023 共用词表）：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'cfg-8025': '未设置说法加「都没有」「查不到」（与 cfg-8023 共用词表）：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'cfg-8026': '未设置说法加「都没有」「查不到」（与 cfg-8023 共用词表）：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'cfg-8027': '未设置说法加「都没有」「查不到」（与 cfg-8023 共用词表）：S5 老师答「两份配置都没有均温延时秒这一项」被词表漏判。', 'log-8018': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'tab-8028': '去掉部分合计 74 的排除：老师给出「已导出 74 张，三里屯只到 20 日，是下限」，是 §4.1 的部分可答写法。', 'tab-8029': '鲜酵母合计改为任一写法（94500 / 94,500 / 94.5 公斤）：老师写 94,500 克被判挂；缺货说明改由逐条阅读把关。', 'tab-8030': '去掉部分合计 63 的排除：老师给出「已导出 63 只、蓝漾只到 12 日」，是部分可答写法。', 'tab-8032': '去掉部分合计 47 的排除：老师给出「logged 47, not the full month」，是部分可答写法。', 'tab-8033': 'press 8 合计改为任一写法（2486 / 2,486）：老师写 2,486 被判挂；故障说明改由逐条阅读把关。', 'fs-8019': '厂商名改判「ommer」：老师照索引写小写 sommer-ironer 被大小写误判。', 'log-8019': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8020': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8021': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8022': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8023': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8024': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8025': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8026': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。', 'log-8027': '去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。'})

NEG_ZH = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没"]
CFG_UNSET_ZH = ["没设", "没有设置", "未设置", "没有配置", "未配置", "没配置",
                "没有这一项", "没有这项", "没有这个键", "没有这个参数", "都没有", "查不到"]
CFG_UNSET_EN = ["not set", "isn't set", "not configured", "isn't configured", "not defined",
                "doesn't set", "does not set", "unset", "neither", "no entry for"]
LOG_GAP_ZH = ["中断", "暂停", "维护", "没有采集", "没有推送", "没有日志", "缺失", "空白", "没有记录",
              "停机", "无法确定", "无法统计", "没有任何记录", "一条记录都没有", "不会补传", "不补录"]
LOG_GAP_EN = ["gap", "not collected", "no logs", "not shipped", "not uploaded", "paused",
              "maintenance", "no records", "not recorded", "no entries", "blank", "missing from",
              "offline", "not backfilled", "can't be counted", "cannot be counted", "no count", "no lines"]
# A bare "0 次" / "0 times" would also hit "10 次" / "20 times" in a reply that
# quotes counts from outside the gap, so zero claims carry a leading space or
# a lead-in word.
LOG_EXC_ZH = [" 0 次", "共0次", "为0次", "是0次", "零次", "共 0", "为 0 次", "次数为 0", "次数是 0", " 0 条", "共0条"]
LOG_EXC_EN = [" 0 times", "zero times", "zero alarms", "zero warnings", "zero alerts", "zero stops",
              "count of 0", "count is 0", " 0 occurrences",
              " 0 faults", " 0 failures", " 0 errors", " 0 events", " 0 alerts", " 0 warnings",
              "logged 0", "recorded 0", "total is 0", "total of 0"]

# Builder-side guard mirroring bank/verify.go: the judged number must not appear
# as a standalone literal in any file, or the number+1 sabotage goes undetected.
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")

def guard_no_literal(files, value, tol=0.01):
    for path, text in files.items():
        for m in NUM_RE.finditer(text):
            s, e = m.start(), m.end()
            if s > 0 and (text[s - 1].isalnum() or text[s - 1] in "_."):
                continue
            if e < len(text) and (text[e].isalnum() or text[e] in "_."):
                continue
            try:
                v = float(m.group())
            except ValueError:
                continue
            assert abs(v - value) > tol, "answer %r collides with literal %r in %s" % (value, m.group(), path)

# Which file the sabotage hits first (bank/verify.go extOrder); verify.py must
# assert the first line of a file in this set.
EXT_ORDER = [".csv", ".tsv", ".txt", ".jsonl", ".log", ".json", ".yaml", ".yml", ".md"]

def _ext_rank(p):
    low = p.lower()
    for i, ext in enumerate(EXT_ORDER):
        if low.endswith(ext):
            return i
    return len(EXT_ORDER)

def sab_first(files):
    return sorted(files, key=lambda p: (_ext_rank(p), p))[0]

def check_guard(files, guarded):
    assert sab_first(files) in guarded, "sabotage hits %s, verify guards %s" % (sab_first(files), sorted(guarded))

WROTE = []

def W(*args, **kwargs):
    WROTE.append(args[0])
    return write_case(*args, **kwargs)

# ================================================================ cfg-8022
FILES_8022 = {
    "config/醒发柜.yaml": "设备: 醒发柜\n门店: 望京店\n设定温度℃: 32\n蒸汽时长秒: 12\n预热补偿℃: 8\n报警上限℃: 38\n",
    "config/门店覆盖/望京店.yaml": "门店: 望京店\n设定温度℃: 30\n蒸汽时长秒: 15\n",
    "docs/醒发柜参数.md": "# 醒发柜参数说明\n\n- 设定温度℃：醒发的目标温度。\n- 蒸汽时长秒：每次加湿的喷汽时长。\n- 预热补偿℃：开机预热阶段在设定温度之上额外加热的幅度，只作用于预热。\n- 回差℃：到达设定温度后允许的波动幅度，超出才重新加热。未设置时使用焙控控制板的内置回差，内置值随控制板固件版本变动，建议显式写进配置。\n- 报警上限℃：柜温超过该值时本地报警。\n",
    "README.md": "# 麦禾烘焙 设备参数仓库\n\n各门店设备参数在 config/ 下，门店差异放 config/门店覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8022, {"config/醒发柜.yaml", "config/门店覆盖/望京店.yaml"})
W(
    "cfg-8022",
    desc="Asks the proofing-cabinet hysteresis for a shop; neither the base nor the shop override sets it, the docs say the Bekon controller's built-in value applies, and the preheat compensation key is the decoy",
    task_type="read_effective", family="fam-cfg-b10-proofcabinet-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "8"},
    axes=["DEC", "OBS"],
    files=FILES_8022,
    turns=[{
        "prompt": "望京店的醒发柜最近醒发效果不稳定，店长让我核对一下它的回差设的是多少。",
        "expect": {
            "output_contains": ["回差", "焙控"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["回差是 8", "回差为 8", "回差是8", "回差为8", "回差 8℃", "回差按 8"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/醒发柜.yaml"].splitlines()[0] == "设备: 醒发柜"
assert files["config/门店覆盖/望京店.yaml"].splitlines()[0] == "门店: 望京店"
assert "回差" not in files["config/醒发柜.yaml"]
assert "回差" not in files["config/门店覆盖/望京店.yaml"]
doc = files["docs/醒发柜参数.md"].splitlines()
assert any("内置回差" in l and "固件" in l for l in doc)
assert any("预热补偿℃" in l and "预热" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/醒发柜.yaml 与 config/门店覆盖/望京店.yaml 都没有「回差℃」这一项；docs/醒发柜参数.md 写明未设置时使用焙控控制板的内置回差，内置值随控制板固件版本变动，仓库没有记录。
- TR-DECOY: config/醒发柜.yaml 里「预热补偿℃: 8」与回差同属温度项。参数说明写明它只作用于开机预热，把 8 当回差就是诱饵答案。

## Reference solution
1. 读 config/醒发柜.yaml：没有回差℃，只有相近的预热补偿℃ = 8。
2. 读 config/门店覆盖/望京店.yaml：只覆盖设定温度和蒸汽时长。
3. 读 docs/醒发柜参数.md：未设置时用焙控控制板的内置回差，随固件版本变动。
终答（2-4 句）：回差在基础配置和门店覆盖里都没设，生效的是焙控控制板的内置回差，仓库里没有记录这个内置值；配置里的预热补偿是预热阶段的幅度，不是回差。建议按 docs 的建议把回差显式写进配置，或先确认控制板固件版本再向厂家查内置值。判据：包含「回差」「焙控」和一个「没设/未设置」说法，不得把 8 当回差。

## Why the answer is unique
预热补偿℃ 只作用于开机预热，参数说明明确它与「超出才重新加热」的回差是两回事；两个配置文件里都没有回差这一项，docs 也只说随固件版本变动而没给数值，所以任何具体数值都是编造，唯一站得住的回答是说明没设、点名内置回差并给出下一步。
''',
)

# ================================================================ cfg-8023
FILES_8023 = {
    "config/风炉.yaml": "设备: 风炉\n门店: 三里屯店\n烤制温度℃: 175\n降温提醒分: 25\n",
    "config/门店覆盖/三里屯店.yaml": "门店: 三里屯店\n烤制温度℃: 170\n",
    "docs/风炉参数.md": "# 风炉参数说明\n\n- 烤制温度℃：常规档位的炉腔温度。\n- 降温提醒分：到点未出炉时提醒值班店的倒计时，与炉腔控制无关。\n- 均温延时秒：开门后风机重新全速运转前的延时。未设置时使用炉体自带程序的延时，程序随炉体机型版本不同，仓库里没有记录这个值，建议按机型向厂家函索后显式写入。\n",
    "README.md": "# 麦禾烘焙 设备参数仓库\n\n各门店设备参数在 config/ 下，门店差异放 config/门店覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8023, {"config/风炉.yaml", "config/门店覆盖/三里屯店.yaml"})
W(
    "cfg-8023",
    desc="Asks the oven fan equalisation delay for a shop; neither config sets it, the docs point at the oven body's built-in programme value, and the cool-down reminder minutes are the decoy",
    task_type="read_effective", family="fam-cfg-b10-ovencurve-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "25"},
    axes=["DEC", "OBS"],
    files=FILES_8023,
    turns=[{
        "prompt": "三里屯店反馈饼干边缘上色偏深，让我核对一下风炉的均温延时设的是多少。",
        "expect": {
            "output_contains": ["均温延时", "炉体"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["均温延时是 25", "均温延时为 25", "均温延时 25", "延时是 25 秒", "延时为 25 秒"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/风炉.yaml"].splitlines()[0] == "设备: 风炉"
assert files["config/门店覆盖/三里屯店.yaml"].splitlines()[0] == "门店: 三里屯店"
assert "均温延时" not in files["config/风炉.yaml"]
assert "均温延时" not in files["config/门店覆盖/三里屯店.yaml"]
doc = files["docs/风炉参数.md"].splitlines()
assert any("自带程序" in l and "机型版本" in l for l in doc)
assert any("降温提醒分" in l and "无关" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/风炉.yaml 与 config/门店覆盖/三里屯店.yaml 都没有「均温延时秒」；docs/风炉参数.md 写明未设置时使用炉体自带程序的延时，随机型版本不同，仓库没有记录。
- TR-DECOY: config/风炉.yaml 里「降温提醒分: 25」名字里也带延时语义。参数说明写明它是到点未出炉的提醒倒计时、与炉腔控制无关，把 25 当均温延时就是诱饵答案。

## Reference solution
1. 读 config/风炉.yaml：没有均温延时秒，只有降温提醒分 = 25。
2. 读 config/门店覆盖/三里屯店.yaml：只覆盖烤制温度。
3. 读 docs/风炉参数.md：未设置时用炉体自带程序的延时，随机型版本不同。
终答（2-4 句）：均温延时在基础配置和门店覆盖里都没设，生效的是炉体自带程序的延时，仓库里没有记录这个值；配置里的降温提醒是提醒倒计时，不是均温延时。建议按 docs 的建议向厂家函索该机型的延时后显式写进配置。判据：包含「均温延时」「炉体」和一个「没设/未设置」说法，不得把 25 当均温延时。

## Why the answer is unique
降温提醒分按参数说明与炉腔控制无关，语义是提醒而不是风机延时；两个配置里都没有均温延时这一项，docs 没有给出任何数值，所以报 25 或任何数都是张冠李戴，唯一正确的是说明没设并给出向厂家函索的下一步。
''',
)

# ================================================================ cfg-8024
FILES_8024 = {
    "config/面团冷藏柜.yaml": "设备: 面团冷藏柜\n库位: 中央工厂一楼\n柜温℃: 4\n报警回调分: 40\n",
    "config/门店覆盖/中央工厂.yaml": "库位: 中央工厂一楼\n柜温℃: 3\n",
    "docs/面团冷藏柜参数.md": "# 面团冷藏柜参数说明\n\n- 柜温℃：冷藏目标温度。\n- 报警回调分：报警恢复后延迟再通知的等待时间，与制冷逻辑无关。\n- 冷藏回调分：压缩机停机后等待多久允许再次启动。未设置时使用制冷模块的内置回调时间，内置值随模块固件版本不同，仓库里没有记录，建议显式写进配置。\n",
    "README.md": "# 麦禾烘焙 设备参数仓库\n\n各门店与中央工厂的设备参数在 config/ 下，差异放 config/门店覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8024, {"config/面团冷藏柜.yaml", "config/门店覆盖/中央工厂.yaml"})
W(
    "cfg-8024",
    desc="Asks the dough chiller compressor restart delay; neither config sets it, the docs point at the refrigeration module's built-in value, and the alarm call-back minutes are the decoy",
    task_type="read_effective", family="fam-cfg-b10-doughchill-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "40"},
    axes=["DEC", "OBS"],
    files=FILES_8024,
    turns=[{
        "prompt": "中央工厂的面团冷藏柜压缩机启停太频繁，师傅让我先确认它的冷藏回调分设的是多少。",
        "expect": {
            "output_contains": ["冷藏回调", "制冷模块"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["冷藏回调是 40", "冷藏回调为 40", "冷藏回调 40", "冷藏回调分 40"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/面团冷藏柜.yaml"].splitlines()[0] == "设备: 面团冷藏柜"
assert files["config/门店覆盖/中央工厂.yaml"].splitlines()[0] == "库位: 中央工厂一楼"
assert "冷藏回调" not in files["config/面团冷藏柜.yaml"]
assert "冷藏回调" not in files["config/门店覆盖/中央工厂.yaml"]
doc = files["docs/面团冷藏柜参数.md"].splitlines()
assert any("内置回调" in l and "固件版本" in l for l in doc)
assert any("报警回调分" in l and "无关" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/面团冷藏柜.yaml 与 config/门店覆盖/中央工厂.yaml 都没有「冷藏回调分」；docs/面团冷藏柜参数.md 写明未设置时使用制冷模块的内置回调时间，随模块固件版本不同。
- TR-DECOY: config/面团冷藏柜.yaml 里「报警回调分: 40」名字里同样带「回调」。参数说明写明它是报警恢复后的延迟通知时间、与制冷逻辑无关，把 40 当冷藏回调就是诱饵答案。

## Reference solution
1. 读 config/面团冷藏柜.yaml：没有冷藏回调分，只有报警回调分 = 40。
2. 读 config/门店覆盖/中央工厂.yaml：只覆盖柜温。
3. 读 docs/面团冷藏柜参数.md：未设置时用制冷模块的内置回调时间，随固件版本不同。
终答（2-4 句）：冷藏回调在基础配置和覆盖文件里都没设，生效的是制冷模块的内置回调时间，仓库里没有记录这个值；配置里的报警回调是报警恢复后的延迟通知，不是压缩机启动回调。建议把冷藏回调分显式写进配置，或先确认制冷模块固件版本再查内置值。判据：包含「冷藏回调」「制冷模块」和一个「没设/未设置」说法，不得把 40 当冷藏回调。

## Why the answer is unique
报警回调分按参数说明与制冷逻辑无关；两个配置文件里都没有冷藏回调这一项，docs 没有给出数值，所以任何具体分钟数都是编造，唯一正确的是说明没设并给出显式配置或查固件的下一步。
''',
)

# ================================================================ cfg-8025
FILES_8025 = {
    "config/RO-400.yaml": "设备: 厨下反渗透机\n型号: RO-400\n进水压力兆帕: 0.28\n冲洗时长秒: 90\n",
    "config/网点覆盖/龙泉苑.yaml": "网点: 龙泉苑\n进水压力兆帕: 0.30\n",
    "docs/RO-400参数.md": "# RO-400 参数说明\n\n- 进水压力兆帕：进水压力的下限保护值。\n- 冲洗时长秒：每次冲洗阀打开的持续时长。\n- 冲洗间隔小时：两次自动冲洗之间的间隔。未设置时按冲洗阀的内置间隔执行，内置值随阀体固件版本不同，仓库和覆盖里都没有记录，建议显式设置或向阀体厂家确认所用批次。\n",
    "README.md": "# 澄泉净水 网点设备参数仓库\n\n各网点设备参数在 config/ 下，网点差异放 config/网点覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8025, {"config/RO-400.yaml", "config/网点覆盖/龙泉苑.yaml"})
W(
    "cfg-8025",
    desc="Asks the RO unit's rinse interval; neither the base nor the site override sets it, the docs point at the rinse valve's built-in interval, and the rinse duration seconds are the decoy",
    task_type="read_effective", family="fam-cfg-b10-rinsevalve-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "90"},
    axes=["DEC", "OBS"],
    files=FILES_8025,
    turns=[{
        "prompt": "龙泉苑那台 RO-400 的用户反映机器夜里频繁启动，我要先确认它的冲洗间隔设的是多少。",
        "expect": {
            "output_contains": ["冲洗间隔", "阀体"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["间隔是 90", "间隔为 90", "冲洗间隔 90", "冲洗间隔是 90", "冲洗间隔为 90"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/RO-400.yaml"].splitlines()[0] == "设备: 厨下反渗透机"
assert files["config/网点覆盖/龙泉苑.yaml"].splitlines()[0] == "网点: 龙泉苑"
assert "冲洗间隔" not in files["config/RO-400.yaml"]
assert "冲洗间隔" not in files["config/网点覆盖/龙泉苑.yaml"]
doc = files["docs/RO-400参数.md"].splitlines()
assert any("内置间隔" in l and "固件版本" in l for l in doc)
assert any("冲洗时长秒" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/RO-400.yaml 与 config/网点覆盖/龙泉苑.yaml 都没有「冲洗间隔小时」；docs/RO-400参数.md 写明未设置时按冲洗阀的内置间隔执行，随阀体固件版本不同。
- TR-DECOY: config/RO-400.yaml 里「冲洗时长秒: 90」名字同样带「冲洗」。参数说明写明它是每次冲洗的持续时长，不是两次冲洗的间隔，把 90 当冲洗间隔就是诱饵答案。

## Reference solution
1. 读 config/RO-400.yaml：没有冲洗间隔小时，只有冲洗时长秒 = 90。
2. 读 config/网点覆盖/龙泉苑.yaml：只覆盖进水压力。
3. 读 docs/RO-400参数.md：未设置时按冲洗阀内置间隔执行，随固件版本不同。
终答（2-4 句）：冲洗间隔在基础配置和网点覆盖里都没设，生效的是冲洗阀的内置间隔，仓库里没有记录这个值；配置里的冲洗时长是每次冲洗的持续秒数，不是间隔。建议把冲洗间隔显式写进配置，或按阀体批次向厂家确认内置值。判据：包含「冲洗间隔」「阀体」和一个「没设/未设置」说法，不得把 90 当冲洗间隔。

## Why the answer is unique
冲洗时长秒按参数说明是冲洗持续时长，与「两次冲洗之间的间隔」是两个键；两个配置文件里都没有冲洗间隔这一项，docs 没有给出数值，所以报 90 或任何数都是编造，唯一正确的是说明没设并给出下一步。
''',
)

# ================================================================ cfg-8026
FILES_8026 = {
    "config/软水机.yaml": "设备: 中央软水机\n型号: RS-800\n出水硬度目标: 4\n再生周期天: 6\n",
    "config/网点覆盖/清晏园.yaml": "网点: 清晏园\n出水硬度目标: 3\n",
    "docs/软水机参数.md": "# 软水机参数说明\n\n- 出水硬度目标：制水硬度的目标值。\n- 再生周期天：定时再生的间隔天数。\n- 再生启动硬度：出水硬度超过该值时在定时再生之外提前再生。未设置时由软水阀的自学习模式决定提前再生的启动点，自学习算法随阀体固件版本不同，仓库里没有记录，建议显式设置。\n",
    "README.md": "# 澄泉净水 网点设备参数仓库\n\n各网点设备参数在 config/ 下，网点差异放 config/网点覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8026, {"config/软水机.yaml", "config/网点覆盖/清晏园.yaml"})
W(
    "cfg-8026",
    desc="Asks the softener's early-regeneration hardness trigger; neither config sets it, the docs say the valve's self-learning mode decides, and the fixed regeneration period days are the decoy",
    task_type="read_effective", family="fam-cfg-b10-softenvalve-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "6"},
    axes=["DEC", "OBS"],
    files=FILES_8026,
    turns=[{
        "prompt": "清晏园的物业问中央软水机什么情况会提前再生，也就是再生启动硬度设的多少，帮我查一下。",
        "expect": {
            "output_contains": ["再生启动硬度", "自学习"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["硬度是 6", "硬度为 6", "启动硬度 6", "启动硬度是 6", "启动硬度为 6"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/软水机.yaml"].splitlines()[0] == "设备: 中央软水机"
assert files["config/网点覆盖/清晏园.yaml"].splitlines()[0] == "网点: 清晏园"
assert "再生启动硬度" not in files["config/软水机.yaml"]
assert "再生启动硬度" not in files["config/网点覆盖/清晏园.yaml"]
doc = files["docs/软水机参数.md"].splitlines()
assert any("自学习" in l and "固件版本" in l for l in doc)
assert any("再生周期天" in l and "定时" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/软水机.yaml 与 config/网点覆盖/清晏园.yaml 都没有「再生启动硬度」；docs/软水机参数.md 写明未设置时由软水阀的自学习模式决定提前再生的启动点，算法随阀体固件版本不同。
- TR-DECOY: config/软水机.yaml 里「再生周期天: 6」同样属于再生逻辑。参数说明写明它是定时再生的间隔天数，与硬度触发的提前再生是两个机制，把 6 当启动硬度就是诱饵答案。

## Reference solution
1. 读 config/软水机.yaml：没有再生启动硬度，只有再生周期天 = 6。
2. 读 config/网点覆盖/清晏园.yaml：只覆盖出水硬度目标。
3. 读 docs/软水机参数.md：未设置时由软水阀自学习模式决定，随固件版本不同。
终答（2-4 句）：再生启动硬度在基础配置和网点覆盖里都没设，提前再生的启动点由软水阀的自学习模式决定，仓库里没有记录这个值；配置里的再生周期天是定时再生的间隔，不是硬度触发值。建议把再生启动硬度显式写进配置，或按阀体固件版本向厂家确认。判据：包含「再生启动硬度」「自学习」和一个「没设/未设置」说法，不得把 6 当启动硬度。

## Why the answer is unique
再生周期天按参数说明是定时再生的间隔，与「硬度超过该值时提前再生」是两个机制；两个配置文件里都没有再生启动硬度这一项，docs 没有给出数值，自学习模式的具体行为仓库也不掌握，所以任何数值都是编造，唯一正确的是说明没设并给出下一步。
''',
)

# ================================================================ cfg-8027
FILES_8027 = {
    "config/管线机.yaml": "设备: 管线机\n型号: GX-2\n加热温度℃: 95\n保温时长分: 30\n",
    "config/网点覆盖/滨湖小学.yaml": "网点: 滨湖小学\n加热温度℃: 92\n",
    "docs/管线机参数.md": "# 管线机参数说明\n\n- 加热温度℃：出水的加热目标温度。\n- 保温时长分：加热完成后保温的时长。\n- UV 延时秒：出水停止后紫外灯继续照射的延时。未设置时按主板的内置延时执行，主板固件各批次不同，仓库里没有记录，建议显式设置。\n",
    "README.md": "# 澄泉净水 网点设备参数仓库\n\n各网点设备参数在 config/ 下，网点差异放 config/网点覆盖/，参数含义见 docs/。\n",
}
check_guard(FILES_8027, {"config/管线机.yaml", "config/网点覆盖/滨湖小学.yaml"})
W(
    "cfg-8027",
    desc="Asks the water dispenser's UV post-exposure delay; neither config sets it, the docs point at the mainboard's built-in delay, and the keep-warm minutes are the decoy",
    task_type="read_effective", family="fam-cfg-b10-uvdelay-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "30"},
    axes=["DEC", "OBS"],
    files=FILES_8027,
    turns=[{
        "prompt": "滨湖小学的管线机要做饮水安全检查，需要确认它的 UV 延时设的是多少。",
        "expect": {
            "output_contains": ["UV 延时", "主板"],
            "output_contains_any": CFG_UNSET_ZH,
            "output_excludes": ["UV 延时是 30", "UV 延时为 30", "UV 延时 30", "延时是 30 秒", "延时为 30 秒"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["config/管线机.yaml"].splitlines()[0] == "设备: 管线机"
assert files["config/网点覆盖/滨湖小学.yaml"].splitlines()[0] == "网点: 滨湖小学"
assert "UV 延时" not in files["config/管线机.yaml"]
assert "UV 延时" not in files["config/网点覆盖/滨湖小学.yaml"]
doc = files["docs/管线机参数.md"].splitlines()
assert any("内置延时" in l and "固件" in l for l in doc)
assert any("保温时长分" in l and "保温" in l for l in doc)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (CFG_UNSET_ZH,),
    notes='''
## Traps
- TR-ABSENT: config/管线机.yaml 与 config/网点覆盖/滨湖小学.yaml 都没有「UV 延时秒」；docs/管线机参数.md 写明未设置时按主板的内置延时执行，主板固件各批次不同。
- TR-DECOY: config/管线机.yaml 里「保温时长分: 30」同样带时长语义。参数说明写明它是加热后的保温时长，与紫外灯延时无关，把 30 当 UV 延时就是诱饵答案。

## Reference solution
1. 读 config/管线机.yaml：没有 UV 延时秒，只有保温时长分 = 30。
2. 读 config/网点覆盖/滨湖小学.yaml：只覆盖加热温度。
3. 读 docs/管线机参数.md：未设置时按主板内置延时执行，随固件批次不同。
终答（2-4 句）：UV 延时在基础配置和网点覆盖里都没设，生效的是主板的内置延时，仓库里没有记录这个值；配置里的保温时长是加热后的保温时间，不是紫外灯延时。建议把 UV 延时显式写进配置，或按主板批次向厂家确认内置值后再应对检查。判据：包含「UV 延时」「主板」和一个「没设/未设置」说法，不得把 30 当 UV 延时。

## Why the answer is unique
保温时长分按参数说明是加热后的保温时间，与「出水停止后紫外灯继续照射的延时」无关；两个配置文件里都没有 UV 延时这一项，docs 没有给出数值，所以报 30 或任何数都是编造，唯一正确的是说明没设并给出显式设置或查主板的下一步。
''',
)

# ================================================================ cfg-8028
FILES_8028 = {
    "config/tunnel-2.toml": '[tunnel]\nline = "tunnel-2"\nload_belt_speed_m_min = 18\nrinse_hold_s = 40\n\n[press]\ndwell_s = 12\n',
    "config/env/production.toml": "[tunnel]\nload_belt_speed_m_min = 16\n",
    "docs/tunnel-config.md": "# Tunnel 2 settings\n\n- load_belt_speed_m_min: conveyor speed through the wash modules.\n- rinse_hold_s: how long the last rinse chamber holds work while the drain cycles. Unrelated to extraction.\n- extract_ramp_s: ramp-up time of the extraction press before full pressure. When unset, the press uses the ramp built into its Hydromax PLC, and that built-in value changed between PLC firmware releases. Neither the base config nor the production override records it; pin it explicitly once the firmware version is confirmed.\n- press.dwell_s: time the press holds full pressure on each stroke.\n",
    "README.md": "Whitecrest Linen Services plant config. Machine settings live in config/; production overrides in config/env/.\n",
}
check_guard(FILES_8028, {"README.md"})
W(
    "cfg-8028",
    desc="Asks the tunnel washer's extraction ramp in production; neither the base nor the production config sets it, the docs say the Hydromax PLC built-in ramp applies, and the rinse hold seconds are the decoy",
    task_type="read_effective", family="fam-cfg-b10-tunnelwash-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "40"},
    axes=["DEC", "OBS"],
    files=FILES_8028,
    turns=[{
        "prompt": "Bath towels off tunnel 2 came out too wet last week, so I want to check the extraction ramp first. What is it set to in production?",
        "expect": {
            "output_contains": ["extract_ramp_s", "Hydromax"],
            "output_contains_any": CFG_UNSET_EN,
            "output_excludes": ["ramp is 40", "ramp of 40", "40-second ramp", "ramp is set to 40", "extract ramp is 40"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services plant config")
doc = files["docs/tunnel-config.md"].splitlines()
assert doc[0] == "# Tunnel 2 settings"
lib = [l for l in doc if l.startswith("- extract_ramp_s:")][0].split("built into its ")[1].split(" ")[0]
for path in ("config/tunnel-2.toml", "config/env/production.toml"):
    assert "extract_ramp_s" not in files[path]
print(json.dumps({"expected_string": lib}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/tunnel-2.toml nor config/env/production.toml sets extract_ramp_s. docs/tunnel-config.md says the unset value falls back to the ramp built into the Hydromax PLC, which changed between firmware releases.
- TR-DECOY: config/tunnel-2.toml has rinse_hold_s = 40. The docs state it is the rinse chamber hold during drain cycles and is unrelated to extraction; reporting a 40-second ramp is the decoy answer.

## Reference solution
1. Read config/tunnel-2.toml: no extract_ramp_s; only rinse_hold_s = 40 and press.dwell_s.
2. Read config/env/production.toml: overrides load_belt_speed_m_min only.
3. Read docs/tunnel-config.md: unset ramp means the Hydromax PLC built-in, which varies by firmware release.
Final answer (2-4 sentences): extract_ramp_s is not set in either the base config or the production override, so production runs on the ramp built into the Hydromax PLC, and the repo does not record what that is for the firmware you ship. The rinse_hold_s = 40 in the file is the rinse chamber hold, not the extraction ramp. Confirm the PLC firmware version or pin extract_ramp_s in config/env/production.toml as the docs recommend. Criteria: mentions extract_ramp_s and Hydromax plus a not-set phrase; must not present 40 as the ramp.

## Why the answer is unique
The only extraction-adjacent number in the config belongs to rinse_hold_s, which the docs explicitly separate from extraction. The ramp key appears in neither file, so the effective value is the PLC built-in, which the workspace does not contain; answering with any number would be invented.
''',
)

# ================================================================ cfg-8029
FILES_8029 = {
    "config/ironer-1.toml": '[ironer]\nline = "flatwork-1"\nsteam_pressure_bar = 6\ncooling_pause_s = 12\n',
    "config/env/production.toml": "[ironer]\nsteam_pressure_bar = 7\n",
    "docs/ironer-config.md": "# Flatwork ironer settings\n\n- steam_pressure_bar: steam supply pressure setpoint.\n- cooling_pause_s: pause between the last heated roll and the cooling roll. Unrelated to speed control.\n- dwell_adjust_pct: percentage speed adjustment applied while a seam passes through the rolls. When unset, the drive falls back to its on-board dwell handling, which changed between drive firmware versions; neither config file records it. Pin it explicitly for a consistent finish.\n",
    "README.md": "Whitecrest Linen Services flatwork line config. Ironer settings in config/ironer-1.toml; per-environment overrides in config/env/.\n",
}
check_guard(FILES_8029, {"README.md"})
W(
    "cfg-8029",
    desc="Asks the ironer's seam dwell adjust percentage; neither config sets it, the docs say the drive's on-board dwell handling applies, and the cooling pause seconds are the decoy",
    task_type="read_effective", family="fam-cfg-b10-ironerdwell-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "12"},
    axes=["DEC", "OBS"],
    files=FILES_8029,
    turns=[{
        "prompt": "Sheets have been finishing damp at the seams, and I want the ironer's dwell adjust value for the service visit. What is it in production?",
        "expect": {
            "output_contains": ["dwell_adjust_pct"],
            "output_contains_any": CFG_UNSET_EN,
            "output_excludes": ["adjust is 12", "adjust of 12", "12 percent adjust", "adjust is set to 12", "dwell adjust is 12"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services flatwork line config")
doc = files["docs/ironer-config.md"].splitlines()
assert doc[0] == "# Flatwork ironer settings"
lib = [l for l in doc if l.startswith("- dwell_adjust_pct:")][0].split("falls back to its ")[1].split(" ")[0]
for path in ("config/ironer-1.toml", "config/env/production.toml"):
    assert "dwell_adjust_pct" not in files[path]
assert lib == 'on-board'
print(json.dumps({"expected_string": 'dwell_adjust_pct'}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/ironer-1.toml nor config/env/production.toml sets dwell_adjust_pct. docs/ironer-config.md says the unset value falls back to the drive's on-board dwell handling, which changed between drive firmware versions.
- TR-DECOY: config/ironer-1.toml has cooling_pause_s = 12. The docs state it is the pause between the last heated roll and the cooling roll, unrelated to speed control; reporting a 12 percent adjust is the decoy answer.

## Reference solution
1. Read config/ironer-1.toml: no dwell_adjust_pct; only cooling_pause_s = 12.
2. Read config/env/production.toml: overrides steam_pressure_bar only.
3. Read docs/ironer-config.md: unset dwell adjust means the drive's on-board handling, which varies by firmware.
Final answer (2-4 sentences): dwell_adjust_pct is not set in either config file, so production runs on the drive's on-board dwell handling, and the repo does not record what that is for the drive firmware in service. The cooling_pause_s = 12 in the file is the roll-to-roll cooling pause, not the seam dwell adjust. Confirm the drive firmware version or pin dwell_adjust_pct in config/env/production.toml as the docs recommend. Criteria: mentions dwell_adjust_pct plus a not-set phrase; must not present 12 as the adjust.

## Why the answer is unique
cooling_pause_s is a roll sequencing pause per the docs, not a speed adjustment. The dwell adjust key appears in neither config, so the effective value is the drive's on-board handling, which the workspace does not contain; any percentage would be invented.
''',
)

# ================================================================ cfg-8030
FILES_8030 = {
    "config/dosing.toml": '[pump]\ncontroller = "doset-4"\nalkali_delay_s = 15\nsurfactant_strength_pct = 8\n',
    "config/env/production.toml": "[pump]\nsurfactant_strength_pct = 6\n",
    "docs/dosing-config.md": "# Dosing controller settings\n\n- surfactant_strength_pct: stock solution strength for the surfactant pump.\n- alkali_delay_s: delay between the alkali and detergent injectors on the same wheel. Unrelated to the surfactant pump.\n- surfactant_holdoff_s: wait after the wash valve opens before the surfactant pump may inject. When unset, the Doset-4 controller applies its internal holdoff, which differs between controller firmware revisions. Nothing in either config records the value; set it explicitly once the revision is confirmed.\n",
    "README.md": "Whitecrest Linen Services chemical dosing config. Pump settings in config/dosing.toml; per-environment overrides in config/env/.\n",
}
check_guard(FILES_8030, {"README.md"})
W(
    "cfg-8030",
    desc="Asks the surfactant pump holdoff in production; neither config sets it, the docs say the Doset-4 controller's internal holdoff applies, and the alkali delay seconds are the decoy",
    task_type="read_effective", family="fam-cfg-b10-dosehold-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "15"},
    axes=["DEC", "OBS"],
    files=FILES_8030,
    turns=[{
        "prompt": "Grease scores on shop towels have crept up, and the chemical vendor asked for the surfactant holdoff the controller runs with. What is it in production?",
        "expect": {
            "output_contains": ["surfactant_holdoff_s", "Doset-4"],
            "output_contains_any": CFG_UNSET_EN,
            "output_excludes": ["holdoff is 15", "holdoff of 15", "15-second holdoff", "holdoff is set to 15", "surfactant holdoff is 15"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services chemical dosing config")
doc = files["docs/dosing-config.md"].splitlines()
assert doc[0] == "# Dosing controller settings"
lib = [l for l in doc if l.startswith("- surfactant_holdoff_s:")][0].split("When unset, the ")[1].split(" ")[0]
for path in ("config/dosing.toml", "config/env/production.toml"):
    assert "surfactant_holdoff_s" not in files[path]
print(json.dumps({"expected_string": lib}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/dosing.toml nor config/env/production.toml sets surfactant_holdoff_s. docs/dosing-config.md says the unset value is the Doset-4 controller's internal holdoff, which differs between firmware revisions.
- TR-DECOY: config/dosing.toml has alkali_delay_s = 15. The docs state it is the delay between the alkali and detergent injectors, unrelated to the surfactant pump; reporting a 15-second surfactant holdoff is the decoy answer.

## Reference solution
1. Read config/dosing.toml: no surfactant_holdoff_s; only alkali_delay_s = 15 and the strength setting.
2. Read config/env/production.toml: overrides surfactant_strength_pct only.
3. Read docs/dosing-config.md: unset holdoff means the Doset-4 internal holdoff, which varies by firmware revision.
Final answer (2-4 sentences): surfactant_holdoff_s is not set in either the base config or the production override, so production runs on the Doset-4 controller's internal holdoff, and the repo does not record what that is for the firmware revision in service. The alkali_delay_s = 15 in the file belongs to the alkali and detergent injectors, not to the surfactant pump. Confirm the controller firmware revision or set surfactant_holdoff_s explicitly as the docs recommend. Criteria: mentions surfactant_holdoff_s and Doset-4 plus a not-set phrase; must not present 15 as the holdoff.

## Why the answer is unique
alkali_delay_s is documented as the injector-to-injector delay on a different chemical line. The holdoff key appears in neither config, so the effective value is the controller's internal one, which the workspace does not contain; any number would be invented.
''',
)

# ================================================================ cfg-8031
FILES_8031 = {
    "config/dryers.toml": '[dryer]\nbank = "dryers-east"\nreversing_s = 9\nanti_wrinkle_min = 20\n',
    "config/env/production.toml": "[dryer]\nreversing_s = 12\n",
    "docs/dryer-config.md": "# Dryer bank settings\n\n- reversing_s: interval between drum direction reversals.\n- anti_wrinkle_min: how long the drum tumbles without heat after the load finishes. Not part of the temperature programme.\n- cool_down_hold_min: minutes the door stays locked while the load cools below the unload threshold. When unset, the dryer controller uses its built-in cool-down hold, which changed between controller firmware versions. Neither config file sets it; pin it explicitly or read it off the controller at the machine.\n",
    "README.md": "Whitecrest Linen Services dryer bank config. Bank settings in config/dryers.toml; per-environment overrides in config/env/.\n",
}
check_guard(FILES_8031, {"README.md"})
W(
    "cfg-8031",
    desc="Asks the dryer bank's cool-down door hold in production; neither config sets it, the docs say the controller's built-in hold applies, and the anti-wrinkle tumble minutes are the decoy",
    task_type="read_effective", family="fam-cfg-b10-dryercool-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "20"},
    axes=["DEC", "OBS"],
    files=FILES_8031,
    turns=[{
        "prompt": "An operator burnt a hand pulling a load on dryers-east, so I am collecting the cool-down hold the bank actually runs with. What is it in production?",
        "expect": {
            "output_contains": ["cool_down_hold_min"],
            "output_contains_any": CFG_UNSET_EN,
            "output_excludes": ["hold is 20", "hold of 20", "20-minute hold", "hold is set to 20", "cool-down hold is 20"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Whitecrest Linen Services dryer bank config")
doc = files["docs/dryer-config.md"].splitlines()
assert doc[0] == "# Dryer bank settings"
lib = [l for l in doc if l.startswith("- cool_down_hold_min:")][0].split("uses its ")[1].split(" ")[0]
for path in ("config/dryers.toml", "config/env/production.toml"):
    assert "cool_down_hold_min" not in files[path]
assert lib == 'built-in'
print(json.dumps({"expected_string": 'cool_down_hold_min'}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/dryers.toml nor config/env/production.toml sets cool_down_hold_min. docs/dryer-config.md says the unset value is the controller's built-in cool-down hold, which changed between controller firmware versions.
- TR-DECOY: config/dryers.toml has anti_wrinkle_min = 20. The docs state it is the heatless post-load tumble and is not part of the temperature programme; reporting a 20-minute cool-down hold is the decoy answer.

## Reference solution
1. Read config/dryers.toml: no cool_down_hold_min; only reversing_s and anti_wrinkle_min = 20.
2. Read config/env/production.toml: overrides reversing_s only.
3. Read docs/dryer-config.md: unset hold means the controller built-in, which varies by firmware version.
Final answer (2-4 sentences): cool_down_hold_min is not set in either the base config or the production override, so production runs on the controller's built-in cool-down hold, and the repo does not record what that is for the firmware in service. The anti_wrinkle_min = 20 in the file is the heatless tumble after the load finishes, not the locked-door cool-down. Confirm the controller firmware version or pin cool_down_hold_min in config/env/production.toml; the docs also allow reading it off the controller at the machine. Criteria: mentions cool_down_hold_min plus a not-set phrase; must not present 20 as the hold.

## Why the answer is unique
anti_wrinkle_min is documented as the post-load heatless tumble, not the door hold while the load cools. The hold key appears in neither config, so the effective value is the controller built-in, which the workspace does not contain; any number would be invented.
''',
)

print("cfg batch: %d cases" % len(WROTE))

# ---------------------------------------------------------------- log helper
def gap_log(seed, date, header, warn, info, pause, resume, pre, post, p_warn=0.45):
    """A log whose middle is missing: events up to pre[1], a pause line, a
    resume line stating the gap is not backfilled, then events from post[0].
    Returns (log_text, n_warn_before_gap). pause/resume are (minute, text)."""
    rng = random.Random(seed)
    events = []
    n_warn = [0]

    def span(a, b):
        minute = a
        while minute < b:
            h, m = divmod(minute, 60)
            if rng.random() < p_warn:
                n_warn[0] += 1
                events.append((h, m, rng.randint(0, 59), warn(rng)))
            else:
                events.append((h, m, rng.randint(0, 59), info(rng)))
            minute += rng.randint(2, 4)

    span(*pre)
    events.append((pause[0] // 60, pause[0] % 60, rng.randint(0, 9), pause[1]))
    events.append((resume[0] // 60, resume[0] % 60, rng.randint(10, 30), resume[1]))
    span(*post)
    events.sort(key=lambda e: (e[0], e[1], e[2]))
    lines = [header]
    for h, m, s, msg in events:
        lines.append("%sT%02d:%02d:%02d+08:00 %s" % (date, h, m, s, msg))
    return "\n".join(lines) + "\n", n_warn[0]

def log_verify(log_path, header, date, w0, w1, pause_kw, resume_kw, words):
    return '''import json
import re

case = json.load(open("case.json"))
log = case["files"][%r].splitlines()
assert log[0].startswith(%r)
stamps = [re.match(r"%sT(\\d\\d):(\\d\\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
assert not any(%d <= x < %d for x in minutes)
assert any(%r in l for l in log) and any(%r in l for l in log)
words = %r
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''' % (log_path, header, date, w0, w1, pause_kw, resume_kw, words)

def log_notes(trap_lines, steps, answer, why, ref):
    return ("## Traps\n" + trap_lines + "\n\n## Reference solution\n" + steps
            + answer + "\n\n## Why the answer is unique\n" + why) % ref

# ---------------------------------------------------------------- log-8018
text, n_pre = gap_log(
    80181, "2026-09-12",
    "# 醒发间温湿度记录，仪器 TH-2A，时间为北京时间",
    warn=lambda r: "WARN 温度超限 摄氏 %.1f 度，已提醒当班" % (33 + r.random() * 3),
    info=lambda r: "INFO 湿度百分之 %d，正常" % r.randint(58, 70),
    pause=(115, "INFO 记录仪：进入校准程序，暂停记录"),
    resume=(230, "INFO 记录仪：校准完成，恢复记录；01:55 至 03:50 之间没有记录，也不会补录"),
    pre=(3, 113), post=(232, 280))
FILES_8018 = {
    "logs/醒发间/2026-09-12.log": text,
    "运维/记录仪说明.md": "# 记录仪采集说明\n\n醒发间温湿度记录仪每 2 分钟写一条到 logs/。校准或断电期间暂停记录，暂停时段的数据不会补录；原始数据在记录仪内部存储保留 30 天，可用 U 盘导出。\n",
    "README.md": "# 麦禾烘焙 中央工厂\n\nlogs/醒发间/ 按天存放温湿度记录。\n",
}
check_guard(FILES_8018, {"logs/醒发间/2026-09-12.log"})
W(
    "log-8018",
    desc="Asks how many temperature overruns the proofing room logged between 02:00 and 03:00; the logger paused for calibration covering that hour and states the gap is not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-fermentgap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8018,
    turns=[{
        "prompt": "9 月 12 日凌晨 2 点到 3 点，醒发间的温度超限了多少次？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/醒发间/2026-09-12.log", "# 醒发间温湿度记录", "2026-09-12",
                      120, 180, "暂停记录", "不会补录", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/醒发间/2026-09-12.log 在 01:55 记录「进入校准程序，暂停记录」，03:50 记录「校准完成，恢复记录；01:55 至 03:50 之间没有记录，也不会补录」。2 点到 3 点之间一行都没有，把「没有记录」读成「0 次超限」就是诱饵答案（0）。\n",
        "1. 读 logs/醒发间/2026-09-12.log：01:55 到 03:50 没有日志，且记录仪写明这段不补录。\n2. 读 运维/记录仪说明.md：校准期间不补录，原始数据在记录仪本机保留 30 天。\n",
        "终答（2-4 句）：2 点到 3 点这一段日志是空的——记录仪 01:55 起进入校准、03:50 才恢复，这段不会补录，所以没法统计超限次数，也不能当成零；原始数据在记录仪本机保留 30 天，可以从记录仪导出后再统计。（参考：暂停之前有 %d 条超限记录，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。\n",
        "诱饵 0 错在把「没有记录」当成「没有发生」：日志自己写明 01:55–03:50 没有记录且不补录，采集说明也确认暂停时段不补录。工作区里没有其他来源覆盖这一小时，所以次数无法确定，只能说明缺口并指向记录仪本机导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8019
text, n_pre = gap_log(
    80191, "2026-09-08",
    "# 望京店烤炉控制器日志，上传器每晚推送，时间为北京时间",
    warn=lambda r: "WARN E-07 门封温度异常，请检查门封条",
    info=lambda r: "INFO 预热完成 炉膛 %d℃" % r.randint(205, 218),
    pause=(1290, "INFO 上传器：门店网络改造，暂停推送"),
    resume=(1421, "INFO 上传器：恢复推送；21:30 至 23:41 的日志没有推送，也不会补传"),
    pre=(1142, 1288), post=(1423, 1439))
FILES_8019 = {
    "logs/烤炉/2026-09-08.log": text,
    "运维/日志推送说明.md": "# 日志推送说明\n\n门店烤炉日志由上传器推送到 logs/。门店网络维护或改造期间推送暂停，暂停时段的日志不会补传；原始日志在控制器本地保留 15 天，可从维护口导出。\n",
    "README.md": "# 麦禾烘焙 门店运维\n\nlogs/烤炉/ 按门店、按天存放烤炉控制器日志。\n",
}
check_guard(FILES_8019, {"logs/烤炉/2026-09-08.log"})
W(
    "log-8019",
    desc="Asks how many E-07 door-seal alarms the shop oven logged between 22:00 and 23:00; the uploader paused for a network refit covering that hour and states the lines are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-ovenerr-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8019,
    turns=[{
        "prompt": "望京店烤炉 9 月 8 日晚上 10 点到 11 点的 E-07 报错有多少次？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/烤炉/2026-09-08.log", "# 望京店烤炉控制器日志", "2026-09-08",
                      1320, 1380, "暂停推送", "不会补传", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/烤炉/2026-09-08.log 在 21:30 记录「门店网络改造，暂停推送」，23:41 记录「恢复推送；21:30 至 23:41 的日志没有推送，也不会补传」。22 点到 23 点之间一行都没有，把「没有记录」读成「0 次 E-07」就是诱饵答案（0）。\n",
        "1. 读 logs/烤炉/2026-09-08.log：21:30 到 23:41 没有日志，且上传器写明这段不补传。\n2. 读 运维/日志推送说明.md：网络改造期间推送暂停、不补传，原始日志在控制器本地保留 15 天。\n",
        "终答（2-4 句）：22 点到 23 点这一段日志是空的——上传器 21:30 起因门店网络改造暂停推送、23:41 才恢复，这段不会补传，所以没法统计 E-07 的次数，也不能当成零；原始日志在控制器本地保留 15 天，可以从维护口导出后再统计。（参考：暂停之前有 %d 条 E-07 记录，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。\n",
        "诱饵 0 错在把「没有推送」当成「没有发生」：日志自己写明 21:30–23:41 的行没有推送也不补传，推送说明也确认改造期间暂停。工作区里没有其他来源覆盖这一小时，所以次数无法确定，只能说明缺口并指向控制器本机导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8020
text, n_pre = gap_log(
    80201, "2026-09-03",
    "# 中央工厂出炉扫码日志，时间为北京时间",
    warn=lambda r: "WARN 漏扫告警 托盘 %d，需人工补录" % r.randint(40, 90),
    info=lambda r: "INFO 出炉扫码 ok 批次 B-%d" % r.randint(310, 360),
    pause=(892, "INFO 扫码枪：固件升级开始，暂停上传"),
    resume=(996, "INFO 扫码枪：固件升级完成，恢复上传；14:52 至 16:36 的记录没有上传，也不会补传"),
    pre=(782, 890), post=(998, 1050))
FILES_8020 = {
    "logs/出炉扫码/2026-09-03.log": text,
    "运维/设备日志说明.md": "# 设备日志说明\n\n出炉扫码枪日志上传到 logs/。固件升级或维护期间上传暂停，暂停时段的记录不会补传；原始记录在扫码枪本地保留 10 天，可用维护线缆导出。\n",
    "README.md": "# 麦禾烘焙 中央工厂\n\nlogs/出炉扫码/ 按天存放出炉扫码日志。\n",
}
check_guard(FILES_8020, {"logs/出炉扫码/2026-09-03.log"})
W(
    "log-8020",
    desc="Asks how many missed-scan alerts the despatch scanner logged between 15:00 and 16:00; the scanner paused for a firmware upgrade covering that hour and states the records are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-ovenscan-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8020,
    turns=[{
        "prompt": "9 月 3 日下午 3 点到 4 点，出炉扫码的漏扫告警有多少次？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/出炉扫码/2026-09-03.log", "# 中央工厂出炉扫码日志", "2026-09-03",
                      900, 960, "暂停上传", "不会补传", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/出炉扫码/2026-09-03.log 在 14:52 记录「固件升级开始，暂停上传」，16:36 记录「固件升级完成，恢复上传；14:52 至 16:36 的记录没有上传，也不会补传」。15 点到 16 点之间一行都没有，把「没有记录」读成「0 次漏扫」就是诱饵答案（0）。\n",
        "1. 读 logs/出炉扫码/2026-09-03.log：14:52 到 16:36 没有日志，且扫码枪写明这段不补传。\n2. 读 运维/设备日志说明.md：升级期间上传暂停、不补传，原始记录在扫码枪本地保留 10 天。\n",
        "终答（2-4 句）：15 点到 16 点这一段日志是空的——扫码枪 14:52 起固件升级暂停上传、16:36 才恢复，这段不会补传，所以没法统计漏扫告警次数，也不能当成零；原始记录在扫码枪本地保留 10 天，可以从设备导出后再统计。（参考：暂停之前有 %d 条漏扫告警，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。\n",
        "诱饵 0 错在把「没有上传」当成「没有发生」：日志自己写明 14:52–16:36 的记录没有上传也不补传，设备说明也确认升级期间暂停。工作区里没有其他来源覆盖这一小时，所以次数无法确定，只能说明缺口并指向设备本机导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8021
text, n_pre = gap_log(
    80211, "2026-09-15",
    "# 龙泉苑网点 TDS 探头日志，时间为北京时间",
    warn=lambda r: "WARN TDS 超标 %d mg/L，请安排换芯检查" % r.randint(95, 130),
    info=lambda r: "INFO TDS %d mg/L，正常" % r.randint(12, 40),
    pause=(48, "INFO 网关：更换电池，停机"),
    resume=(167, "INFO 网关：恢复上报；00:48 至 02:47 之间没有上报，也不会补传"),
    pre=(2, 46), post=(169, 220))
FILES_8021 = {
    "logs/tds/2026-09-15.log": text,
    "运维/网点日志说明.md": "# 网点日志说明\n\n网点 TDS 探头经网关上报到 logs/。网关停机或维护期间上报暂停，暂停时段的数据不会补传；原始数据在探头网关本地保留 20 天，可通过网关后台导出。\n",
    "README.md": "# 澄泉净水 网点日志\n\nlogs/tds/ 按网点、按天存放 TDS 探头日志。\n",
}
check_guard(FILES_8021, {"logs/tds/2026-09-15.log"})
W(
    "log-8021",
    desc="Asks how many TDS exceedances the site probe logged between 01:00 and 02:00; the gateway was down for a battery swap covering that hour and states the data is not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-tdsgap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8021,
    turns=[{
        "prompt": "龙泉苑的 TDS 探头 9 月 15 日凌晨 1 点到 2 点报了多少次超标？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/tds/2026-09-15.log", "# 龙泉苑网点 TDS 探头日志", "2026-09-15",
                      60, 120, "停机", "不会补传", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/tds/2026-09-15.log 在 00:48 记录「更换电池，停机」，02:47 记录「恢复上报；00:48 至 02:47 之间没有上报，也不会补传」。1 点到 2 点之间一行都没有，把「没有记录」读成「0 次超标」就是诱饵答案（0）。\n",
        "1. 读 logs/tds/2026-09-15.log：00:48 到 02:47 没有日志，且网关写明这段不补传。\n2. 读 运维/网点日志说明.md：停机期间上报暂停、不补传，原始数据在网关本地保留 20 天。\n",
        "终答（2-4 句）：1 点到 2 点这一段日志是空的——网关 00:48 起换电池停机、02:47 才恢复，这段不会补传，所以没法统计超标次数，也不能当成零；原始数据在网关本地保留 20 天，可以从网关后台导出后再统计。（参考：停机之前有 %d 次超标，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。\n",
        "诱饵 0 错在把「没有上报」当成「没有发生」：日志自己写明 00:48–02:47 之间没有上报也不补传，网点说明也确认停机期间暂停。工作区里没有其他来源覆盖这一小时，所以次数无法确定，只能说明缺口并指向网关本机导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8022
text, n_pre = gap_log(
    80221, "2026-09-20",
    "# 漏水告警平台日志，时间为北京时间",
    warn=lambda r: "WARN 漏水告警 网点 %s 探头 %d" % (r.choice(["龙泉苑", "清晏园", "滨湖小学"]), r.randint(1, 4)),
    info=lambda r: "INFO 心跳正常 在线 %d 台" % r.randint(38, 42),
    pause=(159, "INFO 平台：例行维护，暂停入库"),
    resume=(262, "INFO 平台：维护结束，恢复入库；02:39 至 04:22 的告警没有入库，也不会补传"),
    pre=(122, 157), post=(264, 320))
FILES_8022L = {
    "logs/告警平台/2026-09-20.log": text,
    "运维/平台维护说明.md": "# 平台维护说明\n\n告警平台日志按天写入 logs/。例行维护期间入库暂停，暂停时段的告警不会补录；原始告警在平台消息队列保留 7 天，可由管理员导出。\n",
    "README.md": "# 澄泉净水 告警平台\n\nlogs/告警平台/ 按天存放平台日志。\n",
}
check_guard(FILES_8022L, {"logs/告警平台/2026-09-20.log"})
W(
    "log-8022",
    desc="Asks how many leak alarms the platform ingested between 03:00 and 04:00; the platform paused for routine maintenance covering that hour and states the alarms are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-leakpause-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8022L,
    turns=[{
        "prompt": "9 月 20 日凌晨 3 点到 4 点，告警平台上新收到的漏水告警有多少条？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/告警平台/2026-09-20.log", "# 漏水告警平台日志", "2026-09-20",
                      180, 240, "暂停入库", "不会补传", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/告警平台/2026-09-20.log 在 02:39 记录「例行维护，暂停入库」，04:22 记录「维护结束，恢复入库；02:39 至 04:22 的告警没有入库，也不会补传」。3 点到 4 点之间一行都没有，把「没有记录」读成「0 条告警」就是诱饵答案（0）。\n",
        "1. 读 logs/告警平台/2026-09-20.log：02:39 到 04:22 没有日志，且平台写明这段不补录。\n2. 读 运维/平台维护说明.md：维护期间入库暂停、不补录，原始告警在平台消息队列保留 7 天。\n",
        "终答（2-4 句）：3 点到 4 点这一段日志是空的——平台 02:39 起例行维护暂停入库、04:22 才恢复，这段不会补录，所以没法统计新收到的告警条数，也不能当成零；原始告警在平台消息队列保留 7 天，可以让管理员导出后再统计。（参考：暂停之前有 %d 条告警，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 条。\n",
        "诱饵 0 错在把「没有入库」当成「没有发生」：日志自己写明 02:39–04:22 的告警没有入库也不补录，维护说明也确认维护期间暂停。工作区里没有其他来源覆盖这一小时，所以条数无法确定，只能说明缺口并指向消息队列导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8023
text, n_pre = gap_log(
    80231, "2026-09-26",
    "# 滤芯寿命上报日志，时间为北京时间",
    warn=lambda r: "WARN 滤芯到期提醒 机器 %s 滤芯 %s" % (r.choice(["RS-3102", "RS-3108", "RS-3115"]), r.choice(["PP 棉", "前置炭", "RO 膜"])),
    info=lambda r: "INFO 寿命上报 机器 %s 剩余 %d%%" % (r.choice(["RS-3102", "RS-3108", "RS-3115"]), r.randint(20, 90)),
    pause=(1196, "INFO 云平台：数据迁移，暂停接收"),
    resume=(1304, "INFO 云平台：迁移完成，恢复接收；19:56 至 21:44 的上报没有接收，也不会补传"),
    pre=(1172, 1194), post=(1306, 1350))
FILES_8023L = {
    "logs/滤芯寿命/2026-09-26.log": text,
    "运维/上报说明.md": "# 上报说明\n\n滤芯寿命上报经云平台写入 logs/。平台迁移或维护期间接收暂停，暂停时段的上报不会补传；原始上报在平台暂存区保留 5 天，可由管理员导出。\n",
    "README.md": "# 澄泉净水 云平台\n\nlogs/滤芯寿命/ 按天存放寿命上报日志。\n",
}
check_guard(FILES_8023L, {"logs/滤芯寿命/2026-09-26.log"})
W(
    "log-8023",
    desc="Asks how many filter expiry reminders the cloud platform received between 20:00 and 21:00; the platform paused for a data migration covering that hour and states the reports are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-filterlife-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8023L,
    turns=[{
        "prompt": "9 月 26 日晚上 8 点到 9 点，云平台收到了多少条滤芯到期提醒？",
        "expect": {
            "output_contains_any": LOG_GAP_ZH,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/滤芯寿命/2026-09-26.log", "# 滤芯寿命上报日志", "2026-09-26",
                      1200, 1260, "暂停接收", "不会补传", LOG_GAP_ZH),
    notes=log_notes(
        "- TR-ABSENT: logs/滤芯寿命/2026-09-26.log 在 19:56 记录「数据迁移，暂停接收」，21:44 记录「迁移完成，恢复接收；19:56 至 21:44 的上报没有接收，也不会补传」。20 点到 21 点之间一行都没有，把「没有记录」读成「0 条提醒」就是诱饵答案（0）。\n",
        "1. 读 logs/滤芯寿命/2026-09-26.log：19:56 到 21:44 没有日志，且平台写明这段不补传。\n2. 读 运维/上报说明.md：迁移期间接收暂停、不补传，原始上报在平台暂存区保留 5 天。\n",
        "终答（2-4 句）：20 点到 21 点这一段日志是空的——云平台 19:56 起数据迁移暂停接收、21:44 才恢复，这段不会补传，所以没法统计收到的提醒条数，也不能当成零；原始上报在平台暂存区保留 5 天，可以让管理员导出后再统计。（参考：暂停之前有 %d 条提醒，都在缺口之前。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 条。\n",
        "诱饵 0 错在把「没有接收」当成「没有发生」：日志自己写明 19:56–21:44 的上报没有接收也不补传，上报说明也确认迁移期间暂停。工作区里没有其他来源覆盖这一小时，所以条数无法确定，只能说明缺口并指向暂存区导出。\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8024
text, n_pre = gap_log(
    80241, "2026-09-18",
    "# tunnel-2 cycle log, exported by the plc-exporter, times local",
    warn=lambda r: "WARN high level alarm bath=rinse-3",
    info=lambda r: "INFO cycle %d ok program=%s" % (r.randint(400, 520), r.choice(["towels", "sheets"])),
    pause=(832, "INFO exporter: paused for the PLC firmware upgrade"),
    resume=(947, "INFO exporter: resumed; lines from 13:52 to 15:47 were not shipped and are not backfilled"),
    pre=(782, 830), post=(949, 1000))
FILES_8024L = {
    "logs/tunnel-2/2026-09-18.log": text,
    "ops/exporter-notes.md": "# Exporter notes\n\nThe plc-exporter ships cycle logs to logs/ every minute. During upgrades and maintenance windows the exporter pauses, and the lines in between are not backfilled; the raw log stays on the PLC for 14 days and can be pulled over the service port.\n",
    "README.md": "# Whitecrest Linen Services plant logs\n\nlogs/ holds per-machine, per-day logs.\n",
}
check_guard(FILES_8024L, {"logs/tunnel-2/2026-09-18.log"})
W(
    "log-8024",
    desc="Asks how many high level alarms tunnel 2 logged between 14:00 and 15:00; the exporter paused for a PLC firmware upgrade covering that hour and states the lines are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-washgap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8024L,
    turns=[{
        "prompt": "How many high level alarms did tunnel 2 log between 14:00 and 15:00 on Sep 18?",
        "expect": {
            "output_contains_any": LOG_GAP_EN,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/tunnel-2/2026-09-18.log", "# tunnel-2 cycle log", "2026-09-18",
                      840, 900, "paused", "not backfilled", LOG_GAP_EN),
    notes=log_notes(
        "- TR-ABSENT: logs/tunnel-2/2026-09-18.log records \"paused for the PLC firmware upgrade\" at 13:52 and \"resumed; lines from 13:52 to 15:47 were not shipped and are not backfilled\" at 15:47. There is no line at all between 14:00 and 15:00; reading the empty hour as 0 alarms is the decoy answer.\n",
        "1. Read logs/tunnel-2/2026-09-18.log: no lines between 13:52 and 15:47, and the exporter itself says the gap is not backfilled.\n2. Read ops/exporter-notes.md: the exporter pauses during upgrades, does not backfill, and the raw log stays on the PLC for 14 days.\n",
        "Final answer (2-4 sentences): the 14:00-15:00 stretch of the log is empty - the exporter paused for the PLC firmware upgrade at 13:52 and only resumed at 15:47, and that window is not backfilled, so the alarm count for the hour cannot be determined and must not be read as 0. The raw log stays on the PLC for 14 days; pull it over the service port to count the alarms. (Reference: %d high level alarms appear ahead of the pause.) Criteria: mentions the pause/gap and must not report 0 alarms.\n",
        "The decoy 0 mistakes \"not shipped\" for \"did not happen\": the log states the lines in the window were not shipped and are not backfilled, and the exporter notes confirm the same. No other source in the workspace covers the hour, so the count is unknowable and the only defensible reply names the gap and points at the PLC copy.\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8025
text, n_pre = gap_log(
    80251, "2026-09-05",
    "# dryers-east event log, gateway gw-3, times local",
    warn=lambda r: "WARN drum overheat warning bank=dryers-east",
    info=lambda r: "INFO load %d done minutes=%d" % (r.randint(900, 990), r.randint(38, 55)),
    pause=(1184, "INFO gateway: maintenance window, event upload paused"),
    resume=(1311, "INFO gateway: upload resumed; events from 19:44 to 21:51 were not uploaded and are not backfilled"),
    pre=(1162, 1182), post=(1313, 1360))
FILES_8025L = {
    "logs/dryers-east/2026-09-05.log": text,
    "ops/gateway-notes.md": "# Gateway notes\n\nDryer events reach logs/ through gateway gw-3. During maintenance windows the gateway pauses uploads and the events in between are not backfilled; the raw events stay on the gateway for 10 days and can be exported from its console.\n",
    "README.md": "# Whitecrest Linen Services plant logs\n\nlogs/ holds per-machine, per-day logs.\n",
}
check_guard(FILES_8025L, {"logs/dryers-east/2026-09-05.log"})
W(
    "log-8025",
    desc="Asks how many drum overheat warnings dryers-east logged between 20:00 and 21:00; the gateway paused uploads for a maintenance window covering that hour and states the events are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-dryerlog-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8025L,
    turns=[{
        "prompt": "How many drum overheat warnings did dryers-east log between 20:00 and 21:00 on Sep 5?",
        "expect": {
            "output_contains_any": LOG_GAP_EN,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/dryers-east/2026-09-05.log", "# dryers-east event log", "2026-09-05",
                      1200, 1260, "paused", "not backfilled", LOG_GAP_EN),
    notes=log_notes(
        "- TR-ABSENT: logs/dryers-east/2026-09-05.log records \"maintenance window, event upload paused\" at 19:44 and \"upload resumed; events from 19:44 to 21:51 were not uploaded and are not backfilled\" at 21:51. There is no line at all between 20:00 and 21:00; reading the empty hour as 0 warnings is the decoy answer.\n",
        "1. Read logs/dryers-east/2026-09-05.log: no lines between 19:44 and 21:51, and the gateway itself says the gap is not backfilled.\n2. Read ops/gateway-notes.md: uploads pause during maintenance windows, events are not backfilled, and the raw events stay on the gateway for 10 days.\n",
        "Final answer (2-4 sentences): the 20:00-21:00 stretch of the log is empty - gateway gw-3 paused uploads for its maintenance window at 19:44 and only resumed at 21:51, and that window is not backfilled, so the warning count for the hour cannot be determined and must not be read as 0. The raw events stay on the gateway for 10 days; export them from its console to get the count. (Reference: %d overheat warnings appear ahead of the pause.) Criteria: mentions the pause/gap and must not report 0 warnings.\n",
        "The decoy 0 mistakes \"not uploaded\" for \"did not happen\": the log states the events in the window were not uploaded and are not backfilled, and the gateway notes confirm the same. No other source in the workspace covers the hour, so the count is unknowable and the only defensible reply names the gap and points at the gateway copy.\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8026
text, n_pre = gap_log(
    80261, "2026-09-22",
    "# doset-4 dosing log, pump house 1, times local",
    warn=lambda r: "WARN refill alert tank=surfactant level=%d" % r.randint(8, 18),
    info=lambda r: "INFO dose cycle ok valve=%d" % r.randint(1, 6),
    pause=(341, "INFO logger: sd card swap, logging paused"),
    resume=(458, "INFO logger: sd card swapped; entries from 05:41 to 07:38 were not logged and are not backfilled"),
    pre=(302, 339), post=(460, 510))
FILES_8026L = {
    "logs/doset-4/2026-09-22.log": text,
    "ops/logger-notes.md": "# Logger notes\n\nThe Doset-4 dosing log reaches logs/ through the pump house logger. During sd card swaps and maintenance the logger pauses, and the entries in between are not backfilled; the card itself keeps the raw entries for 30 days and can be read out at the pump house.\n",
    "README.md": "# Whitecrest Linen Services plant logs\n\nlogs/ holds per-machine, per-day logs.\n",
}
check_guard(FILES_8026L, {"logs/doset-4/2026-09-22.log"})
W(
    "log-8026",
    desc="Asks how many refill alerts the dosing pump logged between 06:00 and 07:00; the logger paused for an sd card swap covering that hour and states the entries are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-dosegap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8026L,
    turns=[{
        "prompt": "How many refill alerts did the Doset-4 pump log between 06:00 and 07:00 on Sep 22?",
        "expect": {
            "output_contains_any": LOG_GAP_EN,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/doset-4/2026-09-22.log", "# doset-4 dosing log", "2026-09-22",
                      360, 420, "paused", "not backfilled", LOG_GAP_EN),
    notes=log_notes(
        "- TR-ABSENT: logs/doset-4/2026-09-22.log records \"sd card swap, logging paused\" at 05:41 and \"sd card swapped; entries from 05:41 to 07:38 were not logged and are not backfilled\" at 07:38. There is no line at all between 06:00 and 07:00; reading the empty hour as 0 alerts is the decoy answer.\n",
        "1. Read logs/doset-4/2026-09-22.log: no lines between 05:41 and 07:38, and the logger itself says the gap is not backfilled.\n2. Read ops/logger-notes.md: the logger pauses during sd swaps, does not backfill, and the card keeps the raw entries for 30 days.\n",
        "Final answer (2-4 sentences): the 06:00-07:00 stretch of the log is empty - the pump house logger paused for the sd card swap at 05:41 and only resumed at 07:38, and that window is not backfilled, so the alert count for the hour cannot be determined and must not be read as 0. The card keeps the raw entries for 30 days; read it out at the pump house to count the alerts. (Reference: %d refill alerts appear ahead of the pause.) Criteria: mentions the pause/gap and must not report 0 alerts.\n",
        "The decoy 0 mistakes \"not logged\" for \"did not happen\": the log states the entries in the window were not logged and are not backfilled, and the logger notes confirm the same. No other source in the workspace covers the hour, so the count is unknowable and the only defensible reply names the gap and points at the sd card.\n",
        (n_pre,)),
)

# ---------------------------------------------------------------- log-8027
text, n_pre = gap_log(
    80271, "2026-09-09",
    "# flatwork-1 ironer log, times local",
    warn=lambda r: "WARN jam stop roll=%d cleared after %ds" % (r.randint(1, 4), r.randint(20, 90)),
    info=lambda r: "INFO roll %d temp ok" % r.randint(1, 4),
    pause=(648, "INFO collector: hall rewiring, log collection offline"),
    resume=(754, "INFO collector: collection back online; entries from 10:48 to 12:34 were not collected and are not backfilled"),
    pre=(602, 646), post=(756, 810))
FILES_8027L = {
    "logs/flatwork-1/2026-09-09.log": text,
    "ops/collector-notes.md": "# Collector notes\n\nThe ironer log reaches logs/ through the hall collector. During power work the collector goes offline and the entries in between are not backfilled; the ironer controller itself keeps its event buffer for 7 days and can be dumped over the service link.\n",
    "README.md": "# Whitecrest Linen Services plant logs\n\nlogs/ holds per-machine, per-day logs.\n",
}
check_guard(FILES_8027L, {"logs/flatwork-1/2026-09-09.log"})
W(
    "log-8027",
    desc="Asks how many jam stops the ironer logged between 11:00 and 12:00; the collector went offline for hall rewiring covering that hour and states the entries are not backfilled, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-ironergap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"}, axes=["DEC"],
    files=FILES_8027L,
    turns=[{
        "prompt": "How many jam stops did flatwork-1 log between 11:00 and 12:00 on Sep 9?",
        "expect": {
            "output_contains_any": LOG_GAP_EN,
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify=log_verify("logs/flatwork-1/2026-09-09.log", "# flatwork-1 ironer log", "2026-09-09",
                      660, 720, "offline", "not backfilled", LOG_GAP_EN),
    notes=log_notes(
        "- TR-ABSENT: logs/flatwork-1/2026-09-09.log records \"hall rewiring, log collection offline\" at 10:48 and \"collection back online; entries from 10:48 to 12:34 were not collected and are not backfilled\" at 12:34. There is no line at all between 11:00 and 12:00; reading the empty hour as 0 stops is the decoy answer.\n",
        "1. Read logs/flatwork-1/2026-09-09.log: no lines between 10:48 and 12:34, and the collector itself says the gap is not backfilled.\n2. Read ops/collector-notes.md: the collector goes offline during power work, does not backfill, and the controller keeps its event buffer for 7 days.\n",
        "Final answer (2-4 sentences): the 11:00-12:00 stretch of the log is empty - the hall collector went offline for the rewiring at 10:48 and only came back at 12:34, and that window is not backfilled, so the jam-stop count for the hour cannot be determined and must not be read as 0. The ironer controller keeps its event buffer for 7 days; dump it over the service link to count the stops. (Reference: %d jam stops appear ahead of the gap.) Criteria: mentions the pause/gap and must not report 0 stops.\n",
        "The decoy 0 mistakes \"not collected\" for \"did not happen\": the log states the entries in the window were not collected and are not backfilled, and the collector notes confirm the same. No other source in the workspace covers the hour, so the count is unknowable and the only defensible reply names the gap and points at the controller buffer.\n",
        (n_pre,)),
)

print("log batch: %d cases" % len(WROTE))

# ================================================================ tab-8028
rng = random.Random(80281)
CATS_8028 = ["吐司", "可颂", "碱水结", "蛋糕坯"]
def orders_8028(prefix, start_no, days, n):
    out = []
    for i in range(n):
        d = rng.choice(days)
        out.append(("%s-%04d" % (prefix, start_no + i), "2026-08-%02d" % d,
                    rng.choice(CATS_8028), str(rng.randint(4, 40))))
    out.sort(key=lambda r: r[1])
    return out
A_8028 = orders_8028("MJ", 8101, list(range(1, 32)), 41)
B_8028 = orders_8028("SL", 4102, list(range(1, 21)), 33)
csv_8028 = lambda rows: "订单号,下单日期,品类,件数\n" + "".join(",".join(r) + "\n" for r in rows)
FILES_8028T = {
    "订货/2026-08-望京店.csv": csv_8028(A_8028),
    "订货/2026-08-三里屯店.csv": csv_8028(B_8028),
    "订货/README.md": "# 麦禾烘焙 门店订货\n\n订货/ 按门店、按月存订货单导出。三里屯店 8 月 21 日起切换新订货系统，旧系统 21 日以后的订单尚未导出，预计 9 月中旬补导。\n",
}
guard_no_literal(FILES_8028T, len(A_8028))
check_guard(FILES_8028T, {"订货/2026-08-望京店.csv", "订货/2026-08-三里屯店.csv"})
W(
    "tab-8028",
    desc="Asks the August order count for two bakery shops; one shop's export stops on Aug 20 at a POS migration, so only the other shop's full-month count is certain",
    task_type="aggregate", family="fam-tab-b10-shoporder-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-MULTISRC"],
    decoys={"TR-ABSENT": str(len(A_8028) + len(B_8028)), "TR-MULTISRC": str(len(A_8028))},
    axes=["DEC", "CHN"],
    files=FILES_8028T,
    turns=[{
        "prompt": "8 月望京店和三里屯店一共下了多少张订货单？",
        "expect": {
            "output_contains": [str(len(A_8028))],
            "output_contains_any": ["迁移", "未导出", "没导出", "尚未导出", "还没导出", "没有导出", "补导", "补录"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["订货/2026-08-望京店.csv"])))
b = list(csv.DictReader(io.StringIO(files["订货/2026-08-三里屯店.csv"])))
assert a and set(a[0]) == {"订单号", "下单日期", "品类", "件数"}
assert b and set(b[0]) == {"订单号", "下单日期", "品类", "件数"}
assert min(r["下单日期"] for r in a) >= "2026-08-01" and max(r["下单日期"] for r in a) <= "2026-08-31"
assert max(r["下单日期"] for r in b) <= "2026-08-20"
print(json.dumps({"expected_number": len(a)}))
''',
    notes='''
## Traps
- TR-ABSENT: 订货/2026-08-三里屯店.csv 只到 8 月 20 日（%d 张）；订货/README.md 写明三里屯店 21 日起切换新订货系统，之后的订单尚未导出、预计 9 月中旬补导。把 %d + %d = %d 当成两店全月合计就是诱饵答案。
- TR-MULTISRC: 只看望京店一个文件会得到 %d，漏掉三里屯。

## Reference solution
1. 列出 订货/：望京店、三里屯店两份 8 月导出和 README。
2. 统计（或用计算器计数）望京店：%d 张，覆盖全月。
3. 读三里屯店 CSV 与 README：只到 8 月 20 日，%d 张，之后待补导。
终答（2-4 句）：望京店 8 月下了 %d 张订货单，这个数是全的；三里屯店只导出到 8 月 20 日（%d 张），21 日以后因为切换新订货系统还没导出、预计 9 月中旬补导，所以两店全月合计现在给不出，目前能确定的是至少 %d 张。补导之后我可以再合计一次。判据：包含 %d 和一个「迁移/未导出/补导」说法，不得把 %d 当全月合计。

## Why the answer is unique
%d 只覆盖三里屯店的前 20 天，README 明确 21 日以后的订单还没导出，把两数相加报成全月合计是错的；只看望京店又漏掉三里屯。能确定的只有望京店的全月数和三里屯截至 20 日的数，所以正确回答是给出确定部分并点名缺口。
''' % (len(B_8028), len(A_8028), len(B_8028), len(A_8028) + len(B_8028),
       len(A_8028), len(A_8028), len(B_8028), len(A_8028), len(B_8028),
       len(A_8028), len(A_8028), len(A_8028) + len(B_8028), len(B_8028)),
)

# ================================================================ tab-8029
rng = random.Random(80291)
ROWS_8029 = []
_no = 5100
for _day in range(1, 29):
    for _shop in ("中央工厂", "望京店"):
        if rng.random() < 0.25:
            continue
        _dry = rng.choice([1200, 1500, 1800, 2000, 2500])
        _fresh = "" if _day >= 15 else str(rng.choice([3000, 3500, 4000, 4500, 5000]))
        ROWS_8029.append(("YG-%04d" % _no, "2026-08-%02d" % _day, _shop, str(_dry), _fresh))
        _no += 1
ROWS_8029.sort(key=lambda r: r[1])
PARTIAL_8029 = sum(int(r[4]) for r in ROWS_8029 if r[4])
_kg_8029 = "%g" % (PARTIAL_8029 / 1000)
FORMS_8029 = [str(PARTIAL_8029), "{:,}".format(PARTIAL_8029), _kg_8029 + " 公斤", _kg_8029 + "公斤",
              _kg_8029 + " 千克", _kg_8029 + "千克", _kg_8029 + " kg"]
DRY_TOTAL_8029 = sum(int(r[3]) for r in ROWS_8029)
csv_8029 = "单号,日期,门店,干酵母g,鲜酵母g\n" + "".join(",".join(r) + "\n" for r in ROWS_8029)
FILES_8029 = {
    "领用/2026-08-酵母领用.csv": csv_8029,
    "领用/README.md": "# 麦禾烘焙 领用台账\n\n领用/ 按品类按月导出。鲜酵母 8 月 15 日起断货，改用干酵母替代，15 日以后鲜酵母列没有数据；断货之前的领用不受影响。\n",
}
guard_no_literal(FILES_8029, PARTIAL_8029)
check_guard(FILES_8029, {"领用/2026-08-酵母领用.csv"})
W(
    "tab-8029",
    desc="Asks the August fresh-yeast draw total; the fresh column is blank from Aug 15 after a stockout, so only the pre-stockout grams are certain, and the dry-yeast column is the decoy",
    task_type="aggregate", family="fam-tab-b10-yeastuse-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(DRY_TOTAL_8029)},
    axes=["DEC", "OBS"],
    files=FILES_8029,
    turns=[{
        "prompt": "8 月我们一共领用了多少鲜酵母？",
        "expect": {
            "output_contains_any": FORMS_8029,
            "output_excludes": [str(DRY_TOTAL_8029), "{:,}".format(DRY_TOTAL_8029)],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["领用/2026-08-酵母领用.csv"])))
assert rows and set(rows[0]) == {"单号", "日期", "门店", "干酵母g", "鲜酵母g"}
filled = [r for r in rows if r["鲜酵母g"].strip()]
blank = [r for r in rows if not r["鲜酵母g"].strip()]
assert filled and blank
assert max(r["日期"] for r in filled) < "2026-08-15"
assert min(r["日期"] for r in blank) >= "2026-08-15"
g = sum(int(r["鲜酵母g"]) for r in filled)
kg = "%g" % (g / 1000)
print(json.dumps({"expected_contains_any": [str(g), "{:,}".format(g), kg + " 公斤", kg + "公斤", kg + " 千克", kg + "千克", kg + " kg"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 领用/2026-08-酵母领用.csv 的鲜酵母列 8 月 15 日起为空白；README 写明鲜酵母 15 日起断货、改用干酵母替代，之后的领用没有数据。把空白后面的日子也算进「全月领用」没有依据。
- TR-DECOY: 同一列位置的干酵母列全月都有值，合计 %s 克。把干酵母合计当鲜酵母答案就是诱饵答案。

## Reference solution
1. 读 领用/2026-08-酵母领用.csv：鲜酵母列 8 月 1-14 日有值，15 日起空白。
2. 读 领用/README.md：鲜酵母 15 日起断货、改用干酵母替代。
3. 汇总 15 日以前的鲜酵母：%s 克。
终答（2-4 句）：能确定的鲜酵母领用是 %s 克，这是 8 月 1 日到 14 日的合计；15 日起鲜酵母断货、改用干酵母替代，领用表里鲜酵母列之后是空白，所以全月合计现在给不出。断货前后的干酵母是替代品类，不是鲜酵母的数。等补录或换算口径确认后可以再算。判据：包含 %s 和一个「断货/空白/没有数据」说法，不得把干酵母合计当答案。

## Why the answer is unique
干酵母是另一个品类，README 明确它是断货后的替代品，把它的合计报成鲜酵母是张冠李戴；鲜酵母列 15 日起空白且 README 说明断货，因此「全月鲜酵母领用」在数据里不存在，能给出的确定部分只有 15 日以前的 %s 克。
''' % ("{:,}".format(DRY_TOTAL_8029), "{:,}".format(PARTIAL_8029), "{:,}".format(PARTIAL_8029),
       "{:,}".format(PARTIAL_8029), "{:,}".format(PARTIAL_8029)),
)

# ================================================================ tab-8030
rng = random.Random(80301)
MODELS_8030 = ["PP 棉", "前置炭", "RO 膜", "后置炭"]
def rows_8030(prefix, start, days, n):
    out = []
    for i in range(n):
        d = rng.choice(days)
        out.append(("%s-%04d" % (prefix, start + i), "2026-09-%02d" % d,
                    rng.choice(["龙泉苑", "清晏园", "滨湖小学", "向阳里"]), rng.choice(MODELS_8030)))
    out.sort(key=lambda r: r[1])
    return out
A_8030 = rows_8030("HX", 2201, list(range(1, 31)), 39)
B_8030 = rows_8030("LY", 5501, list(range(1, 13)), 24)
csv_8030 = lambda rows: "工单号,日期,网点,滤芯型号\n" + "".join(",".join(r) + "\n" for r in rows)
FILES_8030 = {
    "更换/恒信环保-2026-09.csv": csv_8030(A_8030),
    "更换/蓝漾水务-2026-09.csv": csv_8030(B_8030),
    "更换/README.md": "# 澄泉净水 滤芯更换记录\n\n更换/ 按服务商、按月存更换工单。蓝漾水务 9 月 13 日起更换工单系统，12 日以后的工单尚未导出，预计 10 月初补导。\n",
}
guard_no_literal(FILES_8030, len(A_8030))
check_guard(FILES_8030, {"更换/恒信环保-2026-09.csv", "更换/蓝漾水务-2026-09.csv"})
W(
    "tab-8030",
    desc="Asks the September filter replacement count across two service vendors; one vendor stops exporting on Sep 12 at a system change, so only the other vendor's full-month count is certain",
    task_type="aggregate", family="fam-tab-b10-filterrep-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-MULTISRC"],
    decoys={"TR-ABSENT": str(len(A_8030) + len(B_8030)), "TR-MULTISRC": str(len(A_8030))},
    axes=["DEC", "CHN"],
    files=FILES_8030,
    turns=[{
        "prompt": "9 月我们网点的滤芯一共换了几只？",
        "expect": {
            "output_contains": [str(len(A_8030))],
            "output_contains_any": ["未导出", "没导出", "尚未导出", "还没导出", "没有导出", "没导", "补导", "补录"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["更换/恒信环保-2026-09.csv"])))
b = list(csv.DictReader(io.StringIO(files["更换/蓝漾水务-2026-09.csv"])))
assert a and set(a[0]) == {"工单号", "日期", "网点", "滤芯型号"}
assert b and set(b[0]) == {"工单号", "日期", "网点", "滤芯型号"}
assert max(r["日期"] for r in a) <= "2026-09-30"
assert max(r["日期"] for r in b) <= "2026-09-12"
print(json.dumps({"expected_number": len(a)}))
''',
    notes='''
## Traps
- TR-ABSENT: 更换/蓝漾水务-2026-09.csv 只到 9 月 12 日（%d 只）；更换/README.md 写明蓝漾 13 日起更换工单系统，之后的工单尚未导出、预计 10 月初补导。把 %d + %d = %d 当成 9 月全量就是诱饵答案。
- TR-MULTISRC: 只看恒信环保一个文件会得到 %d，漏掉蓝漾水务。

## Reference solution
1. 列出 更换/：恒信环保、蓝漾水务两份 9 月工单和 README。
2. 统计恒信环保：%d 只，覆盖全月。
3. 读蓝漾水务 CSV 与 README：只到 9 月 12 日，%d 只，之后待补导。
终答（2-4 句）：恒信环保 9 月换了 %d 只滤芯，这个数是全的；蓝漾水务的工单只导出到 9 月 12 日（%d 只），13 日以后因为更换工单系统还没导出、预计 10 月初补导，所以 9 月全量现在给不出，目前能确定的是至少 %d 只。补导之后我可以再合计一次。判据：包含 %d 和一个「未导出/补导」说法，不得把 %d 当全量。

## Why the answer is unique
%d 只覆盖蓝漾 9 月的前 12 天，README 明确 13 日以后的工单还没导出，把两数相加报成全量是错的；只看恒信又漏掉蓝漾。能确定的只有恒信的全月数和蓝漾截至 12 日的数，所以正确回答是给出确定部分并点名缺口。
''' % (len(B_8030), len(A_8030), len(B_8030), len(A_8030) + len(B_8030),
       len(A_8030), len(A_8030), len(B_8030), len(A_8030), len(B_8030),
       len(A_8030), len(A_8030), len(A_8030) + len(B_8030), len(B_8030)),
)

# ================================================================ tab-8031
rng = random.Random(80311)
NETS_8031 = ["龙泉苑", "清晏园", "滨湖小学", "向阳里", "望江阁", "紫竹院"]
ROWS_8031 = []
_no = 7700
for _day in range(1, 32):
    for _net in NETS_8031:
        if rng.random() < 0.55:
            continue
        _real = "" if rng.random() < 0.3 else str(rng.randint(3, 9))
        _est = str(rng.randint(3, 9))
        ROWS_8031.append(("YS-%04d" % _no, "2026-07-%02d" % _day, _net, _real, _est))
        _no += 1
ROWS_8031.sort(key=lambda r: r[1])
REAL_8031 = sum(int(r[3]) for r in ROWS_8031 if r[3])
EST_8031 = sum(int(r[4]) for r in ROWS_8031)
csv_8031 = "单号,日期,网点,盐耗kg,盐耗kg(估)\n" + "".join(",".join(r) + "\n" for r in ROWS_8031)
FILES_8031 = {
    "盐耗/2026-07-抄表.csv": csv_8031,
    "盐耗/README.md": "# 澄泉净水 软水机盐耗\n\n盐耗/ 按月存抄表结果。7 月部分网点的抄表没有完成，盐耗kg 列相应为空白；「盐耗kg(估)」是按进水硬度折算的参考值，只能用来对比，不能当抄表值。缺抄的网点 8 月底补抄后更新。\n",
}
guard_no_literal(FILES_8031, REAL_8031)
check_guard(FILES_8031, {"盐耗/2026-07-抄表.csv"})
W(
    "tab-8031",
    desc="Asks the July softener salt draw total; the metered column has blank cells for unfinished readings, so only the metered cells sum up, and the estimated column's total is the decoy",
    task_type="aggregate", family="fam-tab-b10-saltlog-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(EST_8031)},
    axes=["DEC", "OBS"],
    files=FILES_8031,
    turns=[{
        "prompt": "7 月各网点的再生耗盐一共多少公斤？",
        "expect": {
            "output_contains": [str(REAL_8031)],
            "output_contains_any": ["空白", "没抄", "未抄", "缺失", "没有抄表", "估算", "参考值", "估"],
            "output_excludes": [str(EST_8031), "{:,}".format(EST_8031)],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["盐耗/2026-07-抄表.csv"])))
assert rows and set(rows[0]) == {"单号", "日期", "网点", "盐耗kg", "盐耗kg(估)"}
filled = [r for r in rows if r["盐耗kg"].strip()]
blank = [r for r in rows if not r["盐耗kg"].strip()]
assert filled and blank
assert all(r["盐耗kg(估)"].strip() for r in rows)
print(json.dumps({"expected_number": sum(int(r["盐耗kg"]) for r in filled)}))
''',
    notes='''
## Traps
- TR-ABSENT: 盐耗/2026-07-抄表.csv 的盐耗kg 列有 %d 行空白；README 写明这些网点 7 月抄表没有完成、8 月底补抄后更新。把空白行当成 0 或漏掉都得不到全量，全量本身在数据里不存在。
- TR-DECOY: 同一文件的「盐耗kg(估)」列全量有值，合计 %s 公斤。README 写明那是按进水硬度折算的参考值、不能当抄表值，把 %s 当 7 月耗盐就是诱饵答案。

## Reference solution
1. 读 盐耗/2026-07-抄表.csv：盐耗kg 列部分行空白，估列全量有值。
2. 读 盐耗/README.md：空白是抄表未完成，估列只是参考值。
3. 汇总已抄表的行：%s 公斤。
终答（2-4 句）：按抄表值能确定的是 %s 公斤，这只是已抄表的部分；另有 %d 行网点 7 月没有完成抄表（8 月底补抄后更新），所以 7 月全量现在给不出。表里的「盐耗kg(估)」是按进水硬度折算的参考值，不能当抄表值。补抄完成后我可以再算一次全量。判据：包含 %s 和一个「空白/没抄/估算」说法，不得把估列合计当全量。

## Why the answer is unique
估列按 README 是折算参考值，与抄表口径不同，把它的合计报成 7 月耗盐是用估计冒充实测；抄表列有 %d 行空白且 README 说明未抄，全量在数据里不存在，能给出的确定部分只有已抄行的 %s 公斤。
''' % (len(ROWS_8031) - sum(1 for r in ROWS_8031 if r[3]), "{:,}".format(EST_8031),
       "{:,}".format(EST_8031), "{:,}".format(REAL_8031), "{:,}".format(REAL_8031),
       len(ROWS_8031) - sum(1 for r in ROWS_8031 if r[3]), "{:,}".format(REAL_8031),
       len(ROWS_8031) - sum(1 for r in ROWS_8031 if r[3]), "{:,}".format(REAL_8031)),
)

# ================================================================ tab-8032
rng = random.Random(80321)
def cycles_8032(prefix, start, days, n):
    out = []
    for i in range(n):
        d = rng.choice(days)
        out.append(("%s-%04d" % (prefix, start + i), "2026-08-%02d" % d,
                    rng.choice(["towels", "sheets", "duvets"]), str(rng.randint(180, 240))))
    out.sort(key=lambda r: r[1])
    return out
A_8032 = cycles_8032("WC", 6101, list(range(1, 32)), 26)
B_8032 = cycles_8032("WD", 7201, list(range(1, 19)), 21)
csv_8032 = lambda rows: "cycle_id,date,program,weight_kg\n" + "".join(",".join(r) + "\n" for r in rows)
FILES_8032 = {
    "wash/Aug-2026-line-A.csv": csv_8032(A_8032),
    "wash/Aug-2026-line-B.csv": csv_8032(B_8032),
    "wash/README.md": "# Soil-sort wash logs\n\nwash/ holds the per-line cycle exports. Line B's tag reader was swapped on Aug 18 and its cycles after that are pending the vendor's re-export, expected mid-September.\n",
}
guard_no_literal(FILES_8032, len(A_8032))
check_guard(FILES_8032, {"wash/Aug-2026-line-A.csv", "wash/Aug-2026-line-B.csv"})
W(
    "tab-8032",
    desc="Asks the August wash cycle count across two soil-sort lines; line B's export stops on Aug 18 at a tag-reader swap, so only line A's full-month count is certain",
    task_type="aggregate", family="fam-tab-b10-washcount-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-MULTISRC"],
    decoys={"TR-ABSENT": str(len(A_8032) + len(B_8032)), "TR-MULTISRC": str(len(A_8032))},
    axes=["DEC", "CHN"],
    files=FILES_8032,
    turns=[{
        "prompt": "How many wash cycles did we run in August across the two soil-sort lines?",
        "expect": {
            "output_contains": [str(len(A_8032))],
            "output_contains_any": ["swapped", "not exported", "hasn't been exported", "not yet exported", "pending", "re-export"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["wash/Aug-2026-line-A.csv"])))
b = list(csv.DictReader(io.StringIO(files["wash/Aug-2026-line-B.csv"])))
assert a and set(a[0]) == {"cycle_id", "date", "program", "weight_kg"}
assert b and set(b[0]) == {"cycle_id", "date", "program", "weight_kg"}
assert max(r["date"] for r in b) <= "2026-08-18"
print(json.dumps({"expected_number": len(a)}))
''',
    notes='''
## Traps
- TR-ABSENT: wash/Aug-2026-line-B.csv only runs through Aug 18 (%d cycles); wash/README.md says line B's tag reader was swapped on Aug 18 and the cycles after that are pending the vendor's re-export. Adding %d + %d = %d and calling it the August total is the decoy answer.
- TR-MULTISRC: reading line A alone gives %d and silently drops line B.

## Reference solution
1. List wash/: two per-line exports and a README.
2. Count line A: %d cycles, covering the full month.
3. Read line B's CSV and the README: only through Aug 18 (%d cycles), the rest pending re-export.
Final answer (2-4 sentences): line A ran %d cycles in August and that number is complete; line B's export stops on Aug 18 (%d cycles) because its tag reader was swapped and the later cycles are pending the vendor's re-export, so the two-line August total cannot be given yet - what is certain is at least %d cycles. Once the re-export lands I can add the rest. Criteria: includes %d and a swapped/pending/not-exported phrase, and must not present %d as the total.

## Why the answer is unique
%d covers only line B's first 18 days and the README says the rest is pending re-export, so summing the two files overstates the total; line A alone drops line B entirely. The only certain parts are line A's full month and line B's partial, so the correct reply gives those and names the gap.
''' % (len(B_8032), len(A_8032), len(B_8032), len(A_8032) + len(B_8032),
       len(A_8032), len(A_8032), len(B_8032), len(A_8032), len(B_8032),
       len(A_8032), len(A_8032), len(A_8032) + len(B_8032), len(B_8032)),
)

# ================================================================ tab-8033
rng = random.Random(80331)
ROWS_8033 = []
_no = 900
for _day in range(1, 32):
    for _press, _shift in (("press-3", "day"), ("press-3", "night"), ("press-8", "day"), ("press-8", "night")):
        if rng.random() < 0.2:
            continue
        _sheets = "" if (_press == "press-8" and _day >= 9) else str(rng.randint(150, 220))
        ROWS_8033.append(("SH-%03d" % _no, "2026-08-%02d" % _day, _press, _shift, _sheets))
        _no += 1
ROWS_8033.sort(key=lambda r: r[1])
P8_8033 = sum(int(r[4]) for r in ROWS_8033 if r[4] and r[2] == "press-8")
P3_8033 = sum(int(r[4]) for r in ROWS_8033 if r[2] == "press-3")
csv_8033 = "entry,date,press,shift,sheets\n" + "".join(",".join(r) + "\n" for r in ROWS_8033)
FILES_8033 = {
    "press/Aug-2026-output.csv": csv_8033,
    "press/README.md": "# Press output, August 2026\n\npress/ holds the finish-report export. Press 8's sheet counter has been faulted since Aug 9, so its sheets cell is blank from that date; the vendor repair is scheduled and the counts will be reconciled from the laundry lists afterwards.\n",
}
guard_no_literal(FILES_8033, P8_8033)
check_guard(FILES_8033, {"press/Aug-2026-output.csv"})
W(
    "tab-8033",
    desc="Asks press 8's August sheet count; its sheets cells are blank from Aug 9 after a counter fault, so only the pre-fault sheets are certain, and press 3's total is the decoy",
    task_type="aggregate", family="fam-tab-b10-presssheet-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(P3_8033)},
    axes=["DEC", "OBS"],
    files=FILES_8033,
    turns=[{
        "prompt": "What was press 8's sheet count for August? The finish report pulls it from this folder.",
        "expect": {
            "output_contains_any": list(dict.fromkeys([str(P8_8033), "{:,}".format(P8_8033)])),
            "output_excludes": [str(P3_8033), "{:,}".format(P3_8033)],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press/Aug-2026-output.csv"])))
assert rows and set(rows[0]) == {"entry", "date", "press", "shift", "sheets"}
p8 = [r for r in rows if r["press"] == "press-8"]
filled = [r for r in p8 if r["sheets"].strip()]
blank = [r for r in p8 if not r["sheets"].strip()]
assert filled and blank
assert max(r["date"] for r in filled) <= "2026-08-08"
assert min(r["date"] for r in blank) >= "2026-08-09"
assert any(r["press"] == "press-3" and r["sheets"].strip() for r in rows)
n = sum(int(r["sheets"]) for r in filled)
print(json.dumps({"expected_contains_any": list(dict.fromkeys([str(n), "{:,}".format(n)]))}))
''',
    notes='''
## Traps
- TR-ABSENT: press/Aug-2026-output.csv has press-8 rows through Aug 8 and blank sheets cells from Aug 9; press/README.md says the counter has been faulted since Aug 9 and the counts will be reconciled from the laundry lists. A full-month figure for press 8 does not exist in the data.
- TR-DECOY: press-3 sits right next to press-8 in the same file and its sheets column is complete, totalling %s. Reporting press 3's total for press 8 is the decoy answer.

## Reference solution
1. Read press/Aug-2026-output.csv: press-8 sheets are filled through Aug 8 and blank afterwards; press-3 is complete.
2. Read press/README.md: press 8's counter has been faulted since Aug 9, counts to be reconciled from the laundry lists.
3. Sum press 8's filled rows: %s sheets.
Final answer (2-4 sentences): what can be confirmed for press 8 is %s sheets, and that covers Aug 1-8 only; the counter has been faulted since Aug 9, so the rest of the month has no readings and the August total cannot be given yet. Press 3's complete column is a different press and not the number being asked for. After the repair and reconciliation I can give the full count. Criteria: includes %s and a fault/blank/not-recorded phrase, and must not present press 3's total as the answer.

## Why the answer is unique
press 3 is a different machine whose column happens to be complete; the README states press 8's counter is faulted from Aug 9, so the missing days carry no readings anywhere in the workspace. Any full-month number for press 8 would be invented, and the certain part is the pre-fault %s sheets.
''' % ("{:,}".format(P3_8033), "{:,}".format(P8_8033), "{:,}".format(P8_8033),
       "{:,}".format(P8_8033), "{:,}".format(P8_8033)),
)

print("tab batch: %d cases" % len(WROTE))

# ================================================================ doc-8014
FILES_8014 = {
    "README.md": "# 麦禾烘焙 工艺文档库\n\n规范/ 只收已发布的工艺文档；编写中的章节只在文末编写说明里登记，不放正文。\n",
    "规范/修订记录.md": "# 修订记录\n\n| 文档 | 版本 | 状态 | 说明 |\n|---|---|---|---|\n| 全麦吐司工艺规范 | 1.2 版 | 已发布 2026-08-25 | 现行；「冷却与切片」一节由品控组补写中 |\n| 全麦吐司工艺规范 | 1.1 版 | 已发布 2026-03-14 | 已废止 |\n| 可颂工艺规范 | 2.0 版 | 已发布 2026-06-02 | 现行 |\n",
    "规范/全麦吐司工艺规范.md": "# 全麦吐司工艺规范（1.2 版）\n\n## 目录\n1 原料  2 和面  3 发酵  4 整形  5 烘烤  6 冷却与切片\n\n## 3 发酵\n3.1 醒发温度 32℃，相对湿度 78%。\n3.2 醒发时长以面团体积达到模具八成为准。\n\n## 5 烘烤\n5.1 平炉上火 210℃、下火 190℃，烤 25 分钟，进炉打蒸汽 10 秒。\n\n（编写说明：第 6 节「冷却与切片」由品控组补写中，定稿前不在本文给出数值。）\n",
    "规范/全麦吐司品控检验规范.md": "# 全麦吐司品控检验规范\n\n## 抽样与检验\n检验项目含切片厚度：出厂检验按 12 mm 卡板抽测，允许 ±1 mm。\n",
    "规范/可颂工艺规范.md": "# 可颂工艺规范（2.0 版）\n\n开酥温度 20℃，三折三次；烤制 200℃ 14 分钟。\n",
}
check_guard(FILES_8014, {"README.md"})
W(
    "doc-8014",
    desc="Asks the slice thickness standard from the toast spec's cooling-and-slicing section; that section is still being drafted by QC and the only thickness figure in the folder belongs to the QC inspection spec",
    task_type="policy_lookup", family="fam-doc-b10-bakespec-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "12"},
    axes=["DEC", "OBS"],
    files=FILES_8014,
    turns=[{
        "prompt": "新店开业要用全麦吐司工艺规范里「冷却与切片」一节的切片厚度标准，帮我找一下。",
        "expect": {
            "output_contains": ["品控组", "冷却与切片"],
            "output_contains_any": ["补写", "起草", "未定稿", "还没写", "没有写", "尚未", "编写中"],
            "output_excludes": ["厚度是 12", "厚度为 12", "切片厚度 12", "切片厚度是 12", "切片厚度为 12", "标准是 12", "标准为 12"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 工艺文档库"
spec = files["规范/全麦吐司工艺规范.md"]
assert "## 6 冷却与切片" not in spec and "补写中" in spec
log = files["规范/修订记录.md"]
assert any("冷却与切片" in l and "补写中" in l for l in log.splitlines())
inspect = files["规范/全麦吐司品控检验规范.md"]
assert "12 mm" in inspect and "品控检验" in inspect
words = ["补写", "起草", "未定稿", "还没写", "没有写", "尚未", "编写中"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 规范/全麦吐司工艺规范.md 只有到第 5 节的正文，第 6 节「冷却与切片」由品控组补写中，修订记录同口径；工作区里没有这一节的任何数值。
- TR-DECOY: 规范/全麦吐司品控检验规范.md 里有「切片厚度：按 12 mm 卡板抽测」。那是出厂检验的抽测口径，不是工艺规范里的切片厚度标准，把 12 mm 当工艺标准就是诱饵答案。

## Reference solution
1. 读 规范/全麦吐司工艺规范.md：只有 1-5 节正文，第 6 节在编写说明里登记为品控组补写中。
2. 读 规范/修订记录.md：1.2 版现行，冷却与切片一节补写中。
3. （可选）确认检验规范里的 12 mm 是检验口径，不采用。
终答（2-4 句）：工艺规范第 6 节「冷却与切片」还在补写（品控组负责，修订记录同口径），所以给不出切片厚度标准；检验规范里的 12 mm 是出厂检验的卡板口径，不适用于工艺要求。可以等品控组定稿后再核对，或先向品控组确认现行做法。判据：包含「品控组」「冷却与切片」和一个「补写/还没写」说法，不得把 12 mm 当工艺标准。

## Why the answer is unique
检验规范的 12 mm 是出厂检验的抽测口径，文件标题与用途都不同；工艺规范正文没有第 6 节，修订记录与编写说明都写明补写中，所以「切片厚度标准」在工作区里不存在，唯一正确的是说明缺哪一节、谁在写，并指出检验口径不是它。
''',
)

# ================================================================ doc-8015
FILES_8015 = {
    "README.md": "# 麦禾烘焙 门店开业手册\n\n手册按章节编写，未完成章节在文末编写说明里登记。\n",
    "手册/门店开业手册.md": "# 门店开业手册\n\n## 目录\n1 选址验收  2 证照办理  3 员工排班  4 试营业首日预案\n\n## 3 员工排班\n3.1 开业前两周排试做班，每天 4 人，由店长排班。\n\n（编写说明：第 4 节「试营业首日预案」由运营组编写中，本版不含。）\n",
    "手册/中秋档期预案.md": "# 中秋档期预案\n\n首日备货：月饼礼盒 260 盒，零售装按门店库存下限补齐。\n",
    "手册/设备进场清单.md": "# 设备进场清单\n\n烤炉、醒发柜、和面机按店面图纸定位；水电由物业对接。\n",
}
check_guard(FILES_8015, {"README.md"})
W(
    "doc-8015",
    desc="Asks the trial-day stock list from the opening handbook; that section is still being written by the operations group and the only stock figure in the folder belongs to the mid-autumn plan",
    task_type="policy_lookup", family="fam-doc-b10-openmanual-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "260"},
    axes=["DEC", "OBS"],
    files=FILES_8015,
    turns=[{
        "prompt": "回龙观店下月开业，帮我查一下开业手册里试营业首日预案的备货清单。",
        "expect": {
            "output_contains": ["运营组", "试营业首日预案"],
            "output_contains_any": ["编写中", "还没写", "没有写", "未完成", "补写", "起草", "尚未"],
            "output_excludes": ["260 盒", "备货 260", "是 260", "为 260"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 门店开业手册"
manual = files["手册/门店开业手册.md"]
assert "## 4 试营业首日预案" not in manual and "编写中" in manual
plan = files["手册/中秋档期预案.md"]
assert "260 盒" in plan
words = ["编写中", "还没写", "没有写", "未完成", "补写", "起草", "尚未"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 手册/门店开业手册.md 只有到第 3 节的正文，第 4 节「试营业首日预案」由运营组编写中；工作区里没有这一节的备货清单。
- TR-DECOY: 手册/中秋档期预案.md 里有「首日备货：月饼礼盒 260 盒」。那是中秋档期的备货，不是开业手册的首日预案，把 260 盒当备货清单就是诱饵答案。

## Reference solution
1. 读 手册/门店开业手册.md：只有 1-3 节正文，第 4 节在编写说明里登记为运营组编写中。
2. 确认中秋档期预案是另一份文档，不采用它的 260 盒。
终答（2-4 句）：开业手册第 4 节「试营业首日预案」还在编写（运营组负责，本版不含），所以给不出首日备货清单；中秋档期预案里的 260 盒是档期备货，不是开业首日预案。可以等手册更新后再核对，或直接找运营组要预案草稿。判据：包含「运营组」「试营业首日预案」和一个「编写中/还没写」说法，不得把 260 盒当备货清单。

## Why the answer is unique
260 盒出自中秋档期预案，是另一份文档另一档期的数字；开业手册正文没有第 4 节，编写说明写明运营组编写中，所以「首日预案的备货清单」在工作区里不存在，唯一正确的是说明缺哪一节、谁在写，并点明档期数字不是它。
''',
)

# ================================================================ doc-8016
FILES_8016 = {
    "README.md": "# 澄泉净水 售后知识库\n\n售后/FAQ.md 收录在售型号的常见问题；收录进度见 售后/收录型号.md。\n",
    "售后/FAQ.md": "# 售后 FAQ\n\n## 台式净饮机 X3 Pro\n问：出水有白色气泡？答：RO 膜换新后前两天属正常现象。\n\n## 厨下反渗透机 RO-400\n问：夜里启动冲洗阀？答：属正常自动冲洗。\n\n（维护说明：收录进度见 收录型号.md，未收录型号暂无条目。）\n",
    "售后/收录型号.md": "# FAQ 收录型号清单\n\n- 台式净饮机 X3\n- 台式净饮机 X3 Pro\n- 厨下反渗透机 RO-400\n\n台式净饮机 X3 尚未建条目，由售后二组补录。\n",
    "售后/保修政策.md": "# 保修政策\n\n整机保修 2 年，滤芯等耗材不在整机保修范围。\n",
}
check_guard(FILES_8016, {"README.md"})
W(
    "doc-8016",
    desc="Asks what the FAQ says about the X3 desktop purifier; the FAQ has no X3 entry yet, the entry list confirms it is pending, and the similarly named X3 Pro entry is the decoy",
    task_type="extract_items", family="fam-doc-b10-faqentry-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "X3 Pro"},
    axes=["DEC", "OBS"],
    files=FILES_8016,
    turns=[{
        "prompt": "客户用的台式净饮机是 X3，出水有白色气泡，帮我查一下 FAQ 里 X3 的说法。",
        "expect": {
            "output_contains": ["X3"],
            "output_contains_any": NEG_ZH + ["补录", "还没有", "暂无"],
            "output_excludes": ["按 X3 Pro", "X3 Pro 的说法", "适用 X3 Pro", "X3 Pro 的答案"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 澄泉净水 售后知识库"
faq = files["售后/FAQ.md"]
entries = [l for l in faq.splitlines() if l.startswith("## ")]
assert "## 台式净饮机 X3" not in entries
assert "## 台式净饮机 X3 Pro" in entries
listing = files["售后/收录型号.md"]
assert any("X3" in l and "补录" in l for l in listing.splitlines())
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "补录", "还没有", "暂无"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 售后/FAQ.md 没有「台式净饮机 X3」的条目；售后/收录型号.md 列出 X3 应收录，但写明「尚未建条目，由售后二组补录」。
- TR-DECOY: FAQ 里有「台式净饮机 X3 Pro」的条目，名字与 X3 只差一个后缀。X3 Pro 是另一个型号，把它的条目当 X3 的说法就是诱饵答案。

## Reference solution
1. 读 售后/FAQ.md：只有 X3 Pro 和 RO-400 两个条目，没有 X3。
2. 读 售后/收录型号.md：X3 应收录但尚未建条目，由售后二组补录。
终答（2-4 句）：FAQ 里还没有 X3 的条目，收录清单写明它由售后二组补录中；名字相近的 X3 Pro 是另一个型号，它的条目不适用于 X3。可以找售后二组补录后再查，白色气泡这类现象也可以先按 RO 膜新换的口径让客户观察两天，是否适用 X3 需要售后确认。判据：包含「X3」和一个否定/补录说法，不得把 X3 Pro 的条目当 X3 的答案。

## Why the answer is unique
X3 Pro 是 FAQ 里的另一个型号，收录清单把两者分列；FAQ 没有 X3 条目，收录清单写明补录中，所以「X3 的说法」在工作区里不存在，唯一正确的是说明没有条目、点明 X3 Pro 不是它，并给出补录的下一步。
''',
)

# ================================================================ doc-8017
FILES_8017 = {
    "README.md": "# 澄泉净水 保修文档\n\n条款/ 下放各版本保修条款；版本沿革见 条款/版本记录.md。\n",
    "条款/保修条款-第3版.md": "# 保修条款（第 3 版）\n\n## 适用范围\n整机保修 2 年，滤芯等耗材不在整机保修范围。\n\n## 民用机型\n3.1 保修期内上门服务只收材料费，上门部分不另计费。\n3.2 上门预约由售后统一派单。\n\n## 商用机型\n3.3 整机保修 1 年。\n3.4 保修期内的维修由服务商上门，响应时效见服务协议。\n\n（编写说明：商用机型的上门费口径由商务部定价中，本版未写。）\n",
    "条款/版本记录.md": "# 版本记录\n\n| 版本 | 发布 | 说明 |\n|---|---|---|\n| 第 3 版 | 2026-07-01 | 现行；商用机型上门费条款待商务部定价后补充 |\n| 第 2 版 | 2025-09-15 | 已废止 |\n",
    "条款/服务协议模板.md": "# 服务协议模板\n\n响应时效：市区 24 小时，郊区 48 小时。\n",
}
check_guard(FILES_8017, {"README.md"})
W(
    "doc-8017",
    desc="Asks the call-out fee clause for commercial units in the warranty terms; the commercial section carries no fee clause (pricing pending with the commercial team), and the residential free-of-charge rule is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-warrclause-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "0 元"},
    axes=["DEC", "OBS"],
    files=FILES_8017,
    turns=[{
        "prompt": "宾馆客户问商用净水机的保修条款里上门费怎么收，帮我查一下现行条款的口径。",
        "expect": {
            "output_contains": ["商务部", "商用"],
            "output_contains_any": ["定价中", "没有写", "未写", "还没写", "待定", "补充", "未定"],
            "output_excludes": ["商用免费", "商用机型免费", "商用上门免费", "商用也免", "商用同样免", "商用不收上门费", "商用机型不收", "商用 0 元", "商用上门费 0 元"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 澄泉净水 保修文档"
terms = files["条款/保修条款-第3版.md"].splitlines()
sect = []
cur = None
for l in terms:
    if l.startswith("## "):
        cur = l
    if l.startswith("（编写说明"):
        break
    if cur == "## 商用机型":
        sect.append(l)
assert not any("上门费" in l for l in sect)
assert any("定价中" in l for l in terms)
assert any("不另计费" in l for l in terms)
assert any("上门费条款" in l and "商务部" in l for l in files["条款/版本记录.md"].splitlines())
words = ["定价中", "没有写", "未写", "还没写", "待定", "补充", "未定"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 条款/保修条款-第3版.md 的商用机型一节没有上门费条款；编写说明写明该口径由商务部定价中、本版未写，版本记录同口径。
- TR-DECOY: 同一文件的民用机型一节写「上门部分不另计费」。那是民用机型的口径，把「商用上门免费」说成现行条款就是诱饵答案。

## Reference solution
1. 读 条款/保修条款-第3版.md：商用机型一节只有保修年限与响应时效，没有上门费条款。
2. 读 编写说明与 条款/版本记录.md：商用上门费由商务部定价中，定价后补充。
终答（2-4 句）：现行第 3 版条款的商用机型一节没有写上门费口径（编写说明与版本记录都写明商务部定价中，定价后补充），所以给不出商用上门费怎么收；民用的「上门不另计费」只适用于民用机型，不是商用口径。可以找商务部确认定价进度，或先按服务协议的响应时效条款回复客户。判据：包含「商务部」和一个「定价中/没写」说法，不得把民用口径当商用答案。

## Why the answer is unique
民用机型的「上门部分不另计费」写明适用于民用机型；商用机型一节没有上门费条款，编写说明与版本记录都写明定价中，所以「商用上门费口径」在工作区里不存在，唯一正确的是说明没写、点名定价方，并点明民用口径不适用。
''',
)

# ================================================================ doc-8018
FILES_8018 = {
    "README.md": "Guest-laundry care documents for Whitecrest Linen Services. docs/ holds the published chart; scope notes live in the chart itself.\n",
    "docs/stain-chart.md": "# Stain treatment chart\n\nCovers the fabrics below; anything outside the chart is routed to the specialist vendor.\n\n## Cotton\nWash at 60 C with enzyme detergent; oxygen bleach is safe.\n\n## Polyester\nWash at 40 C; chlorine bleach damages the fibre.\n\n## Satin\nWash at 60 C on the delicate programme; test a hidden seam first.\n\n(Scope note: silk is handled by the specialist vendor and this chart carries no silk row.)\n",
    "docs/vendor-guide-extract.md": "# Specialist vendor guide (extract)\n\nSilk items are collected separately and washed by the vendor; the vendor guide owns silk care and hotels do not launder silk in-house.\n",
}
check_guard(FILES_8018, {"README.md"})
W(
    "doc-8018",
    desc="Asks which wash programme the stain chart gives for silk; the chart carries no silk row (silk belongs to the specialist vendor) and the neighbouring satin row is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-stainchart-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "60"},
    axes=["DEC", "OBS"],
    files=FILES_8018,
    turns=[{
        "prompt": "A guest says her silk blouse got sauce on it and housekeeping asked which wash programme the chart gives for silk. What does it say?",
        "expect": {
            "output_contains": ["silk", "vendor"],
            "output_contains_any": ["not covered", "not listed", "no row", "no entry", "isn't covered", "routed", "outside the chart", "specialist"],
            "output_excludes": ["silk at 60", "60 C for silk", "use the satin", "satin programme for silk"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("Guest-laundry care documents")
chart = files["docs/stain-chart.md"]
rows = [l for l in chart.splitlines() if l.startswith("## ")]
assert "## Silk" not in rows
assert "## Satin" in rows and "no silk row" in chart
guide = files["docs/vendor-guide-extract.md"]
assert "Silk" in guide and "vendor" in guide
words = ["not covered", "not listed", "no row", "no entry", "isn't covered", "routed", "outside the chart", "specialist"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: docs/stain-chart.md has rows for cotton, polyester and satin only; the scope note says silk is handled by the specialist vendor and the chart carries no silk row.
- TR-DECOY: the chart does have a satin row with a 60 C delicate programme, one line above where silk would sit. Quoting a 60 C delicate programme for silk is the decoy answer; the guide says silk is collected and washed by the vendor.

## Reference solution
1. Read docs/stain-chart.md: cotton, polyester, satin rows; scope note says no silk row.
2. Read docs/vendor-guide-extract.md: silk is collected separately and washed by the specialist vendor.
Final answer (2-4 sentences): the stain chart has no row for silk - its scope note routes silk to the specialist vendor, and the vendor guide confirms silk is collected and washed off-site. The satin row in the chart is a different fabric and not silk guidance. Housekeeping should log the blouse for the vendor collection rather than wash it in-house. Criteria: mentions silk and the vendor/scope note, with a not-covered phrase; must not present a 60 C programme as silk guidance.

## Why the answer is unique
Satin is a different fabric whose 60 C delicate programme the chart explicitly scopes away from silk ("carries no silk row", "routed to the specialist vendor"). The vendor guide independently states silk is washed by the vendor, so no in-house programme exists to quote and the only correct reply says the chart does not cover silk and names the vendor route.
''',
)

# ================================================================ doc-8019
FILES_8019 = {
    "README.md": "Par-level handbook for the Riverside Hotel housekeeping contract. handbook/ holds the current edition; pending sections are logged at the end of the file.\n",
    "handbook/par-handbook.md": "# Linen par handbook, Riverside Hotel\n\n## Contents\n1 Bath towels  2 Flat sheets  3 Duvet covers  4 Bath mats\n\n## 1 Bath towels\nPar is 4 per occupied room: one on the rail, one in use, two in the drop.\n\n## 2 Flat sheets\nPar is 5 per occupied room.\n\n(Pending: section 3 Duvet covers awaits the floor supervisors' counts; this edition carries no duvet numbers.)\n",
    "handbook/floor-count-tracker.md": "# Floor count tracker\n\nDuvet cover room counts were collected on paper during the September inventory and are awaiting data entry by the housekeeping office.\n",
}
check_guard(FILES_8019, {"README.md"})
W(
    "doc-8019",
    desc="Asks the duvet cover par level from the hotel handbook; that section awaits the floor supervisors' counts and carries no duvet numbers, and the flat-sheet par is the decoy",
    task_type="policy_lookup", family="fam-doc-b10-parhandbook-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "5"},
    axes=["DEC", "OBS"],
    files=FILES_8019,
    turns=[{
        "prompt": "Riverside's executive housekeeper wants the duvet cover par level from the handbook for the room-rate letter. What par does it set?",
        "expect": {
            "output_contains": ["supervisors", "duvet"],
            "output_contains_any": ["pending", "awaits", "awaiting", "not set", "no number", "carries no", "no duvet"],
            "output_excludes": ["par is 5", "par of 5", "5 per occupied room"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("Par-level handbook")
hb = files["handbook/par-handbook.md"].splitlines()
sects = [l for l in hb if l.startswith("## ")]
assert "## 3 Duvet covers" not in sects and "awaits the floor supervisors" in "\\n".join(hb)
assert any("Par is 5" in l for l in hb)
tracker = files["handbook/floor-count-tracker.md"]
assert "awaiting data entry" in tracker
words = ["pending", "awaits", "awaiting", "not set", "no number", "carries no", "no duvet"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: handbook/par-handbook.md has sections for bath towels and flat sheets; the pending note says section 3 Duvet covers awaits the floor supervisors' counts and the edition carries no duvet numbers. The tracker confirms the counts are awaiting data entry.
- TR-DECOY: the handbook does set a flat-sheet par of 5 per occupied room, directly above where the duvet section would sit. Quoting 5 as the duvet par is the decoy answer.

## Reference solution
1. Read handbook/par-handbook.md: towel par 4, flat-sheet par 5; pending note says the duvet section awaits the floor supervisors' counts.
2. Read handbook/floor-count-tracker.md: duvet counts collected on paper, awaiting data entry.
Final answer (2-4 sentences): the handbook sets no duvet cover par yet - section 3 awaits the floor supervisors' counts and this edition carries no duvet numbers. The flat-sheet par of 5 in the same handbook is a different linen type and not the duvet level. The counts are awaiting data entry at the housekeeping office, so the par can be set once they are keyed in. Criteria: mentions duvet and a pending/not-set phrase; must not present 5 as the duvet par.

## Why the answer is unique
The flat-sheet par of 5 belongs to flat sheets; the handbook's pending note and the tracker both state the duvet section is waiting on the supervisors' counts, so no duvet par exists in the workspace. Any number would come from a different linen type and would be invented for the duvet.
''',
)

print("doc batch: %d cases" % len(WROTE))

# ================================================================ fs-8012
FILES_8012F = {
    "配方/登记表.txt": "配方 | 状态 | 负责 | 说明\n可颂 | 已归档 | 研发组 | 2026-05 定稿\n全麦吐司 | 已归档 | 研发组 | 2026-03 定稿\n碱水结 | 重制中 | 研发组 | 新版配方 9 月底归档，现无文件\n碱水面包卷 | 已归档 | 研发组 | 2024 年老配方，仍在售\n",
    "配方/可颂.yaml": "品名: 可颂\n面团含水量: 60%\n黄油: 片状 82%\n烤制: 200℃ 14 分钟\n",
    "配方/全麦吐司.yaml": "品名: 全麦吐司\n面团含水量: 68%\n烤制: 210℃ 25 分钟\n",
    "配方/碱水面包卷.yaml": "品名: 碱水面包卷\n面团含水量: 57%\n碱水浓度: 4%\n烤制: 210℃ 16 分钟\n",
    "README.md": "# 麦禾烘焙 配方库\n\n配方/ 按品名一个 yaml；归档状态看 配方/登记表.txt。\n",
}
check_guard(FILES_8012F, {"配方/登记表.txt"})
W(
    "fs-8012",
    desc="Asks where the standard recipe for the pretzel knot is; the recipe vault has no such file (the remake is still with R&D), the log says so, and the similarly named pretzel roll recipe is the decoy",
    task_type="find_file", family="fam-fs-b10-recipevault-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "配方/碱水面包卷.yaml"},
    axes=["DEC", "OBS"],
    files=FILES_8012F,
    turns=[{
        "prompt": "10 月新品要用碱水结的标准配方，告诉我配方文件在哪，我好用它核算成本。",
        "expect": {
            "output_contains": ["碱水结", "重制"],
            "output_contains_any": NEG_ZH + ["未归档", "还没归档", "重制中"],
            "output_excludes": ["配方文件是 配方/碱水面包卷", "碱水结的配方在 配方/碱水面包卷", "就是 配方/碱水面包卷", "用 配方/碱水面包卷.yaml 核算"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
log = files["配方/登记表.txt"].splitlines()
assert log[0] == "配方 | 状态 | 负责 | 说明"
status = {l.split(" | ")[0]: l.split(" | ")[1] for l in log[1:] if l.strip()}
assert status["碱水结"] == "重制中"
assert status["碱水面包卷"] == "已归档"
assert not any("碱水结" in p for p in files)
names = [p for p in files if p.startswith("配方/") and p.endswith(".yaml")]
assert any("碱水面包卷" in p for p in names)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "未归档", "还没归档", "重制中"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 配方/ 下没有碱水结的配方文件；配方/登记表.txt 写明碱水结「重制中，新版配方 9 月底归档，现无文件」，由研发组负责。
- TR-DECOY: 配方/碱水面包卷.yaml 名字与碱水结相近且已归档。登记表写明它是 2024 年的老配方、另一个品名，把它当碱水结的配方就是诱饵答案。

## Reference solution
1. 列出 配方/：可颂、全麦吐司、碱水面包卷三份 yaml 和 登记表.txt。
2. 读 配方/登记表.txt：碱水结重制中、尚无文件，碱水面包卷是另一品名的老配方。
终答（2-4 句）：配方库里没有碱水结的配方文件，登记表写明新版配方由研发组重制、9 月底才归档；名字相近的 配方/碱水面包卷.yaml 是另一个品名的 2024 年老配方，不能拿来核算新品成本。可以等归档后我再找，或先向研发组要试做版配方。判据：包含「碱水结」「重制」和一个否定/未归档说法，不得把碱水面包卷的路径当答案。

## Why the answer is unique
登记表把「碱水结」与「碱水面包卷」分列：前者重制中、现无文件，后者是仍在售的老品名。碱水面包卷.yaml 虽已归档，但品名与用途都对不上，工作区里不存在碱水结的配方，唯一正确的是说明缺文件、点名登记表口径并给出下一步。
''',
)

# ================================================================ fs-8013
FILES_8013 = {
    "检查表/2026-07-望京店.md": "# 望京店 7 月检查表\n\n卫生：合格\n设备：烤炉 B 门封待换\n",
    "检查表/2026-08-望京店.md": "# 望京店 8 月检查表\n\n卫生：合格\n设备：全部合格\n",
    "检查表/9月检查表-模板.md": "# 门店月度检查表（模板）\n\n卫生：\n设备：\n人员：\n（模板，未填写，不作为检查记录）\n",
    "检查表/登记说明.md": "# 检查表归档说明\n\n从 9 月起门店月度检查改在小程序填报，markdown 检查表不再归档；9 月记录请到运营小程序导出。\n",
    "README.md": "# 麦禾烘焙 门店运营资料\n\n检查表/ 存各月门店检查表，归档口径看 检查表/登记说明.md。\n",
}
check_guard(FILES_8013, {"README.md"})
W(
    "fs-8013",
    desc="Asks where the shop's September inspection sheet is; the folder has July and August sheets plus an unfilled template, the archiving note says September moved to the mini-programme, and the template is the decoy",
    task_type="find_file", family="fam-fs-b10-shopaudit-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "检查表/9月检查表-模板.md"},
    axes=["DEC", "OBS"],
    files=FILES_8013,
    turns=[{
        "prompt": "稽核组要调望京店 9 月的门店检查表，帮我找一下文件在哪。",
        "expect": {
            "output_contains": ["小程序"],
            "output_contains_any": NEG_ZH + ["不再归档", "模板"],
            "output_excludes": ["9月检查表-模板.md 就是", "检查表是 检查表/9月检查表-模板", "9 月检查表在 检查表/9月检查表-模板"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0] == "# 麦禾烘焙 门店运营资料"
note = files["检查表/登记说明.md"]
assert "小程序" in note and "不再归档" in note
sheets = [p for p in files if p.startswith("检查表/")]
assert "检查表/9月检查表-模板.md" in sheets
assert not any(p.startswith("检查表/2026-09") for p in files)
tpl = files["检查表/9月检查表-模板.md"]
assert "模板" in tpl and "未填写" in tpl
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "不再归档", "模板"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 检查表/ 下没有 2026-09 的检查表；检查表/登记说明.md 写明 9 月起门店月度检查改在小程序填报，markdown 检查表不再归档。
- TR-DECOY: 检查表/9月检查表-模板.md 名字带 9 月。它是未填写的模板、文末写明不作为检查记录，把它当 9 月检查表就是诱饵答案。

## Reference solution
1. 列出 检查表/：7 月、8 月两份检查表，一个 9 月模板和登记说明。
2. 读 检查表/登记说明.md：9 月起改小程序填报，markdown 不再归档。
3. （可选）确认 9月检查表-模板.md 未填写、不作为检查记录。
终答（2-4 句）：检查表目录里没有 9 月的检查表——登记说明写明 9 月起改在运营小程序填报，markdown 检查表不再归档；9月检查表-模板.md 是未填写的模板，不作为检查记录。可以让稽核组从运营小程序导出 9 月记录，导出后我可以帮你整理。判据：包含「小程序」和一个否定/不再归档说法，不得把模板当 9 月检查表。

## Why the answer is unique
模板文末写明「未填写，不作为检查记录」，名字带 9 月不改变它不是检查记录的事实；登记说明写明 9 月起不再归档 markdown 检查表，所以 9 月检查表在工作区里不存在，唯一正确的是说明改口径、点出模板不是记录并给出小程序导出的下一步。
''',
)

# ================================================================ fs-8014
FILES_8014F = {
    "服务单/台账.txt": "服务单 | 机器SN | 日期 | 说明\nSV-2026-0918-21078 | RS-21078 | 2026-09-18 | 换 PP 棉\nSV-2026-0902-21079 | RS-21079 | 2026-09-02 | 年度保养\nSV-2026-0821-21081 | RS-21081 | 2026-08-21 | 换 RO 膜\n- | RS-21087 | - | 经销商自服务，服务单留在经销商系统，未归档到这里\n",
    "服务单/SV-2026-0918-21078.md": "# 上门服务单 SV-2026-0918-21078\n\n机器：RS-21078\n内容：更换 PP 棉，进水压力复查合格。\n",
    "服务单/SV-2026-0902-21079.md": "# 上门服务单 SV-2026-0902-21079\n\n机器：RS-21079\n内容：年度保养。\n",
    "服务单/SV-2026-0821-21081.md": "# 上门服务单 SV-2026-0821-21081\n\n机器：RS-21081\n内容：更换 RO 膜。\n",
    "服务单/README.md": "# 服务单归档\n\n台账.txt 登记纸质服务单的归档情况；经销商自服务的机器服务单留在经销商系统，不在本目录。\n",
}
check_guard(FILES_8014F, {"服务单/台账.txt"})
W(
    "fs-8014",
    desc="Asks for the latest service call sheet for unit RS-21087; the folder has no sheet for it (the ledger says the dealer services it directly), and the near serial number RS-21078's sheet is the decoy",
    task_type="find_file", family="fam-fs-b10-servicecall-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "SV-2026-0918-21078"},
    axes=["DEC", "OBS"],
    files=FILES_8014F,
    turns=[{
        "prompt": "审计要 RS-21087 这台机器最近一次上门的服务单，帮我找一下文件。",
        "expect": {
            "output_contains": ["RS-21087", "经销商"],
            "output_contains_any": NEG_ZH + ["未归档", "没有归档", "留在经销商系统"],
            "output_excludes": ["服务单是 SV-2026-0918-21078", "RS-21087 的服务单是 SV-2026-0918", "SV-2026-0918-21078 是 RS-21087"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = files["服务单/台账.txt"].splitlines()
assert ledger[0] == "服务单 | 机器SN | 日期 | 说明"
rows = {l.split(" | ")[1]: l for l in ledger[1:] if l.strip()}
assert "RS-21087" in rows and "经销商" in rows["RS-21087"]
assert not any("RS-21087" in p for p in files if p.endswith(".md"))
assert any("21078" in p for p in files)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "未归档", "没有归档", "留在经销商系统"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 服务单/ 目录下没有 RS-21087 的服务单；服务单/台账.txt 写明 RS-21087 由经销商自服务，服务单留在经销商系统、未归档到这里。
- TR-DECOY: 台账里有 RS-21078 的服务单 SV-2026-0918-21078，SN 与 21087 只差两位。它是另一台机器的记录，把 RS-21078 的服务单当 RS-21087 的就是诱饵答案。

## Reference solution
1. 列出 服务单/：三份服务单 md 和 台账.txt。
2. 读 服务单/台账.txt：RS-21087 一行写明经销商自服务、服务单未归档到这里；RS-21078 是另一台机器。
终答（2-4 句）：服务单目录里没有 RS-21087 的服务单——台账写明这台机器由经销商自服务，服务单留在经销商系统、未归档到这里；台账里相近的 SV-2026-0918-21078 是 RS-21078 那台机器的记录，不是 RS-21087 的。审计需要的话要向经销商调取，拿到后我可以帮你归档。判据：包含「RS-21087」「经销商」和一个否定/未归档说法，不得把 RS-21078 的服务单当答案。

## Why the answer is unique
台账把 RS-21078 与 RS-21087 分列：前者有已归档的服务单，后者写明经销商自服务、未归档。SN 相近不改变机器不同的事实，工作区里不存在 RS-21087 的服务单，唯一正确的是说明台账口径、点出相近单号不是它并给出向经销商调取的下一步。
''',
)

# ================================================================ fs-8015
FILES_8015F = {
    "检测/批次台账.txt": "批次 | 报告文件 | 位置\nWR-2608A | WR-2608A-出厂检测.md | 检测/\nWR-2608B | WR-2608B-出厂检测.md | 检测/\nWR-2609A | - | 报告随货寄给客户，库内无存档\n",
    "检测/WR-2608A-出厂检测.md": "# WR-2608A 出厂检测\n\nTDS 去除率 96%，整机气密合格。\n",
    "检测/WR-2608B-出厂检测.md": "# WR-2608B 出厂检测\n\nTDS 去除率 95%，整机气密合格。\n",
    "README.md": "# 澄泉净水 出厂检测归档\n\n检测/ 按批次存出厂检测报告；随货寄给客户的批次库内不留存。\n",
}
check_guard(FILES_8015F, {"检测/批次台账.txt"})
W(
    "fs-8015",
    desc="Asks for the factory test report of batch WR-2609A; the folder has no report for it (the ledger says it shipped with the goods), and no decoy file carries that batch",
    task_type="find_file", family="fam-fs-b10-outwatertest-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"}, axes=["DEC"],
    files=FILES_8015F,
    turns=[{
        "prompt": "客户把 WR-2609A 批次机的报告弄丢了，想再要一份，帮我找一下这批的出厂检测报告。",
        "expect": {
            "output_contains": ["WR-2609A"],
            "output_contains_any": NEG_ZH + ["寄给客户", "无存档", "没有存档", "不留存"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = files["检测/批次台账.txt"].splitlines()
assert ledger[0] == "批次 | 报告文件 | 位置"
rows = {l.split(" | ")[0]: l for l in ledger[1:] if l.strip()}
assert "库内无存档" in rows["WR-2609A"]
assert not any("WR-2609A" in p for p in files if p != "检测/批次台账.txt")
assert any("WR-2608A" in p for p in files)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "寄给客户", "无存档", "没有存档", "不留存"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 检测/ 下没有 WR-2609A 的报告文件；检测/批次台账.txt 写明该批次「报告随货寄给客户，库内无存档」。

## Reference solution
1. 列出 检测/：WR-2608A、WR-2608B 两份报告和 批次台账.txt。
2. 读 检测/批次台账.txt：WR-2609A 一行写明报告随货寄给客户、库内无存档。
终答（2-4 句）：检测目录里没有 WR-2609A 的出厂检测报告，批次台账写明这批报告随货寄给了客户、库内无存档。可以请客户翻拍一份，或让质检按留样机补做一份检测记录，具体走哪条需要质检确认。判据：包含「WR-2609A」和一个否定/无存档说法。

## Why the answer is unique
台账里 WR-2608A/2608B 都有报告文件，唯独 WR-2609A 写明随货寄出、库内无存档，工作区里也不存在它的报告文件，所以唯一正确的是说明台账口径并给出补报告的下一步。
''',
)

# ================================================================ fs-8016
FILES_8016F = {
    "安装/台账.txt": "安装点 | 验收单 | 状态\n青云台一期 | - | 验收单客户方签章后未回传，工程组催办中\n青云台二期 | 安装/青云台二期-验收单.md | 已归档\n滨河雅苑 | 安装/滨河雅苑-验收单.md | 已归档\n",
    "安装/青云台二期-验收单.md": "# 安装验收单：青云台二期\n\n设备 6 台，出水 TDS 合格，客户签章齐全。\n",
    "安装/滨河雅苑-验收单.md": "# 安装验收单：滨河雅苑\n\n设备 3 台，出水 TDS 合格。\n",
    "README.md": "# 澄泉净水 安装资料\n\n安装/ 存各安装点验收单，归档状态看 安装/台账.txt。\n",
}
check_guard(FILES_8016F, {"安装/台账.txt"})
W(
    "fs-8016",
    desc="Asks for the acceptance sheet of the Qingyuntai phase-one install; the ledger says it is signed at the customer and not returned yet, and the phase-two sheet is the decoy",
    task_type="find_file", family="fam-fs-b10-installaccept-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "安装/青云台二期-验收单.md"},
    axes=["DEC", "OBS"],
    files=FILES_8016F,
    turns=[{
        "prompt": "青云台一期的物业要验收单复印件办进场手续，帮我找一下一期的验收单文件。",
        "expect": {
            "output_contains": ["青云台一期", "催办"],
            "output_contains_any": NEG_ZH + ["未回传", "没有回传"],
            "output_excludes": ["一期的验收单是 安装/青云台二期", "用 安装/青云台二期-验收单", "验收单就是 安装/青云台二期"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = files["安装/台账.txt"].splitlines()
assert ledger[0] == "安装点 | 验收单 | 状态"
rows = {l.split(" | ")[0]: l for l in ledger[1:] if l.strip()}
assert "未回传" in rows["青云台一期"]
assert "已归档" in rows["青云台二期"]
assert not any("青云台一期" in p for p in files if p != "安装/台账.txt")
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "未回传", "没有回传"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 安装/ 目录下没有青云台一期的验收单；安装/台账.txt 写明一期「验收单客户方签章后未回传，工程组催办中」。
- TR-DECOY: 台账里青云台二期的验收单已归档，安装点名字只差一期/二期。把二期的验收单当一期的就是诱饵答案。

## Reference solution
1. 列出 安装/：二期、滨河雅苑两份验收单和 台账.txt。
2. 读 安装/台账.txt：一期未回传、催办中；二期已归档但是另一期。
终答（2-4 句）：安装目录里没有青云台一期的验收单，台账写明一期的验收单在客户方签章后未回传、工程组催办中；目录里已归档的是青云台二期和滨河雅苑，二期不是一期。可以让物业先在客户方找原件，或催工程组跟进回传后再补复印件。判据：包含「青云台一期」「催办」和一个否定/未回传说法，不得把二期验收单当一期答案。

## Why the answer is unique
台账把一期与二期分列：二期已归档有文件，一期写明未回传。名字只差期数不改变安装点不同，工作区里不存在一期的验收单，唯一正确的是说明台账口径、点出二期不是它并给出催办的下一步。
''',
)

# ================================================================ fs-8017
FILES_8017F = {
    "certs/INDEX.txt": "week | certificate | note\n35 | certs/week-35-hygiene-certificate.md | scanned\n36 | certs/week-36-hygiene-certificate.md | scanned\n37 | certs/week-37-wash-certificate.md | general wash programme only\n37 hygiene | - | label printer ran the week; hygiene certificate not scanned yet, expected from the lab next week\n",
    "certs/week-35-hygiene-certificate.md": "# Week 35 hygiene wash certificate\n\nHarborview contract. 71 C wash, final rinse 82 C. Pass.\n",
    "certs/week-36-hygiene-certificate.md": "# Week 36 hygiene wash certificate\n\nHarborview contract. 71 C wash, final rinse 82 C. Pass.\n",
    "certs/week-37-wash-certificate.md": "# Week 37 wash certificate\n\nHarborview contract, general wash programme.\n",
    "certs/README.md": "Certificates for the Harborview contract. Hygiene wash certificates are issued per week by the lab; the general wash certificate does not substitute for the hygiene one.\n",
}
check_guard(FILES_8017F, {"certs/INDEX.txt"})
W(
    "fs-8017",
    desc="Asks for the week 37 hygiene wash certificate for the hotel audit; the index says it has not been scanned yet, the general week 37 wash certificate is the decoy",
    task_type="find_file", family="fam-fs-b10-washcert-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "certs/week-37-wash-certificate.md"},
    axes=["DEC", "OBS"],
    files=FILES_8017F,
    turns=[{
        "prompt": "The Harborview hotel's environmental health officer is on site and wants this week's (week 37) hygiene wash certificate. Where is the file?",
        "expect": {
            "output_contains": ["hygiene"],
            "output_contains_any": ["not scanned", "hasn't been scanned", "not yet scanned", "no hygiene certificate", "not issued", "pending", "next week"],
            "output_excludes": ["hygiene certificate is certs/week-37-wash", "use certs/week-37-wash", "hand over certs/week-37-wash"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["certs/INDEX.txt"].splitlines()
assert index[0] == "week | certificate | note"
body = "\\n".join(index[1:])
assert "not scanned yet" in body
assert "certs/week-37-wash-certificate.md" in body
assert not any(p.startswith("certs/week-37-hygiene") for p in files)
assert any(p.startswith("certs/week-36-hygiene") for p in files)
words = ["not scanned", "hasn't been scanned", "not yet scanned", "no hygiene certificate", "not issued", "pending", "next week"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: certs/ has no week 37 hygiene certificate; certs/INDEX.txt records "37 hygiene | - | hygiene certificate not scanned yet, expected from the lab next week".
- TR-DECOY: certs/week-37-wash-certificate.md is the only week 37 file, but it covers the general wash programme. The README states the general certificate does not substitute for the hygiene one; handing it over is the decoy answer.

## Reference solution
1. List certs/: week 35/36 hygiene certificates, a week 37 general wash certificate, INDEX.txt and README.
2. Read certs/INDEX.txt: week 37 hygiene not scanned yet, expected from the lab next week.
Final answer (2-4 sentences): there is no week 37 hygiene wash certificate in the folder - the index says it has not been scanned yet and is expected from the lab next week. The week 37 file that does exist is the general wash certificate, which the README says does not substitute for the hygiene one. Offer the officer the week 36 hygiene certificate as the most recent issued one, and pass on the lab copy when it arrives. Criteria: mentions week 37 hygiene plus a not-scanned/pending phrase; must not present the general certificate as the hygiene one.

## Why the answer is unique
The index distinguishes the general week 37 certificate from the hygiene one and states the hygiene certificate is not scanned yet; the README states the general one does not substitute. Weeks 35/36 hygiene certificates are older weeks, so the requested file does not exist and the only defensible reply names the gap, the substitute's limits, and the lab as the source.
''',
)

# ================================================================ fs-8018
FILES_8018F = {
    "sds/INDEX.txt": "product | sheet | status\nnovazyme-ex | - | distributor changed in August; new SDS requested 2026-09-05, not received yet\nnovazyme-ex-color | sds/novazyme-ex-color.md | on file (colour-care variant, different formulation)\ncitrus-wash | sds/citrus-wash.md | on file\n",
    "sds/novazyme-ex-color.md": "# Safety data sheet: Novazyme EX Color\n\nColour-care enzymatic detergent; keep off gallium surfaces.\n",
    "sds/citrus-wash.md": "# Safety data sheet: Citrus Wash\n\nSolvent booster; flammable, store at the bunded shelf.\n",
    "sds/README.md": "Safety data sheets for detergents in use at the plant. The index records what is on file; a changed formulation needs the new sheet from the distributor before the old one is quoted.\n",
}
check_guard(FILES_8018F, {"sds/INDEX.txt"})
W(
    "fs-8018",
    desc="Asks for the safety data sheet of the enzyme detergent Novazyme EX; the index says the distributor changed and the new SDS has not arrived, and the EX Color variant's sheet is the decoy",
    task_type="find_file", family="fam-fs-b10-sdsheet-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "sds/novazyme-ex-color.md"},
    axes=["DEC", "OBS"],
    files=FILES_8018F,
    turns=[{
        "prompt": "The auditor wants the safety data sheet for Novazyme EX, the enzyme detergent we dosed all summer. Where is its sheet?",
        "expect": {
            "output_contains": ["Novazyme EX", "distributor"],
            "output_contains_any": ["not received", "hasn't been received", "not yet received", "no sheet", "not on file", "pending"],
            "output_excludes": ["sheet is sds/novazyme-ex-color", "use sds/novazyme-ex-color", "novazyme-ex-color is the right"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["sds/INDEX.txt"].splitlines()
assert index[0] == "product | sheet | status"
body = "\\n".join(index[1:])
assert "not received yet" in body and "distributor changed" in body
assert not any(p.startswith("sds/novazyme-ex.") for p in files)
assert any(p.startswith("sds/novazyme-ex-color") for p in files)
words = ["not received", "hasn't been received", "not yet received", "no sheet", "not on file", "pending"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: sds/ has no sheet for Novazyme EX; sds/INDEX.txt records "distributor changed in August; new SDS requested 2026-09-05, not received yet".
- TR-DECOY: sds/novazyme-ex-color.md is on file and its name shares the "Novazyme EX" prefix. The index marks it a colour-care variant with a different formulation; quoting it as the EX sheet is the decoy answer.

## Reference solution
1. List sds/: two sheets on file and INDEX.txt.
2. Read sds/INDEX.txt: EX's distributor changed in August, the new SDS was requested on 2026-09-05 and has not arrived.
Final answer (2-4 sentences): there is no safety data sheet on file for Novazyme EX - the index says the distributor changed in August and the new sheet, requested on 2026-09-05, has not been received yet. The sheet named novazyme-ex-color is a colour-care variant with a different formulation and is not the EX sheet. The auditor can be given the index line as evidence of the pending request; the sheet itself has to come from the new distributor. Criteria: mentions the distributor and a not-received phrase; must not present the Color variant's sheet as the EX sheet.

## Why the answer is unique
The index separates novazyme-ex (no sheet, distributor changed) from novazyme-ex-color (on file, different formulation), and the README says a changed formulation needs the new sheet before the old one is quoted. The Color sheet's formulation differs, so it is not a defensible substitute and the only correct reply names the pending request.
''',
)

# ================================================================ fs-8019
FILES_8019F = {
    "vendors/INDEX.txt": "vendor | pack | status\nhallman-press | vendors/hallman-press-pack.md | on file\nklepp-tunnel | vendors/klepp-tunnel-pack.md | on file\nsommer-ironer | - | packs ship on request only; request sent 2026-09-28, nothing received yet\n",
    "vendors/hallman-press-pack.md": "# Hallman press installation pack\n\nFootprint, utilities and ventilation requirements for the H-120 press.\n",
    "vendors/klepp-tunnel-pack.md": "# Klepp tunnel installation pack\n\nLine layout, drainage and power requirements for the K-series tunnel.\n",
    "vendors/README.md": "Vendor packs for the plant 2 relocation. Packs are filed per vendor; some vendors ship on request only and stay logged here until the pack arrives.\n",
}
check_guard(FILES_8019F, {"vendors/INDEX.txt"})
W(
    "fs-8019",
    desc="Asks where the ironer vendor's installation pack is filed; the index says Sommer ships packs on request only and the 2026-09-28 request has brought nothing yet, with the other vendors' packs on file",
    task_type="find_file", family="fam-fs-b10-specpack-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"}, axes=["DEC"],
    files=FILES_8019F,
    turns=[{
        "prompt": "For the plant 2 move I need the ironer vendor's installation pack. Where is it filed?",
        "expect": {
            "output_contains": ["ommer", "ironer"],
            "output_contains_any": ["on request", "not received", "nothing received", "hasn't arrived", "not yet", "pending"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
index = files["vendors/INDEX.txt"].splitlines()
assert index[0] == "vendor | pack | status"
body = "\\n".join(index[1:])
assert "ship on request only" in body and "nothing received yet" in body
assert not any("sommer" in p.lower() for p in files if p.endswith(".md") and "INDEX" not in p)
assert any("hallman-press" in p for p in files)
words = ["on request", "not received", "nothing received", "hasn't arrived", "not yet", "pending"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-ABSENT: vendors/ has no pack for the ironer vendor; vendors/INDEX.txt records "sommer-ironer | - | packs ship on request only; request sent 2026-09-28, nothing received yet". The on-file packs belong to other vendors.

## Reference solution
1. List vendors/: two packs on file and INDEX.txt.
2. Read vendors/INDEX.txt: Sommer ships packs on request only; the request sent 2026-09-28 has brought nothing yet.
Final answer (2-4 sentences): there is no ironer pack in the folder - the index says Sommer ships packs on request only, and the request sent on 2026-09-28 has not produced anything yet. The packs on file are Hallman (press) and Klepp (tunnel), different vendors and equipment. Chasing Sommer for the pack, or checking the relocation deadline against their lead time, is the next step. Criteria: mentions Sommer/ironer and an on-request/nothing-received phrase.

## Why the answer is unique
The index explicitly lists sommer-ironer with no pack and a pending request, while the two on-file packs belong to other equipment; nothing in the workspace holds the ironer pack, so the only defensible reply names the gap and the chase-up step.
''',
)

import json as _json
import os as _os

from distill_paths import cases_dir as _cases_dir

zh = 0
for cid in WROTE:
    scen = {"cfg": "config", "log": "logs", "tab": "tabular", "doc": "docs", "fs": "filesystem"}[cid.split("-")[0]]
    path = _os.path.join(_cases_dir("v1.4"), scen, cid, "case.json")
    if not _os.path.exists(path):  # shelved after S5 (common.SHELVED)
        path = path.replace(_os.sep + "cases" + _os.sep, _os.sep + "cases-shelved" + _os.sep)
    case = _json.load(open(path))
    if any('\u4e00' <= ch <= '\u9fff' for ch in "".join(t.get("prompt", "") for t in case["turns"])):
        zh += 1
print("m2d done: %d cases, %d Chinese" % (len(WROTE), zh))
