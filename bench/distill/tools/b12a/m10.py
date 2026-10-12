"""M10 (b12a): special-purpose tool first -- get_weather over web search.
Fixture clock is 2026-09-16 (Wed): 明天 = 09-17 (Thu), 后天 = 09-18 (Fri), 周六 = 09-19, 周日 = 09-20.

File format policy for M10b: every prompt states the exact line format AND whether the
file ends with a newline; the expected file is compared exactly, so the newline rule is
part of the task statement, never left to the model."""
import json

from common import lines, weather, write_case

REFS = {}
NOWEB = ["web_search", "web_fetch"]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


DAY = '''
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][%d]["report"]
day = report["daily"][%d]
assert day["date"] == %r
'''


def direct(cid, *, city, current, rows, aliases, file, head, idx, date, answer, answer_key, prompt, trap, decoy,
           topic, desc, reply, why, alts, level="L1", axes=("OBS",), contains=None, number=False):
    fx = [weather(city, current, rows, aliases=aliases)]
    files = {file[0]: lines(file[1])}
    verify = DAY % (0, idx, date) + 'assert case["files"][%r].startswith(%r)\n' % (file[0], head)
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
    if number:
        expect["output_contains_token"] = True
    fam = "fam-hyb-b12a-%s-01" % topic
    return write_case(cid, desc=desc, task_type="special_tool", family=fam, level=level, ref_calls=1,
                      traps=[trap], decoys={trap: decoy[0]}, axes=list(axes), files=files, verify=verify, notes=notes,
                      weather_fixture=fx, turns=[{"prompt": prompt, "expect": expect}])


def hyb_9039():
    return direct(
        "hyb-9039", city="哈尔滨", aliases=["Harbin"], current="晴 18°C 体感 17°C 湿度 55% 风速 14 km/h",
        rows=[("2026-09-16", "晴", "16~24", "5%"), ("2026-09-17", "多云", "15~23", "10%"),
              ("2026-09-18", "小雨", "13~19", "55%")],
        file=("出差/哈尔滨.md", ["# 哈尔滨出差", "", "- 9 月 18 日 早班机到达"]), head="# 哈尔滨出差", idx=2, date="2026-09-18",
        answer='day["temp_c"].split("~")[0]', answer_key="13", number=True,
        prompt="我后天一大早到哈尔滨，那天最低气温大概几度？",
        trap="TR-DECOY", decoy=("15", "tomorrow's low is 15; the day after tomorrow (2026-09-18) is 13."),
        topic="harbinlow", desc="Asks the day-after-tomorrow low temperature of a city; get_weather answers it directly",
        reply="哈尔滨后天（9 月 18 日）有小雨，最低气温 13°C、最高 19°C。",
        why="The fixed clock makes 后天 = 2026-09-18, the third forecast row.",
        alts=["哈尔滨后天早上冷不冷，最低几度？", "后天哈尔滨的最低温是多少？", "9 月 18 日哈尔滨最低气温", "后天到哈尔滨要穿多厚？先告诉我最低温",
              "What is Harbin's low the day after tomorrow?"])


def hyb_9040():
    return direct(
        "hyb-9040", city="昆明", aliases=["Kunming"], current="多云 22°C 体感 22°C 湿度 78% 风速 7 km/h",
        rows=[("2026-09-16", "多云", "17~25", "20%"), ("2026-09-17", "阵雨", "16~23", "45%"),
              ("2026-09-18", "雷阵雨", "16~22", "70%")],
        file=("周边游/昆明.md", ["# 昆明周边游", "", "- 想去石林，时间待定"]), head="# 昆明周边游", idx=2, date="2026-09-18",
        answer='day["rain_chance"]', answer_key="70%",
        prompt="后天去昆明逛逛，会下雨吗？可能性大不大？", axes=("OBS", "CHN"),
        trap="TR-DECOY", decoy=("45%", "tomorrow is 45% (阵雨); 后天 (2026-09-18) is 70% (雷阵雨)."),
        topic="kunmingrain", desc="Asks whether it rains in a city the day after tomorrow and how likely",
        reply="昆明后天（9 月 18 日）有雷阵雨，降水概率 70%，气温 16~22°C，出门带伞。",
        why="The question names 后天; only the third forecast row matches.",
        alts=["昆明后天会下雨吗，概率多少？", "后天昆明天气如何，要带伞吗", "9 月 18 日昆明下雨的可能性", "后天在昆明逛街，雨大吗", "Will it rain in Kunming the day after tomorrow?"])


