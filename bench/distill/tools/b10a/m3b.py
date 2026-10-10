"""b10a (v1.4 §3.3 M3) single-turn explicit ban: the user says not to open
anything and the question itself is answerable from common knowledge, 50 items.

Shape follows the b10 pilot's nt-8001 / nt-8002 / nt-8003: one turn, expect is
NOCALL (tools: [] + require_active_no_call), the answer is a stable fact
(HTTP / cron / Git / units) or mental arithmetic within the §3.8 bounds.
doc/cfg cases carry decoy workspaces the user explicitly forbids opening; the
question never depends on them.

Themes: Chinese cases take proper names from a tea chain (沐棠茶饮) and a
pastry shop (麦丰面点坊); English cases from the Loomwork coworking space.
Run:
    cd bench/distill/tools/b10a && python3 m3b.py
"""
import re

from common import revised

write_case = revised({'nt-8016': '日期说法加「每月 1 号」：老师答「每月 1 号 18:30 执行」被词表漏判。', 'nt-8026': '权限说法加「可读可写」「只可读」「rw-r--r--」：老师答「属主可读可写、其他人只可读」被词表漏判。', 'cfg-8048': '加「零次或多次」：老师答「重复零次或多次」被词表漏判。', 'cfg-8049': '加「不支持」：老师答「标准 JSON 不支持注释」被词表漏判。', 'doc-8038': '判据由「6」加词元边界改为「6 天 / 6天 / 六天」：老师答「6天（…）」时「天」紧贴数字，被词元边界判挂。'})

NOCALL = {"tools": [], "require_active_no_call": True}

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def corruptible_numbers(text):
    """Mirror of bank verify's numberMatches: the standalone numbers Go's
    sabotage would consider (+1 on the first one equal to the judged value)."""
    out = []
    for m in NUM_RE.finditer(text):
        s, e = m.start(), m.end()
        if s > 0 and (text[s - 1].isalnum() or text[s - 1] in "_."):
            continue
        if e < len(text) and (text[e].isalnum() or text[e] in "_."):
            continue
        out.append(m.group())
    return out


def assert_value_absent(files, *values):
    """The judged value must not appear as a corruptible literal in any file,
    or the sabotage would corrupt a literal verify.py never reads and pass."""
    for path, content in files.items():
        for tok in corruptible_numbers(content):
            try:
                f = float(tok)
            except ValueError:
                continue
            for v in values:
                assert abs(f - v) > 0.01, ("value collision", path, tok, v)


def judged_numbers(*lists):
    """Mirror of caseExpectations: numbers the sabotage would hunt for, taken
    from output_contains / output_contains_any spellings."""
    out = []
    for lst in lists:
        for s in lst:
            clean = s.strip()
            try:
                out.append(float(clean))
                continue
            except ValueError:
                pass
            for fld in clean.split():
                try:
                    out.append(float(fld))
                except ValueError:
                    pass
    return out


TOOL_NAMES = ("list_files", "read_file", "search_text", "read_lines",
              "write_file", "replace_lines", "append_file", "calculator",
              "data_query", "datetime", "web_search", "web_fetch", "get_weather")
FORBIDDEN_PHRASES = ("without tools", "from memory", "quick", "simple",
                     "just", "carefully", "note that")


def check_prompt(prompt):
    low = prompt.lower()
    for word in TOOL_NAMES:
        assert word not in low, ("tool name in prompt", word)
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in low, ("forbidden phrase in prompt", phrase)


def readme_head(text):
    return text.splitlines()[0]


ZH_DOW = ["一", "二", "三", "四", "五", "六", "日"]


def zh_weekday_words(idx):
    if idx == 6:
        return ["周日", "星期日", "星期天", "礼拜天", "礼拜日"]
    return ["周" + ZH_DOW[idx], "星期" + ZH_DOW[idx], "礼拜" + ZH_DOW[idx]]


EN_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def en_weekday_words(idx):
    return [EN_DAYS[idx], EN_DAYS[idx][:3]]


