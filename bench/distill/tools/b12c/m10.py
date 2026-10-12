"""M10 (b12c): special-purpose tool first -- get_weather over web search.
Fixture clock is 2026-09-16 (Wed): 明天 = 09-17 (Thu), 后天 = 09-18 (Fri).
Builders share the shapes of ../b12a/m10.py (direct lookup, rule file + forecast, concept negative);
ids hyb-9078..9087, 9090, nt-9088/9089."""
import json

from common import lines, weather, write_case

REFS = {}
NOWEB = ["web_search", "web_fetch"]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


DAY = '''
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][%d]
assert day["date"] == %r
'''


def direct(cid, *, city, current, rows, aliases, file, head, idx, date, answer, answer_key, prompt, trap, decoy,
           topic, desc, reply, why, alts, level="L1", axes=("OBS",), contains=None, number=False, tok=True):
    fx = [weather(city, current, rows, aliases=aliases)]
    files = {file[0]: lines(file[1])}
    verify = DAY % (idx, date) + 'assert case["files"][%r].startswith(%r)\n' % (file[0], head)
    if number:
        verify += 'print(json.dumps({"expected_number": int(%s)}))\n' % answer
    else:
        verify += 'print(json.dumps({"expected_string": %s}))\n' % answer
    notes = f"""## Traps
- {trap}: {decoy[1]}

## Reference solution
1. get_weather {{"location": "{city}", "days": 3}}
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    expect = {"required_tools": ["get_weather"], "forbidden_tools": NOWEB,
              "output_contains": contains or [answer_key], "max_output_chars": 600}
    if number and tok:
        expect["output_contains_token"] = True
    return write_case(cid, desc=desc, task_type="special_tool", family="fam-hyb-b12c-%s-01" % topic, level=level,
                      ref_calls=1, traps=[trap], decoys={trap: decoy[0]}, axes=list(axes), files=files, verify=verify,
                      notes=notes, weather_fixture=fx, turns=[{"prompt": prompt, "expect": expect}])


def rule_case(cid, *, city, aliases, current, rows, rule_path, rule_lines, topic, desc, prompt, alts, rule_trap,
              decoy, contains, any_of, answer_idx, reply, why, ref_note):
    fx = [weather(city, current, rows, aliases=aliases)]
    head = rule_lines[0]
    files = {rule_path: lines(rule_lines), rule_path.rsplit("/", 1)[0] + "/说明.md": lines(["# 说明", "", "本目录存放日常规则。"])}
    verify = '''
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][%d]
assert case["files"][%r].startswith(%r)
assert case["files"][%r].startswith("# 说明")
assert %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (answer_idx, rule_path, head, rule_path.rsplit("/", 1)[0] + "/说明.md", "day[%r]" % ("temp_c" if "temp_c" in contains[1] else "rain_chance"), json.dumps(any_of, ensure_ascii=False))
    notes = f"""## Traps
- TR-RULEFILE: {rule_trap}
- TR-DECOY: {decoy[1]}

## Reference solution
1. list_files / read_file {rule_path}
2. get_weather {{"location": "{city}", "days": 3}}
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12c-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-RULEFILE", "TR-DECOY"], decoys={"TR-RULEFILE": decoy[2], "TR-DECOY": decoy[0]}, axes=["DEC", "CHN", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": prompt,
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "output_contains": [contains[0]],
                           "output_contains_any": any_of, "max_output_chars": 600}}])