def hyb_9041():
    return direct(
        "hyb-9041", city="Xi'an", aliases=["西安", "Xian"], current="Sunny 30°C feels 32°C humidity 38% wind 9 km/h",
        rows=[("2026-09-16", "Sunny", "21~33", "5%"), ("2026-09-17", "Cloudy", "20~31", "10%"),
              ("2026-09-18", "Showers", "19~27", "65%")],
        file=("trip/xian.md", ["# Xi'an trip", "", "- Fri 2026-09-18: Terracotta Army"]), head="# Xi'an trip", idx=2, date="2026-09-18",
        answer='day["rain_chance"]', answer_key="65%",
        prompt="Is it going to rain in Xi'an the day after tomorrow? How likely is it?", level="L1",
        trap="TR-DECOY", decoy=("10%", "tomorrow is 10%; the day after tomorrow (2026-09-18) is 65%."),
        topic="xianrain", desc="Asks in English whether it rains in a city the day after tomorrow",
        reply="Yes, likely: showers in Xi'an on Friday (2026-09-18), 65% chance of rain, 19-27°C.",
        why="The day after tomorrow is the third forecast row.",
        alts=["Will Xi'an get rain on Friday?", "What's the rain chance in Xi'an two days from now?", "Do I need an umbrella in Xi'an the day after tomorrow?",
              "How likely is rain in Xi'an on 2026-09-18?", "西安后天会下雨吗？"])


def hyb_9042():
    fx = [weather("大理", "多云 22°C 体感 22°C 湿度 66% 风速 12 km/h",
                  [("2026-09-16", "多云", "14~24", "30%"), ("2026-09-17", "多云", "15~25", "20%"),
                   ("2026-09-18", "晴", "15~27", "5%")], aliases=["Dali"])]
    files = {"旅行/大理.md": lines(["# 大理行", "", "- 9 月 18 日 洱海骑行"])}
    verify = DAY % (0, 2, "2026-09-18") + '''assert case["files"]["旅行/大理.md"].startswith("# 大理行")
assert all("洱海" not in a for a in case["weather_fixture"][0]["aliases"]) and "洱海" not in report["location"]
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
'''
    notes = """## Traps
- TR-NEARNAME: 洱海 is a lake near 大理, not a city; get_weather resolves cities only, so asking for 洱海 returns location not found and the retry is 大理.
- TR-DECOY: tomorrow's high is 25; 后天 (2026-09-18) is 27.

## Reference solution
1. get_weather {"location": "大理", "days": 3} (or 洱海 first, then 大理 after the not-found error)
Final answer: 后天（9 月 18 日）大理晴，最高气温 27°C、最低 15°C，适合骑行；洱海在大理，按大理的预报看。

## Why the answer is unique
后天 is the third forecast row; the lake has no separate forecast.
""" + phrasings("后天洱海边最高多少度？", "后天去洱海骑车，热不热？", "大理后天最高气温是多少？", "9 月 18 日洱海气温", "How hot will it be at Erhai Lake the day after tomorrow?")
    return write_case(
        "hyb-9042", desc="Asks the high temperature at a lake the day after tomorrow; the forecast must be looked up by its city",
        task_type="special_tool", family="fam-hyb-b12a-erhaihigh-01", level="L2", ref_calls=1,
        traps=["TR-NEARNAME", "TR-DECOY"], decoys={"TR-NEARNAME": "UNKNOWN", "TR-DECOY": "25"}, axes=["ERR", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "后天我去洱海边骑行，那天最高气温多少度？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB,
                           "output_contains": ["27"], "output_contains_token": True, "max_output_chars": 600}}])