ROMAN_VALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_value(s):
    total = 0
    for i, ch in enumerate(s):
        v = ROMAN_VALS[ch]
        if i + 1 < len(s) and ROMAN_VALS[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total


# ---------------------------------------------------------------- nt-8011
files_8011 = {
    "README.md": "# 沐棠茶饮 点单小程序运维说明\n\n线上接口报警以 值班/接口报警.md 的记录为准，处理前先对照当月值班表。\n",
    "值班/接口报警.md": "09:12 GET /menu 200\n09:15 GET /menu 200\n09:31 GET /coupons 500\n09:44 GET /stores 301\n",
}
p_8011 = "不用翻小程序的报警记录，直接告诉我：HTTP 404 和 403 这两个状态码分别是什么意思？"
check_prompt(p_8011)
assert_value_absent(files_8011, 404, 403)
write_case(
    "nt-8011",
    desc="Tea-chain order tablet workspace on screen, but the user says not to open the incident log and asks what HTTP 404 and 403 mean",
    task_type="concept", family="fam-nt-b10-tealeaf-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8011,
    turns=[{
        "prompt": p_8011,
        "expect": dict(NOCALL, output_contains=["404", "403"],
                       output_contains_any=["权限", "找不到", "不存在", "无权访问"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "404" in prompt and "403" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 点单小程序运维说明")
words = ["权限", "找不到", "不存在", "无权访问"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻报警记录，问的是通用概念。

## Reference solution
不调用任何工具，直接回答（2–3 句）：404 Not Found 是服务器找不到请求的资源（路径或条目不存在）；403 Forbidden 是服务器认出了请求但拒绝执行，即没有权限。可补一句排查方向：404 先看路径和参数，403 先看账号权限。判据：零调用，包含 404、403 和「权限/找不到/不存在」之一。

## Why the answer is unique
这是 HTTP 标准里的稳定定义，与工作区内容无关；用户显式禁止翻文件，所以任何工具调用都是违背指令。
''',
)

# ---------------------------------------------------------------- nt-8012
files_8012 = {
    "README.md": "# 沐棠茶饮 门店终端运维\n\n终端异常先看 运维/发布记录.md，再按值班组排的顺序升级。\n",
    "运维/发布记录.md": "- 9 月 12 日 晚间发布点单小程序新版本，随后一切正常\n- 9 月 26 日 凌晨例行维护，未影响营业\n",
}
p_8012 = "别查了，直接说：接口返回 503 一般是什么情况？"
check_prompt(p_8012)
assert_value_absent(files_8012, 503)
write_case(
    "nt-8012",
    desc="Tea-chain ops workspace available, but the user forbids checking and asks what an HTTP 503 response indicates",
    task_type="concept", family="fam-nt-b10-tealeaf-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8012,
    turns=[{
        "prompt": p_8012,
        "expect": dict(NOCALL, output_contains=["503"],
                       output_contains_any=["不可用", "过载", "维护", "暂时"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "503" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端运维")
words = ["不可用", "过载", "维护", "暂时"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，问的是通用概念。

## Reference solution
不调用任何工具，直接回答（1–2 句）：503 Service Unavailable 表示服务端暂时无法处理请求，常见原因是过载、停机维护或上游不可用，通常稍后重试。判据：零调用，包含 503 和「不可用/过载/维护/暂时」之一。

## Why the answer is unique
503 的含义是 HTTP 标准定义，稳定不变；工作区里的发布记录与问题无关，用户也明确禁止查看。
''',
)

# ---------------------------------------------------------------- nt-8013
files_8013 = {
    "README.md": "# Loomwork front-of-house tablet\n\nError reports from the booking tablet are collected in ops/incident-notes.md.\n",
    "ops/incident-notes.md": "Mon: booking sync OK\nTue: payment step failed once, retried fine\n",
}
p_8013 = "No need to open anything: in plain terms, what does HTTP status 429 tell the caller, and how is that different from 401?"
check_prompt(p_8013)
assert_value_absent(files_8013, 429, 401)
write_case(
    "nt-8013",
    desc="Coworking booking-tablet workspace on screen, but the user forbids opening anything and asks what HTTP 429 means versus 401",
    task_type="concept", family="fam-nt-b10-tealeaf-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8013,
    turns=[{
        "prompt": p_8013,
        "expect": dict(NOCALL, output_contains=["429", "401"],
                       output_contains_any=["too many", "rate limit", "rate limited",
                                            "unauthorized", "credentials", "not authenticated"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "429" in prompt and "401" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-of-house tablet")
words = ["too many", "rate limit", "rate limited", "unauthorized", "credentials", "not authenticated"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- None. The user forbids opening anything; the question is a stable HTTP definition.

## Reference solution
No tool call. Answer in 2-3 sentences: 429 Too Many Requests means the caller has sent too many requests in a given window and is being rate limited, so it should slow down or back off; 401 Unauthorized means the request lacks valid credentials, so the caller must authenticate first. Criteria: zero calls, contains 429 and 401 plus a rate/too-many phrase.

## Why the answer is unique
Both meanings are fixed by the HTTP standard and independent of the workspace; the user explicitly banned opening anything.
''',
)

# ---------------------------------------------------------------- nt-8014
files_8014 = {
    "README.md": "# 沐棠茶饮 门店后台定时任务\n\n下表由运维组维护；表达式改动的审批记录在 运维/变更登记.md。\n",
    "运维/定时任务.md": "任务            表达式\n同步会员积分   0 6 * * *\n生成日结报表   0 23 * * *\n提醒物料补货   0 7 * * 3\n",
}
p_8014 = "不用翻运维清单，直接告诉我：门店后台的 cron 表达式 `15 9 * * 1-5` 是什么意思？"
check_prompt(p_8014)
assert_value_absent(files_8014, *judged_numbers(["9:15"], ["周一到周五", "周一至周五", "星期一到星期五", "星期一至星期五", "工作日"]))
write_case(
    "nt-8014",
    desc="Tea-chain scheduled-jobs workspace available, but the user says not to open it and asks what the cron expression 15 9 * * 1-5 schedules",
    task_type="concept", family="fam-nt-b10-oolong-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8014,
    turns=[{
        "prompt": p_8014,
        "expect": dict(NOCALL, output_contains=["9:15"],
                       output_contains_any=["周一到周五", "周一至周五", "星期一到星期五", "星期一至星期五", "工作日"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("15", "9", "*", "*", "1-5")
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店后台定时任务")
print(json.dumps({"expected_contains_any": ["周一到周五", "周一至周五", "星期一到星期五", "星期一至星期五", "工作日"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻运维清单，考的是 cron 标准语法。

## Reference solution
不调用任何工具，直接回答（1–2 句）：五个字段依次是分、时、日、月、周，即工作日（周一到周五）每天 09:15 执行一次。判据：零调用，包含 9:15 和「周一到周五/工作日」之一。

## Why the answer is unique
五段式 cron 的字段顺序和 1-5 表示周一到周五都是标准语法，答案唯一；运维清单是诱饵，用户明确禁止查看。
''',
)

# ---------------------------------------------------------------- nt-8015
files_8015 = {
    "README.md": "# Loomwork back office\n\nScheduled jobs are listed in ops/scheduled-jobs.md; changes go through the ops rota.\n",
    "ops/scheduled-jobs.md": "job                schedule\nfridge temp check  0 6 * * *\nbin day reminder   0 8 * * 5\n",
}
p_8015 = "No need to open anything for this one: what schedule does the cron expression `0 22 * * 0` describe?"
check_prompt(p_8015)
assert_value_absent(files_8015, *judged_numbers(["Sunday"], ["22:00", "10 PM", "10 pm", "10pm", "10:00 PM", "10:00 pm"]))
write_case(
    "nt-8015",
    desc="Coworking scheduled-jobs workspace on screen, but the user forbids opening it and asks what the cron expression 0 22 * * 0 schedules",
    task_type="concept", family="fam-nt-b10-oolong-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8015,
    turns=[{
        "prompt": p_8015,
        "expect": dict(NOCALL, output_contains=["Sunday"],
                       output_contains_any=["22:00", "10 PM", "10 pm", "10pm", "10:00 PM", "10:00 pm"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("0", "22", "*", "*", "0")
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork back office")
print(json.dumps({"expected_contains_any": ["22:00", "10 PM", "10 pm", "10pm", "10:00 PM", "10:00 pm"]}))
''',
    notes='''
## Traps
- None. Stable cron syntax; the jobs list is a decoy the user forbids opening.

## Reference solution
No tool call. Answer in 1-2 sentences: fields are minute, hour, day-of-month, month, day-of-week, so it runs at 22:00 (10 PM) every Sunday; 0 in the day-of-week field means Sunday. Criteria: zero calls, contains Sunday and the time as 22:00 or 10 PM.

## Why the answer is unique
Standard five-field cron: 0 = Sunday, 22 = the 10 PM hour. The answer is fully determined by the expression in the prompt.
''',
)

# ---------------------------------------------------------------- nt-8016
p_8016 = "别查了，直接说：定时任务 `30 18 1 * *` 是什么意思？"
check_prompt(p_8016)
write_case(
    "nt-8016",
    desc="User forbids looking anything up and asks what the cron expression 30 18 1 * * schedules",
    task_type="concept", family="fam-nt-b10-oolong-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8016,
        "expect": dict(NOCALL, output_contains=["18:30"],
                       output_contains_any=["每月 1 日", "每月1日", "每个月的 1 日", "每月一号", "每个月的一号", "月初第一天", "每月 1 号", "每月1号", "每个月 1 号", "每个月1号"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("30", "18", "1", "*", "*")
print(json.dumps({"expected_contains_any": ["每月 1 日", "每月1日", "每个月的 1 日", "每月一号", "每个月的一号", "月初第一天", "每月 1 号", "每月1号", "每个月 1 号", "每个月1号"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，考的是 cron 标准语法。

## Reference solution
不调用任何工具，直接回答（1–2 句）：字段是分、时、日、月、周，即每个月 1 日 18:30 执行一次，与星期无关。判据：零调用，包含 18:30 和「每月 1 日」类说法。

## Why the answer is unique
第三段写死为 1 表示每月 1 号触发，其余字段用通配，答案由表达式唯一确定。
''',
)

# ---------------------------------------------------------------- nt-8017
p_8017 = "沐棠茶饮进了一批纸杯，共 4 打——一打 12 个。不用调工具，口算一共是多少个纸杯？"
check_prompt(p_8017)
write_case(
    "nt-8017",
    desc="Mental-arithmetic dozen conversion for a tea-chain supply order, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-jasmine-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8017,
        "expect": dict(NOCALL, output_contains=["48"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
dozens = int(re.search(r"共 (\\d+) 打", prompt).group(1))
per = int(re.search(r"一打 (\\d+) 个", prompt).group(1))
print(json.dumps({"expected_number": dozens * per}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，口算可完成（4 × 12）。

## Reference solution
不调用任何工具：4 打 × 12 个/打 = 48 个。终答 1 句给出 48。判据：零调用，包含 48。

## Why the answer is unique
一打就是 12 个，乘法只有一种读法；题目没有折扣、损耗等其他口径。
''',
)

# ---------------------------------------------------------------- nt-8018
p_8018 = "麦丰面点坊的新品培训安排 3 周，一周按 7 天算。不用调工具，直接告诉我一共多少天？"
check_prompt(p_8018)
write_case(
    "nt-8018",
    desc="Mental week-to-days conversion for a pastry-shop training plan, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-jasmine-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8018,
        "expect": dict(NOCALL, output_contains=["21"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
weeks = int(re.search(r"(\\d+) 周", prompt).group(1))
days_per = int(re.search(r"一周按 (\\d+) 天", prompt).group(1))
print(json.dumps({"expected_number": weeks * days_per}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，口算可完成（3 × 7）。

## Reference solution
不调用任何工具：3 周 × 7 天/周 = 21 天。判据：零调用，包含 21。

## Why the answer is unique
一周 7 天是固定事实，乘法唯一；题目没有给休息日等其他口径。
''',
)

# ---------------------------------------------------------------- nt-8019
p_8019 = "No need to open anything — mental math: the Loomwork pantry restock bought 9 packs of tea with 6 bags in each pack. How many bags is that in total?"
check_prompt(p_8019)
write_case(
    "nt-8019",
    desc="Mental multiplication for a coworking pantry restock, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-jasmine-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8019,
        "expect": dict(NOCALL, output_contains=["54"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
packs = int(re.search(r"(\\d+) packs", prompt).group(1))
per = int(re.search(r"(\\d+) bags in each pack", prompt).group(1))
print(json.dumps({"expected_number": packs * per}))
''',
    notes='''
## Traps
- None. Mental arithmetic within bounds (9 x 6); the user declines tool use.

## Reference solution
No tool call: 9 packs x 6 bags = 54 bags. Criteria: zero calls, contains 54.

## Why the answer is unique
One multiplication, no other reading of the quantities is possible.
''',
)

# ---------------------------------------------------------------- nt-8020
p_8020 = "不用调工具，帮我口算：桂花乌龙原价 85 元，打八折后是多少钱？"
check_prompt(p_8020)
write_case(
    "nt-8020",
    desc="Mental 20-percent-off price for a tea-chain drink, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-bergamot-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8020,
        "expect": dict(NOCALL, output_contains=["68"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "八折" in prompt
price = int(re.search(r"原价 (\\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": price * 8 // 10}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，口算可完成（85 的两成是 17，85 − 17 = 68）。

## Reference solution
不调用任何工具：八折即原价的 80%，85 × 0.8 = 68 元。判据：零调用，包含 68。

## Why the answer is unique
八折对应 80%，没有叠加会员价等其他口径，答案唯一。
''',
)

# ---------------------------------------------------------------- nt-8021
p_8021 = "别查了，直接算：鲜奶咖啡一杯 24 元，现在第二杯半价，买两杯一共要付多少元？"
check_prompt(p_8021)
write_case(
    "nt-8021",
    desc="Mental second-item-half-price total for a tea-chain order, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-bergamot-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8021,
        "expect": dict(NOCALL, output_contains=["36"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "第二杯半价" in prompt
price = int(re.search(r"一杯 (\\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": price + price // 2}))
''',
    notes='''
## Traps
- None. 用户明确说别查，口算可完成（24 + 12 = 36）。

## Reference solution
不调用任何工具：第一杯原价 24 元，第二杯半价 12 元，合计 36 元。判据：零调用，包含 36。

## Why the answer is unique
第二杯半价的口径明确（半价只作用在第二杯），两杯总价唯一。
''',
)

# ---------------------------------------------------------------- nt-8022
p_8022 = "No need to open anything — mental math: the Loomwork day pass is 40 dollars and members get 25% off. What does a member pay?"
check_prompt(p_8022)
write_case(
    "nt-8022",
    desc="Mental 25-percent-off day pass for a coworking space, tool use explicitly declined",
    task_type="unit_convert", family="fam-nt-b10-bergamot-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8022,
        "expect": dict(NOCALL, output_contains=["30"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
price = int(re.search(r"pass is (\\d+) dollars", prompt).group(1))
pct = int(re.search(r"(\\d+)% off", prompt).group(1))
print(json.dumps({"expected_number": price - price * pct // 100}))
''',
    notes='''
## Traps
- None. Mental arithmetic within bounds (a quarter of 40 is 10); tool use declined.

## Reference solution
No tool call: 25% of 40 is 10, so a member pays 40 - 10 = 30 dollars. Criteria: zero calls, contains 30.

## Why the answer is unique
The discount base is the list price and there is no other fee, so the member price is unique.
''',
)

# ---------------------------------------------------------------- nt-8023
files_8023 = {
    "README.md": "# 沐棠茶饮 拓展组速览\n\n海外门店的筹备节点见 拓展/海外筹备.md。\n",
    "拓展/海外筹备.md": "- 东京出张所：菜单本地化进行中\n- 吉隆坡合资店：装修报价已回收\n",
}
p_8023 = "不用翻资料，直接告诉我：东京在 UTC+9，北京在 UTC+8。北京晚上 8 点的时候，东京是几点？"
check_prompt(p_8023)
assert_value_absent(files_8023, 21, 9)
write_case(
    "nt-8023",
    desc="Tea-chain overseas-expansion workspace on screen, but the user forbids opening it and asks the Tokyo time when Beijing is 8 PM, offsets given",
    task_type="concept", family="fam-nt-b10-matcha-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8023,
    turns=[{
        "prompt": p_8023,
        "expect": dict(NOCALL, output_contains_any=["21:00", "21 点", "21点", "21 时", "晚上 9 点", "晚上9点", "晚上九点"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\\+(\\d+)", prompt)
m = re.search(r"(上午|下午|晚上) (\\d+) 点", prompt)
base = int(m.group(2))
if m.group(1) != "上午" and base < 12:
    base += 12
hour = base + (int(offs[0]) - int(offs[1]))
assert hour == 21
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 拓展组速览")
print(json.dumps({"expected_contains_any": ["21:00", "21 点", "21点", "21 时", "晚上 9 点", "晚上9点", "晚上九点"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 两个时区偏移都写在题面里，做一次加减即可；用户明确说不用翻资料。

## Reference solution
不调用任何工具：东京比北京快 1 小时，北京 20 点时东京是 21 点（21:00）。判据：零调用，包含 21:00、「21 点」或「晚上 9 点」之一。

## Why the answer is unique
UTC+9 与 UTC+8 都由题面给定，差值固定为 1 小时，同日之内推算唯一。
''',
)

# ---------------------------------------------------------------- nt-8024
files_8024 = {
    "README.md": "# Loomwork studios\n\nOverseas studio handovers live in studios/overseas.md.\n",
    "studios/overseas.md": "Dubai: fit-out signed\nTokyo: desk delivery booked\n",
}
p_8024 = "No need to open anything: our Dubai studio runs UTC+4 and Tokyo runs UTC+9. It is 09:00 in Dubai right now — what time is it in Tokyo?"
check_prompt(p_8024)
write_case(
    "nt-8024",
    desc="Coworking overseas-studios workspace available but forbidden; the user gives both UTC offsets and asks the Tokyo time when Dubai is 09:00",
    task_type="concept", family="fam-nt-b10-matcha-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8024,
    turns=[{
        "prompt": p_8024,
        "expect": dict(NOCALL, output_contains_any=["14:00", "2:00 PM", "2:00 pm", "2:00pm", "2 PM", "2 pm", "2pm"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\\+(\\d+)", prompt)
base = int(re.search(r"It is (\\d+):00", prompt).group(1))
hour = base + (int(offs[1]) - int(offs[0]))
assert hour == 14
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork studios")
print(json.dumps({"expected_contains_any": ["14:00", "2:00 PM", "2:00 pm", "2:00pm", "2 PM", "2 pm", "2pm"]}))
''',
    notes='''
## Traps
- None. Both offsets are stated in the prompt; one subtraction is enough.

## Reference solution
No tool call: Tokyo is 5 hours ahead of Dubai (UTC+9 vs UTC+4), so 09:00 in Dubai is 14:00 (2:00 PM) in Tokyo. Criteria: zero calls, contains 14:00 or 2 PM.

## Why the answer is unique
The offsets come from the prompt itself and both zones are given, so the converted time is unique and stays on the same day.
''',
)

# ---------------------------------------------------------------- nt-8025
files_8025 = {
    "README.md": "# 沐棠茶饮 中东筹备\n\n迪拜快闪店的筹备进度见 拓展/迪拜快闪.md。\n",
    "拓展/迪拜快闪.md": "- 场地押金已付\n- 菜单已送审\n",
}
p_8025 = "别查了，直接算：北京在 UTC+8，迪拜在 UTC+4。北京晚上 11 点的时候，迪拜是几点？"
check_prompt(p_8025)
assert_value_absent(files_8025, 19, 7)
write_case(
    "nt-8025",
    desc="Tea-chain Dubai pop-up workspace available but forbidden; the user gives both UTC offsets and asks the Dubai time when Beijing is 11 PM",
    task_type="concept", family="fam-nt-b10-matcha-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8025,
    turns=[{
        "prompt": p_8025,
        "expect": dict(NOCALL, output_contains_any=["19:00", "19 点", "19点", "19 时", "晚上 7 点", "晚上7点", "晚上七点"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\\+(\\d+)", prompt)
m = re.search(r"(上午|下午|晚上) (\\d+) 点", prompt)
base = int(m.group(2))
if m.group(1) != "上午" and base < 12:
    base += 12
hour = base + (int(offs[1]) - int(offs[0]))
assert hour == 19
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 中东筹备")
print(json.dumps({"expected_contains_any": ["19:00", "19 点", "19点", "19 时", "晚上 7 点", "晚上7点", "晚上七点"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 两个偏移都在题面里，迪拜比北京慢 4 小时；用户明确说别查。

## Reference solution
不调用任何工具：迪拜比北京慢 4 小时，北京 23 点时迪拜是 19 点（19:00，当天晚上 7 点）。判据：零调用，包含 19:00、「19 点」或「晚上 7 点」之一。

## Why the answer is unique
UTC+8 与 UTC+4 均由题面给定，23 − 4 = 19，同日之内答案唯一。
''',
)

# ---------------------------------------------------------------- nt-8026
files_8026 = {
    "README.md": "# 沐棠茶饮 门店终端管理手册\n\n终端镜像与脚本的改动都要走 运维/审批单.md 的流程。\n",
    "运维/审批单.md": "- 更新收银小票模板：待店长会签\n- 调整后厨打印机：已通过\n",
}
p_8026 = "不用翻手册，直接讲：Linux 里 chmod 644 是什么意思？"
check_prompt(p_8026)
assert_value_absent(files_8026, 644)
write_case(
    "nt-8026",
    desc="Tea-chain device-manual workspace on screen, but the user forbids opening it and asks what chmod 644 means",
    task_type="concept", family="fam-nt-b10-tapioca-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8026,
    turns=[{
        "prompt": p_8026,
        "expect": dict(NOCALL, output_contains=["644"],
                       output_contains_any=["读写", "只读", "可读可写", "只可读", "rw-r--r--"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "644" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端管理手册")
print(json.dumps({"expected_contains_any": ["读写", "只读", "可读可写", "只可读", "rw-r--r--"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻手册，考的是文件权限的稳定含义。

## Reference solution
不调用任何工具，直接回答（1–2 句）：644 表示所有者可读可写，同组用户和其他用户只可读，即 rw-r--r--。判据：零调用，包含 644 和「读写/只读」。

## Why the answer is unique
三位八进制权限的定义是固定的：6=rw-，4=r--；与工作区内容无关。
''',
)

# ---------------------------------------------------------------- nt-8027
files_8027 = {
    "README.md": "# 沐棠茶饮 门店终端管理手册\n\n终端镜像与脚本的改动都要走 运维/审批单.md 的流程。\n",
    "运维/审批单.md": "- 更新收银小票模板：待店长会签\n- 调整后厨打印机：已通过\n",
}
p_8027 = "别查了，直接说：`git fetch` 和 `git pull` 的区别是什么？"
check_prompt(p_8027)
write_case(
    "nt-8027",
    desc="Tea-chain device-manual workspace available but forbidden; the user asks how git fetch differs from git pull",
    task_type="concept", family="fam-nt-b10-tapioca-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8027,
    turns=[{
        "prompt": p_8027,
        "expect": dict(NOCALL, output_contains=["fetch"],
                       output_contains_any=["合并", "merge", "拉取并合并"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "git fetch" in prompt and "git pull" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店终端管理手册")
print(json.dumps({"expected_contains_any": ["合并", "merge", "拉取并合并"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，考的是 Git 的稳定概念。

## Reference solution
不调用任何工具，直接回答（1–2 句）：fetch 只把远端的最新提交下载到本地仓库，不动当前分支；pull 相当于 fetch 之后再把远端分支合并（merge）进当前分支。判据：零调用，包含 fetch 和「合并/merge」。

## Why the answer is unique
fetch 与 pull 的关系是 Git 的固定语义，答案唯一；管理手册与问题无关。
''',
)

# ---------------------------------------------------------------- nt-8028
files_8028 = {
    "README.md": "# Loomwork member portal\n\nLaptop and badge setup steps are in ops/onboarding.md.\n",
    "ops/onboarding.md": "New starters get laptop and badge on day one.\n",
}
p_8028 = "No need to open anything: what does the octal permission 755 allow, and for whom?"
check_prompt(p_8028)
assert_value_absent(files_8028, 755)
write_case(
    "nt-8028",
    desc="Coworking onboarding workspace available but forbidden; the user asks what octal permission 755 allows",
    task_type="concept", family="fam-nt-b10-tapioca-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8028,
    turns=[{
        "prompt": p_8028,
        "expect": dict(NOCALL, output_contains=["755"],
                       output_contains_any=["execute", "read", "write"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "755" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork member portal")
print(json.dumps({"expected_contains_any": ["execute", "read", "write"]}))
''',
    notes='''
## Traps
- None. A stable permission definition; the user forbids opening anything.

## Reference solution
No tool call. Answer in 1-2 sentences: 755 is rwxr-xr-x — the owner may read, write and execute, while the group and everyone else may read and execute but not write. Criteria: zero calls, contains 755 and an execute/read phrase.

## Why the answer is unique
Each octal digit maps to a fixed rwx triple (7=rwx, 5=r-x); the meaning does not depend on the workspace.
''',
)

# ---------------------------------------------------------------- nt-8029
files_8029 = {
    "README.md": "# 麦丰面点坊 门店系统速查\n\n系统名词的写法以总部的 用语规范.md 为准。\n",
    "总部/用语规范.md": "- 对顾客统一称「取餐号」，不用「订单号」\n- 门店群公告不用表情符号\n",
}
p_8029 = "不用查资料，直接说：URL 指的是什么？"
check_prompt(p_8029)
write_case(
    "nt-8029",
    desc="Pastry-shop system glossary workspace available but forbidden; the user asks what URL stands for",
    task_type="concept", family="fam-nt-b10-pomelo-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8029,
    turns=[{
        "prompt": p_8029,
        "expect": dict(NOCALL, output_contains=["URL"],
                       output_contains_any=["统一资源定位", "网址", "地址"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "URL" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 门店系统速查")
print(json.dumps({"expected_contains_any": ["统一资源定位", "网址", "地址"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用查资料，问的是稳定缩写。

## Reference solution
不调用任何工具，直接回答（1 句）：URL 是 Uniform Resource Locator 的缩写，即统一资源定位符，俗称网址，用来定位网络上的资源。判据：零调用，包含 URL 和「统一资源定位/网址」之一。

## Why the answer is unique
URL 的全称和含义是稳定事实，与工作区内容无关。
''',
)

# ---------------------------------------------------------------- nt-8030
files_8030 = {
    "README.md": "# Loomwork member portal\n\nWording for member-facing screens follows brand/voice.md.\n",
    "brand/voice.md": "Say book a desk, not reserve a unit.\n",
}
p_8030 = "No need to open anything: what does the acronym API stand for?"
check_prompt(p_8030)
write_case(
    "nt-8030",
    desc="Coworking brand-voice workspace available but forbidden; the user asks what API stands for",
    task_type="concept", family="fam-nt-b10-pomelo-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_8030,
    turns=[{
        "prompt": p_8030,
        "expect": dict(NOCALL, output_contains=["API"],
                       output_contains_any=["Application Programming Interface",
                                            "application programming interface"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "API" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork member portal")
print(json.dumps({"expected_contains_any": ["Application Programming Interface", "application programming interface"]}))
''',
    notes='''
## Traps
- None. A stable acronym; the user forbids opening anything.

## Reference solution
No tool call. Answer in one sentence: API stands for Application Programming Interface, the contract through which programs talk to each other. Criteria: zero calls, contains API and the full expansion.

## Why the answer is unique
The expansion is a fixed fact, independent of the workspace.
''',
)

# ---------------------------------------------------------------- nt-8031
p_8031 = "别查了，直接告诉我：CSV 是什么的缩写，这种文件长什么样？"
check_prompt(p_8031)
write_case(
    "nt-8031",
    desc="User forbids looking anything up and asks what CSV stands for and what such a file looks like",
    task_type="concept", family="fam-nt-b10-pomelo-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8031,
        "expect": dict(NOCALL, output_contains=["CSV"],
                       output_contains_any=["逗号分隔", "逗号分隔值", "Comma-Separated", "Comma Separated", "comma-separated"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "CSV" in prompt
print(json.dumps({"expected_contains_any": ["逗号分隔", "逗号分隔值", "Comma-Separated", "Comma Separated", "comma-separated"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，问的是稳定缩写。

## Reference solution
不调用任何工具，直接回答（1–2 句）：CSV 是 Comma-Separated Values 的缩写，即逗号分隔值；文件里每行一条记录，字段之间用逗号隔开，第一行常是表头。判据：零调用，包含 CSV 和「逗号分隔」类说法。

## Why the answer is unique
缩写全称与文件形态都是稳定事实，答案唯一。
''',
)

# ---------------------------------------------------------------- nt-8032
p_8032 = "不用调工具，算完把算式写出来：进货 12 箱椰乳，每箱 8 罐，路上破了 5 罐，还剩多少罐？"
check_prompt(p_8032)
write_case(
    "nt-8032",
    desc="Two-step mental arithmetic for a tea-chain delivery (multiply, then subtract), expression demanded, tool use declined",
    task_type="unit_convert", family="fam-nt-b10-steamer-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8032,
        "expect": dict(NOCALL, output_contains=["91"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
boxes = int(re.search(r"(\\d+) 箱", prompt).group(1))
per = int(re.search(r"每箱 (\\d+) 罐", prompt).group(1))
broken = int(re.search(r"破了 (\\d+) 罐", prompt).group(1))
print(json.dumps({"expected_number": boxes * per - broken}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，两步口算（12 × 8 = 96，96 − 5 = 91）可完成。

## Reference solution
不调用任何工具：12 × 8 = 96 罐，减去破损的 5 罐，剩 91 罐；终答写出算式 12 × 8 − 5 = 91。判据：零调用，包含 91。

## Why the answer is unique
先乘后减的口径由题面写死（破损从到货总量里扣），答案唯一。
''',
)

# ---------------------------------------------------------------- nt-8033
p_8033 = "帮我口算并写明算式，不用调工具：麦丰面点坊上午烤了 36 个豆沙包，下午烤了 27 个，每 7 个装一袋，能装满几袋？"
check_prompt(p_8033)
write_case(
    "nt-8033",
    desc="Two-step mental arithmetic for a pastry shop (add the two batches, then divide), expression demanded, tool use declined",
    task_type="unit_convert", family="fam-nt-b10-steamer-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8033,
        "expect": dict(NOCALL, output_contains=["9"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
am = int(re.search(r"上午烤了 (\\d+) 个", prompt).group(1))
pm = int(re.search(r"下午烤了 (\\d+) 个", prompt).group(1))
per = int(re.search(r"每 (\\d+) 个装一袋", prompt).group(1))
print(json.dumps({"expected_number": (am + pm) // per}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，两步口算（36 + 27 = 63，63 ÷ 7 = 9）可完成。

## Reference solution
不调用任何工具：全天共 36 + 27 = 63 个，63 ÷ 7 = 9，能装满 9 袋；终答写出算式。判据：零调用，包含 9。

## Why the answer is unique
「装满」意味着只算整袋，63 正好除尽，没有余数歧义。
''',
)

# ---------------------------------------------------------------- nt-8034
p_8034 = "不用调工具，写出算式：沐棠茶饮的包场费 90 元，来了 12 位同事、每人出 8 元，收齐之后还剩几元？"
check_prompt(p_8034)
write_case(
    "nt-8034",
    desc="Two-step mental arithmetic for a tea-chain room booking (multiply contributions, then subtract the fee), expression demanded",
    task_type="unit_convert", family="fam-nt-b10-steamer-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8034,
        "expect": dict(NOCALL, output_contains=["6"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
people = int(re.search(r"(\\d+) 位同事", prompt).group(1))
share = int(re.search(r"每人出 (\\d+) 元", prompt).group(1))
fee = int(re.search(r"包场费 (\\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": people * share - fee}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，两步口算（12 × 8 = 96，96 − 90 = 6）可完成。

## Reference solution
不调用任何工具：12 × 8 = 96 元，96 − 90 = 6，还剩 6 元；终答写出算式。判据：零调用，包含 6。

## Why the answer is unique
收齐的总额与包场费都是题面给定的整数，作差唯一。
''',
)

# ---------------------------------------------------------------- nt-8035
p_8035 = "不用调工具，直接告诉我：罗马数字 XIV 是多少？"
check_prompt(p_8035)
write_case(
    "nt-8035",
    desc="Mental Roman-numeral conversion (XIV), tool use explicitly declined",
    task_type="concept", family="fam-nt-b10-mooncake-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8035,
        "expect": dict(NOCALL, output_contains=["14"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

VALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"[IVXLCDM]{2,}", prompt).group(0)
total = 0
for i, ch in enumerate(token):
    v = VALS[ch]
    if i + 1 < len(token) and VALS[token[i + 1]] > v:
        total -= v
    else:
        total += v
print(json.dumps({"expected_number": total}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，罗马数字转十进制是稳定规则。

## Reference solution
不调用任何工具：X = 10、IV = 4，XIV = 14。判据：零调用，包含 14。

## Why the answer is unique
罗马数字的减写规则（小值在大值前）唯一确定 XIV = 14。
''',
)

# ---------------------------------------------------------------- nt-8036
p_8036 = "别查了，直接说：麦丰面点坊开业四十八周年，罗马数字 XLVIII 对应的数字是多少？"
check_prompt(p_8036)
write_case(
    "nt-8036",
    desc="Mental Roman-numeral conversion (XLVIII) tied to a pastry-shop anniversary, tool use declined",
    task_type="concept", family="fam-nt-b10-mooncake-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8036,
        "expect": dict(NOCALL, output_contains=["48"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

VALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"[IVXLCDM]{2,}", prompt).group(0)
total = 0
for i, ch in enumerate(token):
    v = VALS[ch]
    if i + 1 < len(token) and VALS[token[i + 1]] > v:
        total -= v
    else:
        total += v
print(json.dumps({"expected_number": total}))
''',
    notes='''
## Traps
- None. 用户明确说别查，罗马数字转十进制是稳定规则。

## Reference solution
不调用任何工具：XL = 40、VIII = 8，XLVIII = 48。判据：零调用，包含 48。

## Why the answer is unique
减写规则唯一确定 XLVIII = 48；周年说法只是场景包装，不引入第二种口径。
''',
)

# ---------------------------------------------------------------- nt-8037
p_8037 = "不用翻任何东西：罗马数字 CXL 是多少？"
check_prompt(p_8037)
write_case(
    "nt-8037",
    desc="Mental Roman-numeral conversion (CXL), tool use explicitly declined",
    task_type="concept", family="fam-nt-b10-mooncake-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8037,
        "expect": dict(NOCALL, output_contains=["140"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

VALS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"[IVXLCDM]{2,}", prompt).group(0)
total = 0
for i, ch in enumerate(token):
    v = VALS[ch]
    if i + 1 < len(token) and VALS[token[i + 1]] > v:
        total -= v
    else:
        total += v
print(json.dumps({"expected_number": total}))
''',
    notes='''
## Traps
- None. 用户明确说不用翻任何东西，罗马数字转十进制是稳定规则。

## Reference solution
不调用任何工具：C = 100、XL = 40，CXL = 140。判据：零调用，包含 140。

## Why the answer is unique
减写规则唯一确定 CXL = 140。
''',
)

# ---------------------------------------------------------------- nt-8038
p_8038 = "不用翻任何东西：沐棠茶饮的晚间班从下午 3 点 40 分开始，换算成 24 小时制是几点？"
check_prompt(p_8038)
write_case(
    "nt-8038",
    desc="Mental 12-hour to 24-hour clock conversion for a tea-chain shift start, tool use declined",
    task_type="concept", family="fam-nt-b10-hotdesk-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8038,
        "expect": dict(NOCALL, output_contains_any=["15:40", "15 点 40 分", "15点40分", "15 点 40", "15点40", "15 时 40 分", "15时40分"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(上午|下午|晚上) (\\d+) 点 (\\d+) 分", prompt)
hour, minute = int(m.group(2)), int(m.group(3))
if m.group(1) != "上午" and hour < 12:
    hour += 12
assert "%d:%02d" % (hour, minute) == "15:40"
print(json.dumps({"expected_contains_any": ["15:40", "15 点 40 分", "15点40分", "15 点 40", "15点40", "15 时 40 分", "15时40分"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻任何东西，十二小时制换二十四小时制是固定规则。

## Reference solution
不调用任何工具：下午 3 点 40 分即 15:40。判据：零调用，包含 15:40（或等价写法）。

## Why the answer is unique
下午加 12 的换算规则固定，3:40 PM 只对应 15:40。
''',
)

# ---------------------------------------------------------------- nt-8039
p_8039 = "No need to open anything: the Loomwork Friday social starts at 7:25 PM — what is that in 24-hour time?"
check_prompt(p_8039)
write_case(
    "nt-8039",
    desc="Mental 12-hour to 24-hour clock conversion for a coworking social, tool use declined",
    task_type="concept", family="fam-nt-b10-hotdesk-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8039,
        "expect": dict(NOCALL, output_contains=["19:25"],
                       output_contains_any=["19:25", "19:25 hours"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(\\d+):(\\d+) (AM|PM)", prompt)
hour, minute = int(m.group(1)), int(m.group(2))
if m.group(3) == "PM" and hour < 12:
    hour += 12
if m.group(3) == "AM" and hour == 12:
    hour = 0
assert "%d:%02d" % (hour, minute) == "19:25"
print(json.dumps({"expected_contains_any": ["19:25", "19:25 hours"]}))
''',
    notes='''
## Traps
- None. A fixed clock conversion; the user forbids opening anything.

## Reference solution
No tool call: 7:25 PM is 19:25 in 24-hour time. Criteria: zero calls, contains 19:25.

## Why the answer is unique
Adding 12 to a PM hour below 12 is the fixed rule, so 7:25 PM maps only to 19:25.
''',
)

# ---------------------------------------------------------------- nt-8040
p_8040 = "别查了：麦丰面点坊的烤箱预约从晚上 11 点 05 分开始，24 小时制怎么写？"
check_prompt(p_8040)
write_case(
    "nt-8040",
    desc="Mental 12-hour to 24-hour clock conversion for a pastry-shop oven booking, tool use declined",
    task_type="concept", family="fam-nt-b10-hotdesk-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_8040,
        "expect": dict(NOCALL, output_contains_any=["23:05", "23 点 05 分", "23点05分", "23 点 05", "23点05", "23 时 05 分", "23时05分"],
                       max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(上午|下午|晚上) (\\d+) 点 (\\d+) 分", prompt)
hour, minute = int(m.group(2)), int(m.group(3))
if m.group(1) != "上午" and hour < 12:
    hour += 12
assert "%d:%02d" % (hour, minute) == "23:05"
print(json.dumps({"expected_contains_any": ["23:05", "23 点 05 分", "23点05分", "23 点 05", "23点05", "23 时 05 分", "23时05分"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，十二小时制换二十四小时制是固定规则。

## Reference solution
不调用任何工具：晚上 11 点 05 分即 23:05。判据：零调用，包含 23:05（或等价写法）。

## Why the answer is unique
晚上加 12 的换算规则固定，11:05 PM 只对应 23:05。
''',
)

# ---------------------------------------------------------------- doc-8031
files_doc31 = {
    "README.md": "# 沐棠茶饮 门店文案库\n\n上架与海报文案以 文案/在用清单.md 为准，改稿前先对照。\n",
    "文案/在用清单.md": "- 桂花乌龙：秋日限定\n- 云雾青柠：冰饮更佳\n",
}
p_doc31 = "不用翻文案库，直接帮我翻：「今日鲜奶茶已售罄」翻成英文怎么说？"
check_prompt(p_doc31)
write_case(
    "doc-8031",
    desc="Tea-chain copywriting workspace available but the user forbids opening it and asks how to render a sold-out notice in English",
    task_type="policy_lookup", family="fam-doc-b10-boba-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc31,
    turns=[{
        "prompt": p_doc31,
        "expect": dict(NOCALL,
                       output_contains_any=["sold out", "sold-out", "out of stock", "run out of"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "售罄" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店文案库")
print(json.dumps({"expected_contains_any": ["sold out", "sold-out", "out of stock", "run out of"]}))
''',
    notes='''
## Traps
- None. 用户明确说不用翻文案库，翻译成英文的固定说法即可。

## Reference solution
不调用任何工具，直接给译文：「今日鲜奶茶已售罄」可译为 "Fresh milk tea is sold out today"，也可用 out of stock / run out of 的写法。判据：零调用，包含 sold out（或等价说法）。

## Why the answer is unique
「售罄」对应 sold out / out of stock 是固定译法；判据列出了等价说法，翻译唯一。
''',
)

# ---------------------------------------------------------------- doc-8032
files_doc32 = {
    "README.md": "# 麦丰面点坊 门店文案库\n\n海报与提示牌文案以 文案/在用清单.md 为准。\n",
    "文案/在用清单.md": "- 蝴蝶酥：下午出炉\n- 鲜肉月饼：现烤现卖\n",
}
p_doc32 = "别查了，把这句英文换成自然的中文：「While supplies last」。"
check_prompt(p_doc32)
write_case(
    "doc-8032",
    desc="Pastry-shop copywriting workspace available but the user forbids opening it and asks for a natural Chinese rendering of While supplies last",
    task_type="policy_lookup", family="fam-doc-b10-boba-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc32,
    turns=[{
        "prompt": p_doc32,
        "expect": dict(NOCALL,
                       output_contains_any=["售完即止", "售完为止", "送完即止", "卖完即止", "数量有限", "送完为止"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "While supplies last" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 门店文案库")
print(json.dumps({"expected_contains_any": ["售完即止", "售完为止", "送完即止", "卖完即止", "数量有限", "送完为止"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，改写成中文的惯用说法即可。

## Reference solution
不调用任何工具，直接给改写：「While supplies last」即「售完即止」（也可作「数量有限，售完为止」）。判据：零调用，包含「售完即止」等惯用说法之一。

## Why the answer is unique
这句英文的通行中文写法收敛于「售完即止/数量有限」一族，判据已列出等价说法。
''',
)

# ---------------------------------------------------------------- doc-8033
files_doc33 = {
    "README.md": "# Loomwork front-desk playbook\n\nBooking wording lives in front-desk/playbook.md; edits need the duty manager.\n",
    "front-desk/playbook.md": "Late arrivals: walk them around to the side door.\n",
}
p_doc33 = "No need to open anything: shorten this sentence to one line without losing the key detail — Guests who arrive after 6 in the evening will need to check in at the side entrance."
check_prompt(p_doc33)
write_case(
    "doc-8033",
    desc="Coworking playbook workspace available but forbidden; the user asks to shorten a long arrival notice while keeping the entrance detail",
    task_type="policy_lookup", family="fam-doc-b10-boba-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc33,
    turns=[{
        "prompt": p_doc33,
        "expect": dict(NOCALL,
                       output_contains_any=["side entrance"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "after 6" in prompt and "side entrance" in prompt
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-desk playbook")
print(json.dumps({"expected_contains_any": ["side entrance"]}))
''',
    notes='''
## Traps
- None. The user forbids opening anything; the rewrite only needs the sentence in the prompt.

## Reference solution
No tool call. Rewrite in one line, e.g. "Evening arrivals after 6: check in at the side entrance." The key detail (which entrance) must survive. Criteria: zero calls, contains "side entrance".

## Why the answer is unique
The shortened line must keep the location detail, and only one entrance is named in the source sentence; dropping it would not answer the request.
''',
)

# ---------------------------------------------------------------- doc-8034
files_doc34 = {
    "README.md": "# 沐棠茶饮 门店排班\n\n每周排班以门店白板为准，系统里的是上月存档。\n",
    "门店/排班.md": "- 早班：阿澈、小满\n- 晚班：阿澜、柚子\n",
}
p_doc34 = "不用翻排班表，直接告诉我：今天是周三，沐棠茶饮的盘点定在 4 天后，那天是周几？"
check_prompt(p_doc34)
write_case(
    "doc-8034",
    desc="Tea-chain rota workspace available but forbidden; the user states today is Wednesday and asks which weekday is 4 days later",
    task_type="policy_lookup", family="fam-doc-b10-whiteboard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc34,
    turns=[{
        "prompt": p_doc34,
        "expect": dict(NOCALL,
                       output_contains_any=zh_weekday_words(6),
                       max_output_chars=400),
    }],
    verify='''
import json
import re

NAMES = ["一", "二", "三", "四", "五", "六", "日"]
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
base = NAMES.index(re.search(r"今天是周(.)", prompt).group(1))
shift = int(re.search(r"(\\d+) 天后", prompt).group(1))
idx = (base + shift) % 7
assert idx == 6
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门店排班")
if idx == 6:
    words = ["周日", "星期日", "星期天", "礼拜天", "礼拜日"]
else:
    words = ["周" + NAMES[idx], "星期" + NAMES[idx], "礼拜" + NAMES[idx]]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 今天是周几和间隔天数都在题面里；用户明确说不用翻排班表。

## Reference solution
不调用任何工具：周三往后数 4 天，周四、周五、周六、周日，盘点日是周日。判据：零调用，包含「周日/星期日/星期天」之一。

## Why the answer is unique
起点（周三）与间隔（4 天）由题面给定，往后数唯一得到周日。
''',
)

# ---------------------------------------------------------------- doc-8035
files_doc35 = {
    "README.md": "# 麦丰面点坊 会员活动\n\n活动场地安排见 门店/活动排期.md。\n",
    "门店/活动排期.md": "- 会员品鉴会：待定\n- 中秋礼盒预售：筹备中\n",
}
p_doc35 = "别查了，直接算：今天是周五，麦丰面点坊的会员日定在 10 天后，那天是周几？"
check_prompt(p_doc35)
write_case(
    "doc-8035",
    desc="Pastry-shop events workspace available but forbidden; the user states today is Friday and asks which weekday is 10 days later",
    task_type="policy_lookup", family="fam-doc-b10-whiteboard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc35,
    turns=[{
        "prompt": p_doc35,
        "expect": dict(NOCALL,
                       output_contains_any=zh_weekday_words(0),
                       max_output_chars=400),
    }],
    verify='''
import json
import re

NAMES = ["一", "二", "三", "四", "五", "六", "日"]
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
base = NAMES.index(re.search(r"今天是周(.)", prompt).group(1))
shift = int(re.search(r"(\\d+) 天后", prompt).group(1))
idx = (base + shift) % 7
assert idx == 0
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 会员活动")
if idx == 6:
    words = ["周日", "星期日", "星期天", "礼拜天", "礼拜日"]
else:
    words = ["周" + NAMES[idx], "星期" + NAMES[idx], "礼拜" + NAMES[idx]]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 起点和间隔都在题面里；用户明确说别查。

## Reference solution
不调用任何工具：周五往后 10 天，10 ÷ 7 余 3，即再过三天，周五加三天是周一，会员日是周一。判据：零调用，包含「周一/星期一/礼拜一」之一。

## Why the answer is unique
(周五 + 10 天) mod 7 唯一对应周一。
''',
)

# ---------------------------------------------------------------- doc-8036
files_doc36 = {
    "README.md": "# Loomwork front-desk rota\n\nDesk cover and evening shifts are listed in front-desk/rota.md.\n",
    "front-desk/rota.md": "Desk cover: Priya, Marco\nEvenings: Lena\n",
}
p_doc36 = "No need to open anything: today is Tuesday, and the Loomwork members' town hall is 9 days later. Which weekday does that land on?"
check_prompt(p_doc36)
write_case(
    "doc-8036",
    desc="Coworking rota workspace available but forbidden; the user states today is Tuesday and asks which weekday is 9 days later",
    task_type="policy_lookup", family="fam-doc-b10-whiteboard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc36,
    turns=[{
        "prompt": p_doc36,
        "expect": dict(NOCALL,
                       output_contains_any=en_weekday_words(3),
                       max_output_chars=400),
    }],
    verify='''
import json
import re

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
base = next(i for i, d in enumerate(DAYS) if d in prompt)
shift = int(re.search(r"(\\d+) days later", prompt).group(1))
idx = (base + shift) % 7
assert idx == 3
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork front-desk rota")
print(json.dumps({"expected_contains_any": [DAYS[idx], DAYS[idx][:3]]}))
''',
    notes='''
## Traps
- None. Both the base weekday and the gap are in the prompt; the rota is a decoy.

## Reference solution
No tool call: 9 days later means 9 mod 7 = 2 extra days beyond a full week, so Tuesday plus 2 is Thursday. Criteria: zero calls, contains Thursday.

## Why the answer is unique
(Tuesday + 9) mod 7 lands on Thursday; no other reading of the gap exists.
''',
)

# ---------------------------------------------------------------- doc-8037
files_doc37 = {
    "README.md": "# 沐棠茶饮 营销档期\n\n档期与物料排期见 营销/档期表.md。\n",
    "营销/档期表.md": "- 秋季桂花季：档期待定\n- 会员日物料：设计中\n",
}
p_doc37 = "不用调工具，直接算：沐棠茶饮的桂花季从 10 月 1 日开始到 10 月 7 日结束，首尾两天都算，一共是几天？"
check_prompt(p_doc37)
assert_value_absent(files_doc37, 7)
write_case(
    "doc-8037",
    desc="Tea-chain campaign workspace available but forbidden; the user gives both endpoint dates and asks the inclusive day count",
    task_type="policy_lookup", family="fam-doc-b10-mailroom-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc37,
    turns=[{
        "prompt": p_doc37,
        "expect": dict(NOCALL, output_contains=["7"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "首尾两天都算" in prompt
pairs = re.findall(r"(\\d+) 月 (\\d+) 日", prompt)
m1, d1 = int(pairs[0][0]), int(pairs[0][1])
m2, d2 = int(pairs[1][0]), int(pairs[1][1])
assert (m1, m2) == (10, 10)
days = d2 - d1 + 1
assert days == 7
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 营销档期")
print(json.dumps({"expected_number": days}))
''',
    notes='''
## Traps
- None. 起止日期和「首尾都算」都在题面里；用户明确说不用调工具。

## Reference solution
不调用任何工具：10 月 1 日到 10 月 7 日首尾都算，7 − 1 + 1 = 7 天。判据：零调用，包含 7。

## Why the answer is unique
闭区间计数的口径由「首尾两天都算」写死，答案唯一；不写这个口径才会有 6 天的歧义。
''',
)

# ---------------------------------------------------------------- doc-8038
files_doc38 = {
    "README.md": "# 麦丰面点坊 生产档期\n\n产能与档期安排见 工坊/档期表.md。\n",
    "工坊/档期表.md": "- 酥皮类停产检修：待定\n- 新品试产：筹备中\n",
}
p_doc38 = "别查了，直接算：3 月 28 日到 4 月 2 日，首尾都算，麦丰面点坊一共停业检修几天？"
check_prompt(p_doc38)
assert_value_absent(files_doc38, 6)
write_case(
    "doc-8038",
    desc="Pastry-shop schedule workspace available but forbidden; the user gives a cross-month range and asks the inclusive day count",
    task_type="policy_lookup", family="fam-doc-b10-mailroom-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc38,
    turns=[{
        "prompt": p_doc38,
        "expect": dict(NOCALL, output_contains_any=["6 天", "6天", "六天"], max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "首尾都算" in prompt
pairs = re.findall(r"(\\d+) 月 (\\d+) 日", prompt)
m1, d1 = int(pairs[0][0]), int(pairs[0][1])
m2, d2 = int(pairs[1][0]), int(pairs[1][1])
MONTH_LEN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
if m1 == m2:
    days = d2 - d1 + 1
else:
    days = (MONTH_LEN[m1] - d1 + 1) + d2
assert days == 6
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 生产档期")
print(json.dumps({"expected_contains_any": ["%d 天" % days, "%d天" % days, "六天"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 两个日期与「首尾都算」都在题面里；跨月计数的月份长度是固定事实。

## Reference solution
不调用任何工具：3 月 28 日到 31 日是 4 天（31 − 28 + 1），加上 4 月 1 日到 2 日是 2 天，共 6 天。判据：零调用，包含 6。

## Why the answer is unique
3 月有 31 天是固定事实，闭区间口径由题面写死，跨月相加唯一。
''',
)

# ---------------------------------------------------------------- doc-8039
files_doc39 = {
    "README.md": "# Loomwork maintenance planner\n\nRepaint and repairs scheduling lives in maintenance/planner.md.\n",
    "maintenance/planner.md": "Repaint quotes: two pending\nLighting retrofit: scheduled\n",
}
p_doc39 = "No need to open anything — mental math: the Loomwork studio repaint runs from September 25 through October 1, both days included. How many days is that in total?"
check_prompt(p_doc39)
assert_value_absent(files_doc39, 7)
write_case(
    "doc-8039",
    desc="Coworking maintenance workspace available but forbidden; the user gives a cross-month range and asks the inclusive day count",
    task_type="policy_lookup", family="fam-doc-b10-mailroom-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc39,
    turns=[{
        "prompt": p_doc39,
        "expect": dict(NOCALL, output_contains=["7"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

MONTHS = {"January": 31, "February": 28, "March": 31, "April": 30, "May": 31, "June": 30,
          "July": 31, "August": 31, "September": 30, "October": 31, "November": 30, "December": 31}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "both days included" in prompt
pairs = re.findall(r"([A-Z][a-z]+) (\\d+)", prompt)
m1, d1 = MONTHS[pairs[0][0]], int(pairs[0][1])
m2, d2 = MONTHS[pairs[1][0]], int(pairs[1][1])
days = (m1 - d1 + 1) + d2 if m1 != m2 else d2 - d1 + 1
assert days == 7
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork maintenance planner")
print(json.dumps({"expected_number": days}))
''',
    notes='''
## Traps
- None. Both endpoints and the inclusive rule are in the prompt; September has 30 days.

## Reference solution
No tool call: September 25-30 is 6 days (30 - 25 + 1), plus October 1 is 1 day, 7 days in total. Criteria: zero calls, contains 7.

## Why the answer is unique
September's length is a fixed fact and the inclusive reading is stated, so the count is unique.
''',
)

# ---------------------------------------------------------------- doc-8040
files_doc40 = {
    "README.md": "# 沐棠茶饮 菜单配置\n\n菜单数据的样例见 菜单/配置样例.json，改配置要提前一天提审。\n",
    "菜单/配置样例.json": '{\n  "menu": [\n    "云雾青柠",\n    "桂花乌龙"\n  ]\n}\n',
}
p_doc40 = "不用翻文档，直接告诉我：手写 JSON 的时候，字符串两边要用什么引号？用单引号行不行？"
check_prompt(p_doc40)
write_case(
    "doc-8040",
    desc="Tea-chain menu-config workspace available but forbidden; the user asks which quotes JSON strings require and whether single quotes work",
    task_type="policy_lookup", family="fam-doc-b10-pantry-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_doc40,
    turns=[{
        "prompt": p_doc40,
        "expect": dict(NOCALL,
                       output_contains_any=["双引号", "double quote", "Double quote"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "JSON" in prompt and "单引号" in prompt
assert case["files"]["菜单/配置样例.json"].splitlines()[0] == "{"
print(json.dumps({"expected_contains_any": ["双引号", "double quote", "Double quote"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻文档，JSON 的引号规则是稳定事实。

## Reference solution
不调用任何工具，直接回答（1–2 句）：JSON 的字符串必须用双引号（键和字符串值都是），单引号不是合法的 JSON 语法。判据：零调用，包含「双引号」。

## Why the answer is unique
JSON 标准规定字符串一律用双引号，答案唯一。
''',
)

# ---------------------------------------------------------------- cfg-8040
files_cfg40 = {
    "README.md": "# 沐棠茶饮 门禁权限说明\n\n权限码的位含义见 行政/门禁交接.md。\n",
    "行政/门禁交接.md": "- 权限码由四个开关位组成，从左到右依次对应门口、吧台、后仓、办公室\n",
}
p_cfg40 = "不用翻配置文件，直接算：门禁卡的权限码二进制 `1011` 换成十进制是多少？"
check_prompt(p_cfg40)
assert_value_absent(files_cfg40, 11)
write_case(
    "cfg-8040",
    desc="Tea-chain door-access workspace available but the user forbids opening it and asks to convert binary 1011 to decimal",
    task_type="read_effective", family="fam-cfg-b10-keycard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_cfg40,
    turns=[{
        "prompt": p_cfg40,
        "expect": dict(NOCALL, output_contains=["11"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
bits = re.search(r"`([01]+)`", prompt).group(1)
value = int(bits, 2)
assert value == 11
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 门禁权限说明")
print(json.dumps({"expected_number": value}))
''',
    notes='''
## Traps
- None. 用户明确说不用翻配置文件，二进制转十进制是稳定规则。

## Reference solution
不调用任何工具：1011 = 8 + 2 + 1 = 11。判据：零调用，包含 11。

## Why the answer is unique
按位权展开只有一种结果；门禁交接文件与问题无关，用户也明确禁止查看。
''',
)

# ---------------------------------------------------------------- cfg-8041
p_cfg41 = "别查了，直接算：十六进制 `1A` 换成十进制是多少？"
check_prompt(p_cfg41)
write_case(
    "cfg-8041",
    desc="User forbids looking anything up and asks to convert hexadecimal 1A to decimal",
    task_type="read_effective", family="fam-cfg-b10-keycard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_cfg41,
        "expect": dict(NOCALL, output_contains=["26"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"`([0-9A-Fa-f]+)`", prompt).group(1)
value = int(token, 16)
assert value == 26
print(json.dumps({"expected_number": value}))
''',
    notes='''
## Traps
- None. 用户明确说别查，十六进制转十进制是稳定规则。

## Reference solution
不调用任何工具：1A = 16 + 10 = 26。判据：零调用，包含 26。

## Why the answer is unique
A 对应 10，按位权展开唯一得到 26。
''',
)

# ---------------------------------------------------------------- cfg-8042
files_cfg42 = {
    "README.md": "# Loomwork door access\n\nPanel codes are described in config/door-access.yaml.\n",
    "config/door-access.yaml": "panel:\n  model: airlite\n  holdopen: dusk\n",
}
p_cfg42 = "No need to open anything: the door-code config stores 0x2C — what is that in decimal?"
check_prompt(p_cfg42)
assert_value_absent(files_cfg42, 44)
write_case(
    "cfg-8042",
    desc="Coworking door-access workspace available but forbidden; the user asks to convert hex 0x2C to decimal",
    task_type="read_effective", family="fam-cfg-b10-keycard-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_cfg42,
    turns=[{
        "prompt": p_cfg42,
        "expect": dict(NOCALL, output_contains=["44"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"0x([0-9A-Fa-f]+)", prompt).group(1)
value = int(token, 16)
assert value == 44
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork door access")
assert case["files"]["config/door-access.yaml"].splitlines()[0] == "panel:"
print(json.dumps({"expected_number": value}))
''',
    notes='''
## Traps
- None. A stable hex conversion; the user forbids opening anything.

## Reference solution
No tool call: 0x2C = 2 x 16 + 12 = 44. Criteria: zero calls, contains 44.

## Why the answer is unique
C is 12 and place values are fixed, so the conversion has one result.
''',
)

# ---------------------------------------------------------------- cfg-8043
files_cfg43 = {
    "README.md": "# 麦丰面点坊 会员日历\n\n储值活动的跨年结算口径见 财务/结算说明.md。\n",
    "财务/结算说明.md": "- 会员储值按自然年结转，跨年余额不清零\n",
}
p_cfg43 = "不用调工具，直接说：2028 年一整年有多少天？"
check_prompt(p_cfg43)
assert_value_absent(files_cfg43, 366)
write_case(
    "cfg-8043",
    desc="Pastry-shop calendar workspace available but forbidden; the user asks how many days the year 2028 has",
    task_type="read_effective", family="fam-cfg-b10-doughrise-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_cfg43,
    turns=[{
        "prompt": p_cfg43,
        "expect": dict(NOCALL, output_contains=["366"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
year = int(re.search(r"(\\d{4}) 年", prompt).group(1))
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
days = 366 if leap else 365
assert days == 366
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 会员日历")
print(json.dumps({"expected_number": days}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具，闰年规则是稳定事实。

## Reference solution
不调用任何工具：2028 能被 4 整除且不是整百年，是闰年，全年 366 天。判据：零调用，包含 366。

## Why the answer is unique
闰年判定规则固定，2028 的天数唯一。
''',
)

# ---------------------------------------------------------------- cfg-8044
p_cfg44 = "别查了，直接算：2100 年有多少天？"
check_prompt(p_cfg44)
write_case(
    "cfg-8044",
    desc="User forbids looking anything up and asks how many days the year 2100 has (century rule)",
    task_type="read_effective", family="fam-cfg-b10-doughrise-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_cfg44,
        "expect": dict(NOCALL, output_contains=["365"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
year = int(re.search(r"(\\d{4}) 年", prompt).group(1))
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
days = 366 if leap else 365
assert days == 365
print(json.dumps({"expected_number": days}))
''',
    notes='''
## Traps
- None. 用户明确说别查，闰年的整百年例外是稳定规则。

## Reference solution
不调用任何工具：2100 是整百年但不能被 400 整除，不是闰年，全年 365 天。判据：零调用，包含 365。

## Why the answer is unique
「能被 4 整除的整百年还要能被 400 整除才是闰年」是固定规则，2100 的天数唯一。
''',
)

# ---------------------------------------------------------------- cfg-8045
p_cfg45 = "No need to open anything: how many days does February have in 2032?"
check_prompt(p_cfg45)
write_case(
    "cfg-8045",
    desc="User forbids opening anything and asks the length of February 2032 (leap year)",
    task_type="read_effective", family="fam-cfg-b10-doughrise-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_cfg45,
        "expect": dict(NOCALL, output_contains=["29"], output_contains_token=True, max_output_chars=400),
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
year = int(re.search(r"in (\\d{4})", prompt).group(1))
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
days = 29 if leap else 28
assert days == 29
print(json.dumps({"expected_number": days}))
''',
    notes='''
## Traps
- None. A stable calendar fact; the user forbids opening anything.

## Reference solution
No tool call: 2032 is divisible by 4 and not a century year, so it is a leap year and February has 29 days. Criteria: zero calls, contains 29.

## Why the answer is unique
The leap-year rule pins February 2032 to exactly one length.
''',
)

# ---------------------------------------------------------------- cfg-8046
files_cfg46 = {
    "README.md": "# 沐棠茶饮 会员编码规范\n\n编码格式的校验规则由小程序端维护，运营侧只登记前缀。\n",
    "运营/前缀登记.md": "- 会员号前缀：MT\n- 券码前缀：Q\n",
}
p_cfg46 = "不用翻手册，直接讲：正则表达式里的 `\\d` 匹配的是什么？"
check_prompt(p_cfg46)
write_case(
    "cfg-8046",
    desc="Tea-chain coding-standard workspace available but forbidden; the user asks what the regex token backslash-d matches",
    task_type="read_effective", family="fam-cfg-b10-chai-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_cfg46,
    turns=[{
        "prompt": p_cfg46,
        "expect": dict(NOCALL,
                       output_contains_any=["数字", "digit", "0-9"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == chr(92) + "d"
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 会员编码规范")
print(json.dumps({"expected_contains_any": ["数字", "digit", "0-9"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻手册，正则元字符的含义是稳定事实。

## Reference solution
不调用任何工具，直接回答（1–2 句）：`\\d` 匹配一个数字字符，等价于 0-9。判据：零调用，包含「数字/digit」。

## Why the answer is unique
`\\d` 的定义由正则语法固定，答案唯一；编码规范文件是诱饵，用户明确禁止查看。
''',
)

# ---------------------------------------------------------------- cfg-8047
p_cfg47 = "别查了，直接说：正则里的 `^` 这个符号表示什么？"
check_prompt(p_cfg47)
write_case(
    "cfg-8047",
    desc="User forbids looking anything up and asks what the caret means in a regular expression",
    task_type="read_effective", family="fam-cfg-b10-chai-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_cfg47,
        "expect": dict(NOCALL,
                       output_contains_any=["行首", "开头", "起始", "start", "beginning"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == "^"
print(json.dumps({"expected_contains_any": ["行首", "开头", "起始", "start", "beginning"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说别查，正则锚点的含义是稳定事实。

## Reference solution
不调用任何工具，直接回答（1 句）：`^` 是锚点，匹配行的开头（或字符串的开头）；放在字符组里才是取反，语义不同。判据：零调用，包含「行首/开头」之一。

## Why the answer is unique
`^` 的锚点语义由正则语法固定；判据已覆盖行首/开头/起始的等价说法。
''',
)

# ---------------------------------------------------------------- cfg-8048
p_cfg48 = "不用翻文档，直接讲：正则里写在某个字符后面的星号 `*` 表示什么？"
check_prompt(p_cfg48)
write_case(
    "cfg-8048",
    desc="User forbids opening anything and asks what a trailing asterisk quantifier means in a regular expression",
    task_type="read_effective", family="fam-cfg-b10-chai-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": p_cfg48,
        "expect": dict(NOCALL,
                       output_contains_any=["任意多", "零个或多个", "0 个或多个", "零或多个", "零次或多次", "0 次或多次", "zero or more", "0 or more"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == "*"
print(json.dumps({"expected_contains_any": ["任意多", "零个或多个", "0 个或多个", "零或多个", "零次或多次", "0 次或多次", "zero or more", "0 or more"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻文档，量词的含义是稳定事实。

## Reference solution
不调用任何工具，直接回答（1 句）：星号是量词，表示前面的字符可以出现零次或任意多次。判据：零调用，包含「零个或多个/任意多」之一。

## Why the answer is unique
`*` 的量词语义由正则语法固定；判据覆盖了「零个或多个」「任意多个」等价说法。
''',
)

# ---------------------------------------------------------------- cfg-8049
files_cfg49 = {
    "README.md": "# 沐棠茶饮 菜单配置\n\n加料与冰量的样例见 菜单/配置样例.json，改配置要提前一天提审。\n",
    "菜单/配置样例.json": '{\n  "toppings": ["椰果", "仙草"],\n  "ice": ["正常冰", "少冰", "去冰"]\n}\n',
}
p_cfg49 = "不用翻配置文件，直接告诉我：JSON 里能写注释吗？"
check_prompt(p_cfg49)
write_case(
    "cfg-8049",
    desc="Tea-chain menu-config workspace available but forbidden; the user asks whether JSON allows comments",
    task_type="read_effective", family="fam-cfg-b10-frontdesk-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files=files_cfg49,
    turns=[{
        "prompt": p_cfg49,
        "expect": dict(NOCALL,
                       output_contains_any=["不允许", "不能", "不行", "没有注释", "不支持"],
                       max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "JSON" in prompt and "注释" in prompt
assert case["files"]["菜单/配置样例.json"].splitlines()[0] == "{"
print(json.dumps({"expected_contains_any": ["不允许", "不能", "不行", "没有注释", "不支持"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 用户明确说不用翻配置文件，JSON 是否允许注释是稳定事实。

## Reference solution
不调用任何工具，直接回答（1–2 句）：JSON 标准不允许注释，写进去会导致解析失败；需要说明时放在单独的字段里。判据：零调用，包含「不允许/不能」之一。

## Why the answer is unique
JSON 语法没有注释这一成分，答案唯一。
''',
)