def concept(cid, *, topic, desc, prompt, words, answer, trap_note, alts):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(words, ensure_ascii=False)
    notes = f"""## Traps
- TR-NOTOOLNEED: {trap_note}

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
Standard meteorological explanation; no location or date is asked for.
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="concept", family="fam-nt-b12c-%s-01" % topic, level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "查一下今天的天气"}, axes=["DEC"],
        files={}, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words,
                                              "max_output_chars": 600}}])




def hyb_9078():
    return direct(
        "hyb-9078", city="兰州", aliases=["Lanzhou"], current="晴 19°C 体感 18°C 湿度 35% 风速 16 km/h",
        rows=[("2026-09-16", "晴", "12~22", "0%"), ("2026-09-17", "多云", "9~20", "10%"), ("2026-09-18", "多云", "10~21", "15%")],
        file=("出差/兰州.md", ["# 兰州出差", "", "- 周四早班机"]), head="# 兰州出差", idx=1, date="2026-09-17",
        answer='day["temp_c"].split("~")[0]', answer_key="9", number=True, axes=("OBS", "CHN"),
        prompt="明天一早到兰州，早上会很冷吗？明天最低气温是多少度？",
        trap="TR-DECOY", decoy=("12", "today's low is 12; tomorrow (2026-09-17) is 9."),
        topic="lanzhoulow", desc="Asks tomorrow's low temperature of a city for an early arrival",
        reply="兰州明天（9 月 17 日）多云，最低气温 9°C、最高 20°C，早上偏凉，带件外套。",
        why="Tomorrow is the second forecast row.",
        alts=["兰州明天最低几度", "明早兰州冷吗，最低温多少", "9 月 17 日兰州最低气温", "明天到兰州要穿什么，先告诉我最低温", "What is Lanzhou's low tomorrow?"])


def hyb_9079():
    return direct(
        "hyb-9079", city="Sydney", aliases=["悉尼"], current="Sunny 20°C feels 19°C humidity 48% wind 20 km/h",
        rows=[("2026-09-16", "Sunny", "11~22", "0%"), ("2026-09-17", "Showers", "12~19", "60%"), ("2026-09-18", "Cloudy", "11~20", "20%")],
        file=("trip/sydney.md", ["# Sydney trip", "", "- Harbour walk Thursday afternoon"]), head="# Sydney trip", idx=1, date="2026-09-17",
        answer='day["rain_chance"]', answer_key="60%", axes=("OBS",),
        prompt="I'm planning a harbour walk in Sydney tomorrow afternoon. Is it likely to rain?",
        trap="TR-DECOY", decoy=("0%", "today is 0%; tomorrow (2026-09-17) is 60% showers."),
        topic="sydneyrain", desc="Asks in English whether it rains in a city tomorrow",
        reply="Yes, likely: showers in Sydney tomorrow (2026-09-17), 60% chance of rain, 12-19°C. Bring a rain jacket.",
        why="Tomorrow is the second forecast row.",
        alts=["Will it rain in Sydney tomorrow?", "How likely is rain in Sydney on Thursday?", "Do I need an umbrella for a Sydney harbour walk tomorrow?", "Sydney chance of rain 2026-09-17", "悉尼明天会下雨吗？"])


def hyb_9080():
    return direct(
        "hyb-9080", city="武汉", aliases=["Wuhan"], current="多云 30°C 体感 35°C 湿度 75% 风速 6 km/h",
        rows=[("2026-09-16", "多云", "25~34", "20%"), ("2026-09-17", "雷阵雨", "24~31", "70%"), ("2026-09-18", "阴", "24~30", "40%")],
        file=("工作/外勤.md", ["# 外勤安排", "", "- 下午在汉口跑客户"]), head="# 外勤安排", idx=0, date="2026-09-16",
        answer='day["temp_c"].split("~")[1]', answer_key="34", number=True, tok=False, axes=("OBS", "CHN"),
        prompt="我今天下午在武汉跑外勤，今天最高会到多少度？热不热？",
        trap="TR-DECOY", decoy=("31", "tomorrow's high is 31; today (2026-09-16) is 34."),
        topic="wuhantoday", desc="Asks today's high temperature of a city",
        reply="武汉今天（9 月 16 日）多云，最高气温 34°C、最低 25°C，体感更闷热，注意防暑。",
        why="Today is the first forecast row.",
        alts=["武汉今天最高多少度", "今天武汉热不热，最高几度", "武汉 9 月 16 日最高气温", "今天下午武汉外面多热", "How hot does Wuhan get today?"])


def hyb_9081():
    return direct(
        "hyb-9081", city="深圳", aliases=["Shenzhen"], current="多云 31°C 体感 37°C 湿度 82% 风速 9 km/h",
        rows=[("2026-09-16", "多云", "27~33", "30%"), ("2026-09-17", "雷阵雨", "26~31", "80%"), ("2026-09-18", "中雨", "26~30", "85%")],
        file=("周边/深圳.md", ["# 深圳周末", "", "- 周四晚上想去海边吃烧烤"]), head="# 深圳周末", idx=1, date="2026-09-17",
        answer='day["condition"]', answer_key="雷阵雨", axes=("OBS", "CHN"),
        prompt="明天晚上想在深圳海边吃烧烤，明天天气怎么样？",
        trap="TR-DECOY", decoy=("多云", "today is 多云; tomorrow (2026-09-17) is 雷阵雨 with 80%."),
        topic="shenzhenbbq", desc="Asks tomorrow's weather in a city for an outdoor dinner",
        reply="深圳明天（9 月 17 日）有雷阵雨，降水概率 80%，气温 26~31°C，海边烧烤不太合适。",
        why="Tomorrow is the second forecast row.",
        alts=["深圳明天天气如何，能去海边吗", "明晚深圳下雨吗", "9 月 17 日深圳的天气", "深圳明天适合户外烧烤吗", "What's the weather in Shenzhen tomorrow?"])


def hyb_9090():
    return direct(
        "hyb-9090", city="天津", aliases=["Tianjin"], current="晴 25°C 体感 25°C 湿度 40% 风速 12 km/h",
        rows=[("2026-09-16", "晴", "17~26", "0%"), ("2026-09-17", "晴", "18~27", "5%"), ("2026-09-18", "多云", "19~29", "10%")],
        file=("周末/天津.md", ["# 天津周末", "", "- 周五下班后去海河边跑步"]), head="# 天津周末", idx=2, date="2026-09-18",
        answer='day["temp_c"].split("~")[1]', answer_key="29", number=True, tok=False, axes=("OBS", "CHN"),
        prompt="后天傍晚我想在天津海河边跑步，那天最高气温大概多少？",
        trap="TR-DECOY", decoy=("27", "tomorrow's high is 27; the day after tomorrow (2026-09-18) is 29."),
        topic="tianjinrun", desc="Asks the day-after-tomorrow high temperature of a city for a run",
        reply="天津后天（9 月 18 日）多云，最高气温 29°C、最低 19°C，降水概率 10%，傍晚跑步合适。",
        why="The fixed clock makes 后天 = 2026-09-18, the third forecast row.",
        alts=["后天天津最高几度", "天津后天傍晚热不热", "9 月 18 日天津最高气温", "后天去海河跑步，最高温多少", "How high does Tianjin's temperature go the day after tomorrow?"])


def hyb_9082():
    fx = [weather("西宁", "多云 16°C 体感 14°C 湿度 50% 风速 14 km/h",
                  [("2026-09-16", "多云", "7~18", "20%"), ("2026-09-17", "小雨", "6~15", "55%"), ("2026-09-18", "阴", "6~16", "30%")], aliases=["Xining"])]
    before = lines(["# 出行提示", "", "- 城市：兰州", "- 日期：2026-09-14", "- 天气：晴", "- 气温：10~21°C"])
    after = lines(["# 出行提示", "", "- 城市：西宁", "- 日期：2026-09-17", "- 天气：小雨", "- 气温：6~15°C"])
    verify = '''
import json
case = json.load(open("case.json"))
path = "出行/提示.md"
assert case["files"][path].startswith("# 出行提示")
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
text = chr(10).join(["# 出行提示", "", "- 城市：西宁", "- 日期：" + day["date"], "- 天气：" + day["condition"],
                     "- 气温：%s~%s°C" % (low, high)]) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the old file holds another city and date; the whole file is overwritten. Tomorrow is the second row, not today's.
Newline policy: six lines (second is blank) joined by newlines plus exactly one trailing newline.

## Reference solution
1. get_weather {"location": "西宁", "days": 3}
2. write_file 出行/提示.md with the six lines
3. read_file 出行/提示.md to confirm
Final answer: 已把西宁明天（2026-09-17）的预报（小雨，6~15°C）写进 出行/提示.md，旧内容已覆盖。

## Why the answer is unique
明天 is the second forecast row; the layout is fully specified.
""" + phrasings("西宁明天的天气更新到出行提示", "用西宁明天预报覆盖 出行/提示.md", "出行提示改成西宁 9 月 17 日", "把提示文件换成西宁明天的天气", "Rewrite the travel note with Xining's forecast for tomorrow.")
    return write_case(
        "hyb-9082", desc="Overwrites a travel note with tomorrow's forecast in a fully specified six-line layout",
        task_type="tool_then_write", family="fam-hyb-b12c-travelnote-01", level="L1", ref_calls=3,
        traps=["TR-DEFN"], decoys={"TR-DEFN": "晴"}, axes=["OBS"],
        files={"出行/提示.md": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"出行/提示.md": {"equals": after}}},
        turns=[{"prompt": "把西宁明天的天气写进 出行/提示.md，整个文件覆盖成下面六行（第二行为空行）："
                          "「# 出行提示」「」「- 城市：西宁」「- 日期：<日期，格式 2026-09-17>」「- 天气：<天气>」「- 气温：<最低>~<最高>°C」。"
                          "每行都以换行结束，最后一行之后恰好一个换行，不要多余空行。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9083():
    fx = [weather("Singapore", "Thundery showers 29°C feels 35°C humidity 90% wind 8 km/h",
                  [("2026-09-16", "Thundery showers", "26~32", "75%"), ("2026-09-17", "Cloudy", "26~33", "40%"), ("2026-09-18", "Showers", "26~31", "60%")],
                  aliases=["新加坡"])]
    before = lines(["2026-09-14 Mon Singapore Showers 26-32C", "2026-09-15 Tue Singapore Cloudy 26-33C"])
    line = "2026-09-17 Thu Singapore Cloudy 26-33C"
    verify = '''
import json
case = json.load(open("case.json"))
path = "logs/sg-weather.txt"
before = case["files"][path]
assert before.startswith("2026-09-14 Mon Singapore") and before.endswith(chr(10))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
line = "%s Thu Singapore %s %s-%sC" % (day["date"], day["condition"], low, high)
print(json.dumps({"files": {path: before + line + chr(10)}}))
'''
    notes = """## Traps
- TR-DEFN: the log line carries the weekday abbreviation (2026-09-17 is Thu), which the forecast does not state; bare C suffix, hyphenated range.
- TR-DECOY: today (Thundery showers 26-32C) is the first row; the line is for tomorrow.
Newline policy: expected = before + line + "\\n" (file ends with exactly one trailing newline).

## Reference solution
1. get_weather {"location": "Singapore", "days": 3}
2. append_file logs/sg-weather.txt with "2026-09-17 Thu Singapore Cloudy 26-33C\\n"
3. read_file logs/sg-weather.txt to confirm
Final answer: Appended tomorrow's Singapore forecast (cloudy, 26-33C) to logs/sg-weather.txt.

## Why the answer is unique
Tomorrow is the second forecast row; the line format is spelled out.
""" + phrasings("Log tomorrow's Singapore weather in the same style.", "Add a line for 2026-09-17 to logs/sg-weather.txt.", "Append Singapore's forecast for tomorrow to the log.", "Update the Singapore weather log with tomorrow.", "把新加坡明天的天气按同样格式记到日志里")
    return write_case(
        "hyb-9083", desc="Appends tomorrow's forecast to a city weather log in the style of its existing lines, with an explicit newline rule",
        task_type="tool_then_write", family="fam-hyb-b12c-sglog-01", level="L2", ref_calls=3,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": None, "TR-DECOY": "Thundery showers 26-32C"}, axes=["OBS"],
        files={"logs/sg-weather.txt": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"logs/sg-weather.txt": {"equals": before + line + "\n"}}},
        turns=[{"prompt": "Add tomorrow's Singapore forecast to logs/sg-weather.txt as one new line in exactly the same style as the existing lines "
                          "(date, weekday abbreviation, city, condition, low-high with a C suffix). Every line, including yours, "
                          "ends with a newline, so the file must end with exactly one trailing newline after your line.",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9084():
    fx = [weather("天津", "晴 25°C 体感 25°C 湿度 40% 风速 12 km/h",
                  [("2026-09-16", "晴", "17~26", "0%"), ("2026-09-17", "晴", "18~27", "5%"), ("2026-09-18", "多云", "19~29", "10%")],
                  aliases=["Tianjin"])]
    tpl = ["# 周五行程", "", "- 08:30 例会", "- 天气：（待填）", "- 18:30 海河边跑步"]
    before = lines(tpl)
    after = lines(["# 周五行程", "", "- 08:30 例会", "- 天气：多云 19~29°C，降水概率 10%", "- 18:30 海河边跑步"])
    verify = '''
import json
case = json.load(open("case.json"))
path = "行程/周五.md"
before = case["files"][path]
assert before.startswith("# 周五行程") and before.count("天气：（待填）") == 1
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
low, high = day["temp_c"].split("~")
after = before.replace("天气：（待填）", "天气：%s %s~%s°C，降水概率 %s" % (day["condition"], low, high, day["rain_chance"]), 1)
print(json.dumps({"files": {path: after}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: 周五 is 2026-09-18, the third forecast row (days must be >= 3); only the placeholder line changes and the other lines stay byte-identical.
- TR-DECOY: tomorrow (晴 18~27°C 5%) is the wrong row.
Newline policy: only the placeholder text is replaced; the trailing newline stays.

## Reference solution
1. get_weather {"location": "天津", "days": 3}
2. replace_lines (or write_file) 行程/周五.md line 4 -> "- 天气：多云 19~29°C，降水概率 10%"
3. read_file 行程/周五.md to confirm
Final answer: 已把周五天津的预报（多云 19~29°C，降水概率 10%）填进 行程/周五.md。

## Why the answer is unique
周五 is the third forecast row; the line format is fixed by the prompt.
""" + phrasings("把天津周五的天气填进行程", "行程/周五.md 的天气那行补上天津周五预报", "周五天津天气写进行程文件", "填一下周五行程里的天气", "Fill the weather line in the Friday plan for Tianjin.")
    return write_case(
        "hyb-9084", desc="Fills the placeholder weather line of a Friday plan with the day-after-tomorrow forecast, leaving every other line unchanged",
        task_type="tool_then_write", family="fam-hyb-b12c-fridayplan-01", level="L2", ref_calls=3,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": None, "TR-DECOY": "晴 18~27°C 5%"}, axes=["OBS"],
        files={"行程/周五.md": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"行程/周五.md": {"equals": after}}},
        turns=[{"prompt": "周五我在天津。查一下那天天津的天气，填进 行程/周五.md 里「天气：（待填）」那一行，格式固定为"
                          "「- 天气：<天气> <最低>~<最高>°C，降水概率 <x>」，只替换这一行，其余各行和结尾换行都不要动。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9085():
    return rule_case(
        "hyb-9085", city="哈尔滨", aliases=["Harbin"], current="晴 12°C 体感 9°C 湿度 50% 风速 15 km/h",
        rows=[("2026-09-16", "晴", "9~19", "5%"), ("2026-09-17", "晴", "7~18", "10%"), ("2026-09-18", "多云", "8~20", "15%")],
        rule_path="球馆/开放规定.md",
        rule_lines=["# 室外球场开放规定", "", "- 当日最低气温 ≤ 8°C：室外球场不开放，只开室内馆。", "- 当日降水概率 ≥ 40%：室外球场不开放。",
                    "- 其余情况室外球场正常开放。"],
        topic="harbinbadminton", desc="Applies a sports centre's low-temperature rule to tomorrow's forecast to decide whether the outdoor courts open",
        prompt="按球馆的开放规定，哈尔滨明天的室外球场开不开？",
        alts=["哈尔滨球馆明天室外场开放吗", "明天室外球场能不能用，按规定", "按规定哈尔滨明天只开室内馆吗", "明天室外场地开放情况按规定怎么算", "Under the rules, will the outdoor courts in Harbin be open tomorrow?"],
        rule_trap="the closing threshold is the daily low (<= 8°C), not rain; tomorrow is sunny with 10% rain, so common sense says open.",
        decoy=("9", "today's low is 9 (above the line); tomorrow's low is 7.", "10%"),
        contains=("7°C", 'day["temp_c"].split("~")[0]'), any_of=["不开放", "不开", "关闭", "只开室内"], answer_idx=1,
        reply="不开放：哈尔滨明天最低气温 7°C，不高于规定的 8°C，室外球场关闭，只开室内馆；天晴、降水概率 10%，不是下雨的问题。",
        why="The low 7 is <= 8; the rule is explicit.", ref_note="")


def hyb_9086():
    return rule_case(
        "hyb-9086", city="南宁", aliases=["Nanning"], current="多云 31°C 体感 36°C 湿度 78% 风速 7 km/h",
        rows=[("2026-09-16", "多云", "25~33", "15%"), ("2026-09-17", "多云", "25~34", "25%"), ("2026-09-18", "晴", "26~35", "5%")],
        rule_path="农场/晾晒规定.md",
        rule_lines=["# 稻谷晾晒规定", "", "- 当日降水概率 ≥ 20%：不晾晒，谷子收进仓。", "- 当日最高气温 < 25°C：不晾晒，干得太慢。",
                    "- 其余情况在晒场摊晒。"],
        topic="nanningdry", desc="Applies a farm's drying rule to tomorrow's forecast to decide whether to spread rice on the yard",
        prompt="按农场的晾晒规定，南宁明天的稻谷能不能摊到晒场上晒？",
        alts=["南宁明天晒谷子行不行", "按规定明天稻谷要收仓吗", "明天南宁晒场能用吗", "稻谷明天晒还是收，按农场规定", "Under the farm rules, can we dry rice on the yard in Nanning tomorrow?"],
        rule_trap="the rain threshold is 20%, lower than common sense; tomorrow is only 多云 with 25%, so it looks dry enough.",
        decoy=("15%", "today's rain chance is 15% (would pass); tomorrow's is 25%.", "34"),
        contains=("25%", 'day["rain_chance"]'), any_of=["不晾晒", "不能", "收进", "收仓", "不晒"], answer_idx=1,
        reply="不能晒：南宁明天降水概率 25%，达到规定的 20%，谷子收进仓；最高气温 34°C 不是问题。",
        why="25% >= 20% triggers the no-drying rule.", ref_note="")


def hyb_9087():
    return rule_case(
        "hyb-9087", city="长春", aliases=["Changchun"], current="多云 15°C 体感 13°C 湿度 60% 风速 14 km/h",
        rows=[("2026-09-16", "多云", "8~17", "20%"), ("2026-09-17", "阵雨", "9~16", "55%"), ("2026-09-18", "阴", "8~17", "25%")],
        rule_path="学校/运动会规定.md",
        rule_lines=["# 运动会举办规定", "", "- 比赛当天降水概率 ≥ 50%：运动会延期。", "- 比赛当天最高气温 ≥ 35°C：运动会延期。",
                    "- 其余情况如期举行。"],
        topic="changchunsports", desc="Applies a school sports-day postponement rule to tomorrow's forecast",
        prompt="按学校的运动会规定，长春明天的运动会还能如期举行吗？",
        alts=["长春明天运动会要延期吗", "按规定明天运动会照常吗", "运动会明天办不办，规定怎么说", "长春学校明天运动会按规定行不行", "Under the school rules, does tomorrow's sports day in Changchun go ahead?"],
        rule_trap="the postponement threshold is rain >= 50%; tomorrow is 阵雨 with 55%, while the high of 16°C is far from the heat limit.",
        decoy=("20%", "today's rain chance is 20%; tomorrow's 55% crosses the 50% limit.", "16"),
        contains=("55%", 'day["rain_chance"]'), any_of=["延期", "推迟", "改期", "不能"], answer_idx=1,
        reply="不能如期举行：长春明天有阵雨，降水概率 55%，达到规定的 50%，运动会延期。",
        why="55% >= 50% triggers postponement.", ref_note="")


def nt_9088():
    return concept(
        "nt-9088", topic="uvindex", desc="Weather concept question (UV index) with the weather tool offered; answered without a call",
        prompt="预报里的「紫外线指数」是什么意思？数字多大需要防晒？",
        words=["紫外线", "防晒"], answer="紫外线指数表示当天太阳紫外线辐射的强弱，一般 0-2 弱、3-5 中等、6-7 强、8-10 很强、11 以上极强；3 以上就建议涂防晒，6 以上避开正午外出。",
        trap_note="a definition question; get_weather is offered but no city or date is asked for.",
        alts=["紫外线指数多少算强", "紫外线指数 7 要防晒吗", "天气预报的紫外线指数怎么看", "紫外线指数和气温有关吗", "What does the UV index in a forecast mean?"])


def nt_9089():
    return concept(
        "nt-9089", topic="dewpoint", desc="Weather concept question (dew point) with the weather tool offered; answered without a call",
        prompt="「露点温度」是什么？为什么说露点高的时候会觉得闷？",
        words=["露点", "水汽", "饱和"], answer="露点是空气中的水汽冷却到刚好饱和、开始凝结成露的温度。露点越高，空气里水汽越多，汗不容易蒸发，所以更闷；露点低则干爽。",
        trap_note="a general-knowledge question; get_weather is offered but no location or date is asked for.",
        alts=["什么是露点", "露点温度高了会怎样", "露点和湿度有什么关系", "为什么露点高就闷热", "What is the dew point and why does a high one feel muggy?"])


BUILDERS = [hyb_9078, hyb_9079, hyb_9080, hyb_9081, hyb_9082, hyb_9083, hyb_9084, hyb_9085, hyb_9086, hyb_9087, nt_9088, nt_9089, hyb_9090]
SPEC = {
    "hyb-9078": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9079": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9080": dict(kind="weather", sub="M10a", dates=["2026-09-16"]),
    "hyb-9081": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9090": dict(kind="weather", sub="M10a", dates=["2026-09-18"]),
    "hyb-9082": dict(kind="weather_write", sub="M10b"),
    "hyb-9083": dict(kind="weather_write", sub="M10b"),
    "hyb-9084": dict(kind="weather_write", sub="M10b"),
    "hyb-9085": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["球馆/开放规定.md"]),
    "hyb-9086": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["农场/晾晒规定.md"]),
    "hyb-9087": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["学校/运动会规定.md"]),
    "nt-9088": dict(kind="zero_call", sub="M10e"),
    "nt-9089": dict(kind="zero_call", sub="M10e"),
}