def hyb_9043():
    nj = weather("南京", "阴 24°C 体感 26°C 湿度 79% 风速 8 km/h",
                 [("2026-09-16", "阴", "21~26", "35%"), ("2026-09-17", "小雨", "20~25", "60%"),
                  ("2026-09-18", "阴", "20~26", "30%"), ("2026-09-19", "多云", "21~29", "20%"),
                  ("2026-09-20", "晴", "22~31", "5%")], aliases=["Nanjing"])
    yz = weather("扬州", "阴 23°C 体感 25°C 湿度 82% 风速 6 km/h",
                 [("2026-09-16", "阴", "20~25", "40%"), ("2026-09-17", "小雨", "19~24", "65%"),
                  ("2026-09-18", "阴", "19~25", "35%"), ("2026-09-19", "晴", "20~30", "10%"),
                  ("2026-09-20", "雷阵雨", "21~27", "75%")], aliases=["Yangzhou"])
    tpl = ["# 周末出行", "", "## 周六", "天气：（待填）", "", "## 周日", "天气：（待填）"]
    before = lines(tpl)
    sat, sun = "天气：多云 21~29°C，降水概率 20%", "天气：雷阵雨 21~27°C，降水概率 75%"
    after = lines(tpl[:3] + [sat] + tpl[4:6] + [sun])
    verify = '''
import json
case = json.load(open("case.json"))
path = "出行/周末.md"
before = case["files"][path]
assert before.startswith("# 周末出行") and before.count("天气：（待填）") == 2
nj, yz = (f["report"]["daily"] for f in case["weather_fixture"])
assert nj[3]["date"] == "2026-09-19" and yz[4]["date"] == "2026-09-20"
def fmt(d):
    low, high = d["temp_c"].split("~")
    return "天气：%s %s~%s°C，降水概率 %s" % (d["condition"], low, high, d["rain_chance"])
after = before.replace("天气：（待填）", fmt(nj[3]), 1).replace("天气：（待填）", fmt(yz[4]), 1)
print(json.dumps({"files": {path: after}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: 周六 / 周日 are 2026-09-19 / 09-20 (4th and 5th rows, so days must be >= 4 and >= 5); the second turn switches city AND day, so reusing the first forecast gives the wrong line.
- TR-DECOY: 南京 周日 is 晴 22~31°C 5% and 扬州 周六 is 晴 20~30°C 10%; only 南京 周六 (多云 21~29°C 20%) and 扬州 周日 (雷阵雨 21~27°C 75%) belong in the file.
Newline policy: only the placeholder line text is replaced, so every other line and the trailing newline stay as they are; the expected file is `before` with the two placeholders substituted (ends with one newline).

## Reference solution
Turn 1: get_weather {"location": "南京", "days": 4}; replace line 4 of 出行/周末.md; read_file 出行/周末.md.
Turn 2: get_weather {"location": "扬州", "days": 5}; replace line 7; read_file 出行/周末.md.
Final answer: 已把周日扬州的预报（雷阵雨 21~27°C，降水概率 75%）填进「周日」下面；周六南京是多云，文件里两天都已写好。

## Why the answer is unique
The line format is fixed by the prompt; city/day pairs and the fixed clock determine every value.
""" + phrasings("周六南京的天气填进周末出行文件", "把南京周六预报写进出行/周末.md 的周六一栏", "周日改去扬州，天气补上", "扬州周日天气写到文件里再核对", "Fill the weekend trip file with the forecasts.")
    fmt_line = "「天气：<天气> <最低>~<最高>°C，降水概率 <x>」"
    return write_case(
        "hyb-9043", desc="Two-turn: fills a weekend trip note with one city's forecast, then with another city and day after the plan changes",
        task_type="tool_then_write", family="fam-hyb-b12a-weekendnote-01", level="L2", ref_calls=6,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": None, "TR-DECOY": "晴 22~31°C 5%"}, axes=["OBS"],
        files={"出行/周末.md": before}, verify=verify, notes=notes, weather_fixture=[nj, yz],
        case_expect={"files": {"出行/周末.md": {"equals": after}}},
        turns=[{"prompt": "周六我去南京。查一下那天南京的天气，填进 出行/周末.md 里「周六」下面那行「天气：（待填）」，格式固定为"
                          + fmt_line + "，只替换这一行，其余各行和结尾换行都不要动。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}},
               {"prompt": "计划变了，周日改去扬州。同样查那天扬州的天气，按同样格式填进「周日」下面那行，填完确认一下文件。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9044():
    fx = [weather("Wuhan", "Cloudy 28°C feels 33°C humidity 80% wind 7 km/h",
                  [("2026-09-16", "Cloudy", "23~30", "30%"), ("2026-09-17", "Thundery showers", "24~31", "70%"),
                   ("2026-09-18", "Cloudy", "23~29", "25%")], aliases=["武汉"])]
    before = lines(["2026-09-14 Mon Wuhan Sunny 22-32C", "2026-09-15 Tue Wuhan Cloudy 22-30C"])
    line = "2026-09-17 Thu Wuhan Thundery showers 24-31C"
    verify = '''
import json
case = json.load(open("case.json"))
path = "logs/weather-log.txt"
before = case["files"][path]
assert before.startswith("2026-09-14 Mon Wuhan") and before.endswith(chr(10))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
line = "%s Thu Wuhan %s %s-%sC" % (day["date"], day["condition"], low, high)
print(json.dumps({"files": {path: before + line + chr(10)}}))
'''
    notes = """## Traps
- TR-DEFN: the log line carries the weekday abbreviation (2026-09-17 is Thu) which the forecast does not state; the unit is a bare C and the range uses a hyphen.
Newline policy: the prompt says the file already ends with a newline and must still end with exactly one newline after the new line (expected = before + line + "\\n").

## Reference solution
1. get_weather {"location": "Wuhan", "days": 3}
2. append_file logs/weather-log.txt with "2026-09-17 Thu Wuhan Thundery showers 24-31C\\n"
3. read_file logs/weather-log.txt to confirm
Final answer: Appended tomorrow's Wuhan forecast (thundery showers, 24-31C) to logs/weather-log.txt.

## Why the answer is unique
Tomorrow is the second forecast row; the line format is spelled out and the file ends with one newline.
""" + phrasings("Log tomorrow's Wuhan weather in the same style.", "Add one line for tomorrow to logs/weather-log.txt.", "Append Wuhan's forecast for 2026-09-17 to the weather log.", "Update the weather log with tomorrow's forecast.", "把武汉明天的天气按同样格式记到日志里")
    return write_case(
        "hyb-9044", desc="Appends tomorrow's forecast to a weather log in the style of its existing lines, with an explicit newline rule",
        task_type="tool_then_write", family="fam-hyb-b12a-weatherlog-01", level="L1", ref_calls=3,
        traps=["TR-DEFN"], decoys={"TR-DEFN": None}, axes=["OBS"],
        files={"logs/weather-log.txt": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"logs/weather-log.txt": {"equals": before + line + "\n"}}},
        turns=[{"prompt": "Add tomorrow's Wuhan forecast to logs/weather-log.txt as one new line in exactly the same style as the existing "
                          "lines (date, weekday abbreviation, city, condition, low-high with a C suffix). Each line, including yours, "
                          "ends with a newline, so the file must end with exactly one trailing newline after your line.",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9045():
    fx = [weather("重庆", "阴 27°C 体感 31°C 湿度 85% 风速 5 km/h",
                  [("2026-09-16", "阴", "24~30", "40%"), ("2026-09-17", "多云", "24~32", "25%"),
                   ("2026-09-18", "中雨", "22~27", "85%")], aliases=["Chongqing"])]
    before = lines(["# 天气速报", "", "- 城市：成都", "- 日期：2026-09-14", "- 天气：晴", "- 气温：20~29°C"])
    after = lines(["# 天气速报", "", "- 城市：重庆", "- 日期：2026-09-18", "- 天气：中雨", "- 气温：22~27°C"])
    verify = '''
import json
case = json.load(open("case.json"))
path = "报告/天气速报.md"
assert case["files"][path].startswith("# 天气速报")
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
low, high = day["temp_c"].split("~")
text = chr(10).join(["# 天气速报", "", "- 城市：重庆", "- 日期：" + day["date"], "- 天气：" + day["condition"],
                     "- 气温：%s~%s°C" % (low, high)]) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the old file holds another city and date; the whole file is overwritten, not appended to.
Newline policy: the prompt lists all six lines (including the blank second line) and says the file ends with exactly one newline after the last line; expected is those six lines joined by newlines plus one trailing newline.

## Reference solution
1. get_weather {"location": "重庆", "days": 3}
2. write_file 报告/天气速报.md (full new content)
3. read_file 报告/天气速报.md to confirm
Final answer: 已把重庆后天（2026-09-18）的预报（中雨，22~27°C）写进 报告/天气速报.md，旧内容已覆盖。

## Why the answer is unique
后天 is the third forecast row; the template is fully specified.
""" + phrasings("重庆后天的天气重做一份速报", "用重庆后天预报覆盖 报告/天气速报.md", "天气速报改成重庆 9 月 18 日", "更新速报文件，城市换成重庆、日期后天", "Rewrite the weather brief for Chongqing the day after tomorrow.")
    return write_case(
        "hyb-9045", desc="Overwrites a weather brief file with a day-after-tomorrow forecast in a fully specified six-line layout",
        task_type="tool_then_write", family="fam-hyb-b12a-weatherbrief-01", level="L1", ref_calls=3,
        traps=["TR-DEFN"], decoys={"TR-DEFN": "晴"}, axes=["OBS"],
        files={"报告/天气速报.md": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"报告/天气速报.md": {"equals": after}}},
        turns=[{"prompt": "把后天重庆的天气重新写进 报告/天气速报.md，整个文件覆盖成下面六行（第二行为空行）："
                          "「# 天气速报」「」「- 城市：重庆」「- 日期：<日期，格式 2026-09-18>」「- 天气：<天气>」「- 气温：<最低>~<最高>°C」。"
                          "每行都以换行结束，最后一行之后恰好一个换行，不要多余空行。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def composite(cid, *, city, current, rows, aliases, web, file, head, topic, desc, prompt, alts, reply, trap, decoy,
              day_idx, date, cond, fact, want, traps_note, query_hint):
    fx = [weather(city, current, rows, aliases=aliases)]
    files = {file[0]: lines(file[1])}
    verify = DAY % (0, day_idx, date) + '''assert case["files"][%r].startswith(%r)
fact = case["web_fixture"][0]["snippet"]
assert %r in fact and day["condition"] == %r
print(json.dumps({"expected_string": day["condition"] + " " + %r}, ensure_ascii=False))
''' % (file[0], head, fact, cond, want)
    notes = f"""## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast from get_weather ({traps_note}) and {query_hint} from web search; the weather part must not be searched.
- {trap}: {decoy[1]}

## Reference solution
1. get_weather {{"location": "{city}", "days": {day_idx + 1}}}
2. web_search {query_hint}
Final answer: {reply}

## Why the answer is unique
One forecast row and one web snippet each carry the unique value.
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12a-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-MULTISRC", trap], decoys={"TR-MULTISRC": decoy[0], trap: decoy[2]}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx, web=web,
        turns=[{"prompt": prompt,
                "expect": {"required_tools": ["get_weather", "web_search"], "output_contains": [cond, want],
                           "max_output_chars": 600}}])


def hyb_9046():
    web = [{"query_match": "马拉松", "url": "https://www.dlmarathon.example.cn/2026/signup", "url_match": "dlmarathon",
            "title": "2026 大连国际马拉松 报名须知",
            "snippet": "2026 大连国际马拉松全程报名费 198 元（2025 年为 168 元），报名截止 9 月 28 日。",
            "content": "# 报名须知\n\n2026 大连国际马拉松全程报名费 198 元（2025 年为 168 元），半程 128 元，报名截止 9 月 28 日。",
            "published_at": "2026-08-20"}]
    return composite(
        "hyb-9046", city="大连", aliases=["Dalian"], current="多云 21°C 体感 20°C 湿度 70% 风速 22 km/h",
        rows=[("2026-09-16", "多云", "18~23", "15%"), ("2026-09-17", "雷阵雨", "17~22", "65%"), ("2026-09-18", "晴", "16~24", "5%")],
        web=web, file=("跑步/计划.md", ["# 秋季跑步计划", "", "- 目标：大连全马"]), head="# 秋季跑步计划",
        topic="dalianrun", desc="Composite request: tomorrow's forecast from the weather tool plus a race fee from web search",
        prompt="明天我要在大连跑个晨跑，先看看那边明天的天气；另外帮我查下大连国际马拉松全程的报名费是多少。",
        alts=["大连明天天气如何？还有马拉松全程报名费多少", "查查大连国际马拉松全马报名费，顺便看明天大连天气", "明早大连跑步天气，加上马拉松报名价格",
              "大连明天会下雨吗，马拉松报名要多少钱", "Dalian weather tomorrow, and the 马拉松 (marathon) entry fee?"],
        reply="大连明天（9 月 17 日）有雷阵雨，降水概率 65%，17~22°C，晨跑建议改室内；2026 大连国际马拉松全程报名费 198 元（去年 168 元），9 月 28 日截止。",
        trap="TR-DECOY", decoy=("雷阵雨", "the web page also lists last year's fee 168; today's weather is 多云 (not tomorrow's).", "168"),
        day_idx=1, date="2026-09-17", cond="雷阵雨", fact="198 元", want="198",
        traps_note="明天 is the second row", query_hint="大连国际马拉松 报名费")


def hyb_9047():
    web = [{"query_match": "高铁", "url": "https://www.rail.example.cn/cs-zjj", "url_match": "rail.example",
            "title": "长沙南到张家界西 高铁时刻参考",
            "snippet": "长沙南—张家界西最快 G 字头列车全程约 1 小时 59 分，每天 14 趟。",
            "content": "# 时刻参考\n\n长沙南—张家界西最快 G 字头列车全程约 1 小时 59 分，每天 14 趟。",
            "published_at": "2026-07-01"}]
    return composite(
        "hyb-9047", city="长沙", aliases=["Changsha"], current="晴 29°C 体感 33°C 湿度 62% 风速 10 km/h",
        rows=[("2026-09-16", "晴", "24~32", "10%"), ("2026-09-17", "多云", "24~31", "20%"), ("2026-09-18", "中雨", "22~27", "80%")],
        web=web, file=("出游/张家界.md", ["# 张家界两日游", "", "- 周五出发"]), head="# 张家界两日游",
        topic="changshatrain", desc="Composite request: train duration from web search plus the day-after-tomorrow forecast from the weather tool",
        prompt="长沙到张家界的高铁最快要多久？顺便看下长沙后天的天气，我周五出发。",
        alts=["查下长沙到张家界高铁最快用时，再告诉我长沙后天天气", "周五从长沙去张家界，高铁多久，那天长沙天气怎样", "长沙后天天气和去张家界高铁时长",
              "长沙—张家界高铁最短多长时间？后天天气呢", "Changsha to Zhangjiajie 高铁 (high-speed train) time, and Changsha's weather the day after tomorrow?"],
        reply="长沙南到张家界西最快约 1 小时 59 分；长沙后天（9 月 18 日）中雨，降水概率 80%，22~27°C，出发记得带伞。",
        trap="TR-DECOY", decoy=("中雨", "tomorrow is 多云; only 后天 (2026-09-18) is 中雨.", "多云"),
        day_idx=2, date="2026-09-18", cond="中雨", fact="1 小时 59 分", want="59",
        traps_note="后天 is the third row", query_hint="长沙 张家界 高铁 最快时长")


def hyb_9048():
    fx = [weather("郑州", "多云 29°C 体感 31°C 湿度 58% 风速 11 km/h",
                  [("2026-09-16", "多云", "24~31", "20%"), ("2026-09-17", "晴", "26~34", "10%"),
                   ("2026-09-18", "多云", "25~32", "30%")], aliases=["Zhengzhou"])]
    rules = lines(["# 户外活动规则", "", "- 当日最高气温 ≥ 33°C：户外活动一律改到室内。",
                   "- 当日降水概率 ≥ 50%：户外活动一律改到室内。", "- 其余情况照常在户外进行。"])
    files = {"规则/户外活动.md": rules, "规则/说明.md": lines(["# 说明", "", "本目录存放学校日常规则。"])}
    verify = DAY % (0, 1, "2026-09-17") + '''rules = case["files"]["规则/户外活动.md"]
assert rules.startswith("# 户外活动规则") and "33°C" in rules and "50%" in rules
assert case["files"]["规则/说明.md"].startswith("# 说明")
assert int(day["temp_c"].split("~")[1]) >= 33 and int(day["rain_chance"].rstrip("%")) < 50
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
'''
    notes = """## Traps
- TR-RULEFILE: the go/no-go thresholds are in 规则/户外活动.md (high >= 33°C or rain >= 50%); 郑州 tomorrow is clear (10% rain) but its high 34°C crosses the heat limit, so common sense on rain alone says go outdoors.
- TR-DECOY: today's high is 31 (would pass).

## Reference solution
1. list_files / read_file 规则/户外活动.md
2. get_weather {"location": "郑州", "days": 3}
Final answer: 不能照常户外：郑州明天最高气温 34°C，达到规则里 33°C 的上限，户外拓展改到室内；降水概率只有 10%，不是雨的问题。

## Why the answer is unique
The rule and the forecast together decide; only the high temperature triggers it.
""" + phrasings("郑州明天户外活动要不要改室内？", "明天郑州的拓展训练还能在外面搞吗", "按学校规定，明天户外课行不行", "明天郑州户外活动按规则怎么安排", "Can tomorrow's outdoor activity in Zhengzhou go ahead under our rules?")
    return write_case(
        "hyb-9048", desc="Applies a local heat/rain threshold rule to tomorrow's forecast to decide on an outdoor activity",
        task_type="special_tool", family="fam-hyb-b12a-outdoorrule-01", level="L2", ref_calls=2,
        traps=["TR-RULEFILE", "TR-DECOY"], decoys={"TR-RULEFILE": "10%", "TR-DECOY": "31"}, axes=["DEC", "CHN", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "郑州明天下午学校的户外拓展活动，能照常在外面进行吗？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB,
                           "output_contains": ["34"], "output_contains_token": True,
                           "output_contains_any": ["室内"], "max_output_chars": 600}}])


def hyb_9049():
    fx = [weather("合肥", "阴 26°C 体感 28°C 湿度 74% 风速 9 km/h",
                  [("2026-09-16", "阴", "22~28", "40%"), ("2026-09-17", "多云", "22~29", "10%"),
                   ("2026-09-18", "中雨", "21~26", "80%")], aliases=["Hefei"])]
    rules = lines(["# 洗车建议规则", "", "- 看接下来两天（明天、后天）的预报：任一天降水概率 ≥ 30%，建议改天再洗。",
                   "- 两天都低于 30%，建议洗车，可顺便办理镀膜。"])
    files = {"门店/洗车规则.md": rules, "门店/价目.md": lines(["# 价目", "", "- 标准洗车 30 元", "- 镀膜 280 元"])}
    verify = DAY % (0, 2, "2026-09-18") + '''rules = case["files"]["门店/洗车规则.md"]
assert rules.startswith("# 洗车建议规则") and "两天" in rules and "30%" in rules
assert case["files"]["门店/价目.md"].startswith("# 价目") and "镀膜 280 元" in case["files"]["门店/价目.md"]
assert int(day["rain_chance"].rstrip("%")) >= 30 and int(report["daily"][1]["rain_chance"].rstrip("%")) < 30
print(json.dumps({"expected_string": day["rain_chance"]}))
'''
    notes = """## Traps
- TR-RULEFILE: the window is two days (明天 and 后天); the user asks about 明天 only, and tomorrow alone (10%) would say go ahead, but 后天 (80%) triggers the rule.
- TR-DECOY: today is 40%, outside the window.

## Reference solution
1. read_file 门店/洗车规则.md
2. get_weather {"location": "合肥", "days": 3}
Final answer: 建议改天：规则看明天和后天两天，合肥明天虽然只有 10%，但后天中雨、降水概率 80%，超过 30%，所以不建议现在洗车或办镀膜。

## Why the answer is unique
The local rule fixes a two-day window and a 30% threshold; the forecast supplies the rest.
""" + phrasings("合肥明天洗车合适吗？按店里规则", "明天去洗车会不会白洗", "合肥这两天适合洗车还是改天", "我想明天洗车加镀膜，行吗", "Is tomorrow a good day to wash the car in Hefei under the shop's rule?")
    return write_case(
        "hyb-9049", desc="Applies a shop's two-day rain-chance rule to the forecast to decide whether to wash a car tomorrow",
        task_type="special_tool", family="fam-hyb-b12a-carwashrule-01", level="L2", ref_calls=2,
        traps=["TR-RULEFILE", "TR-DECOY"], decoys={"TR-RULEFILE": "10%", "TR-DECOY": "40%"}, axes=["DEC", "CHN", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "我想明天在合肥洗个车，还想顺便做镀膜，合适吗？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB,
                           "output_contains": ["80%"],
                           "output_contains_any": ["改天", "推迟", "延后", "改期", "不建议"], "max_output_chars": 600}}])


def nt_9050():
    words = ["湿度", "风"]
    verify = '''
import json
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "体感温度" in prompt
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(words, ensure_ascii=False)
    notes = """## Traps
- TR-NOTOOLNEED: a definition question; get_weather is offered but no city or date is asked for.

## Reference solution
No tool call. Final answer: 体感温度是人实际感受到的冷热，不只看气温，还受湿度和风的影响：湿度高、无风时汗不易蒸发，感觉比气温更闷热；风大时带走体表热量，冬天会觉得更冷（风寒效应）。

## Why the answer is unique
Standard meteorological explanation; no location is named.
"""
    return write_case(
        "nt-9050", desc="Weather concept question (apparent temperature) with the weather tool offered; answered without any call",
        task_type="concept", family="fam-nt-b12a-feelslike-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "查一下今天的体感温度"}, axes=["DEC"],
        files={}, verify=verify, notes=notes,
        turns=[{"prompt": "天气预报里的「体感温度」是什么意思？为什么有时候比气温高很多？",
                "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words,
                           "max_output_chars": 600}}])


BUILDERS = [hyb_9039, hyb_9040, hyb_9041, hyb_9042, hyb_9043, hyb_9044, hyb_9045, hyb_9046, hyb_9047, hyb_9048,
            hyb_9049, nt_9050]

SPEC = {
    "hyb-9039": dict(kind="weather", sub="M10a"),
    "hyb-9040": dict(kind="weather", sub="M10a"),
    "hyb-9041": dict(kind="weather", sub="M10a"),
    "hyb-9042": dict(kind="weather_landmark", sub="M10a", landmark="洱海", city=("大理", "Dali")),
    "hyb-9043": dict(kind="weather_write", sub="M10b"),
    "hyb-9044": dict(kind="weather_write", sub="M10b"),
    "hyb-9045": dict(kind="weather_write", sub="M10b"),
    "hyb-9046": dict(kind="weather", sub="M10c"),
    "hyb-9047": dict(kind="weather", sub="M10c"),
    "hyb-9048": dict(kind="weather", sub="M10d", needs=["规则/户外活动.md"]),
    "hyb-9049": dict(kind="weather", sub="M10d", needs=["门店/洗车规则.md"]),
    "nt-9050": dict(kind="zero_call", sub="M10e"),
}
