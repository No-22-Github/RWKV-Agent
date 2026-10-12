"""M10 (b12e): two-turn get_weather cases, ids hyb-9133..9138.

Fixture clock is 2026-09-16 (Wed): 明天 = 09-17 (Thu), 后天 = 09-18 (Fri), 周六 = 09-19.
M10b weather -> file (9133-9136): turn 2 changes the city or the day, so a second lookup and a second write are needed
(shape of ../b12a/m10.py hyb_9043). M10a (9137, 9138): direct answers in two turns, the second with a new city or a landmark.
Every write prompt states the exact line format and the newline rule; the expected file is compared exactly."""
import json

from common import phrasings, verify_src, weather, write_case, lines

REFS = {}
NOWEB = ["web_search", "web_fetch"]
WEXP = {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}
FMT = "「<天气> <最低>~<最高>°C，降水概率 <x>」"


def write_case_two(cid, *, desc, family, level, files, after, fx, body, trap_note, reply, why, alts, prompts, decoy):
    notes = f"""## Traps
{trap_note}
Newline policy: only the named lines are replaced/appended, so every other line and the single trailing newline stay as they are.

## Reference solution
Turn 1: get_weather for the first city; edit the file; read_file to confirm.
Turn 2: get_weather for the new city/day (a different forecast is needed); edit the file again; read_file to confirm.
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    path = next(iter(files))
    return write_case(
        cid, desc=desc, task_type="tool_then_write", family=family, level=level, ref_calls=6,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": None, "TR-DECOY": decoy}, axes=["OBS"], files=files,
        verify=verify_src(files, body), notes=notes, weather_fixture=fx, case_expect={"files": {path: {"equals": after}}},
        turns=[{"prompt": p, "expect": dict(WEXP)} for p in prompts])


def hyb_9133():
    hz = weather("杭州", "多云 25°C 体感 27°C 湿度 70% 风速 9 km/h",
                 [("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "小雨", "21~26", "65%"), ("2026-09-18", "阴", "21~27", "35%")], aliases=["Hangzhou"])
    sz = weather("苏州", "阴 24°C 体感 26°C 湿度 76% 风速 7 km/h",
                 [("2026-09-16", "阴", "21~27", "30%"), ("2026-09-17", "中雨", "20~25", "80%"), ("2026-09-18", "多云", "21~28", "25%")], aliases=["Suzhou"])
    before = lines(["# 明日出行", "", "- 地点：杭州", "- 天气：（待填）"])
    after = lines(["# 明日出行", "", "- 地点：苏州", "- 天气：中雨 20~25°C，降水概率 80%"])
    body = r'''
path = "行程/明日.md"
rows = case["files"][path].splitlines()
assert rows == ["# 明日出行", "", "- 地点：杭州", "- 天气：（待填）"]
hz, sz = (f["report"]["daily"][1] for f in case["weather_fixture"])
assert hz["date"] == "2026-09-17" and sz["date"] == "2026-09-17"
low, high = sz["temp_c"].split("~")
rows[2] = "- 地点：苏州"
rows[3] = "- 天气：%s %s~%s°C，降水概率 %s" % (sz["condition"], low, high, sz["rain_chance"])
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
'''
    return write_case_two(
        "hyb-9133", desc="Two turns: fills tomorrow's forecast for one city into a trip note, then the plan moves to another city and both the place line and the forecast line change",
        family="fam-hyb-b12e-citychange-01", level="L2", files={"行程/明日.md": before}, after=after, fx=[hz, sz], body=body,
        trap_note="- TR-DEFN: turn 2 changes the city, so the 杭州 forecast (小雨 21~26°C 65%) must be replaced, not kept; both the 地点 line and the 天气 line change.\n- TR-DECOY: 苏州 today is 阴 21~27°C 30% and the day after is 多云; only tomorrow's row (中雨 20~25°C 80%) belongs in the file.",
        reply="已把 行程/明日.md 改成苏州：地点是苏州，天气是中雨 20~25°C，降水概率 80%。",
        why="The line formats are fixed by the prompts; 明天 = 2026-09-17 is the second forecast row of each city.",
        alts=["明天改去苏州，文件里的地点和天气一起换掉", "把明日出行改成苏州明天的预报", "杭州换成苏州，天气行用苏州明天的数据", "行程文件先填杭州天气，再改成苏州", "Fill the trip note with Hangzhou's forecast, then change it to Suzhou."],
        decoy="阴 21~27°C 30%",
        prompts=["明天我去杭州。查一下杭州明天的天气，填进 行程/明日.md 里「天气：（待填）」那一行，格式固定为「- 天气：<condition> <low>~<high>°C，降水概率 <rain>」" + "，只替换这一行，其余各行和结尾换行都不要动。",
                 "计划变了，明天改去苏州。把「地点」那行改成苏州，「天气」那行换成苏州明天的预报，格式不变，其余各行和结尾换行都不要动。"])


def hyb_9134():
    cd = weather("成都", "阴 23°C 体感 25°C 湿度 80% 风速 5 km/h",
                 [("2026-09-16", "阴", "20~25", "40%"), ("2026-09-17", "阵雨", "19~24", "70%"), ("2026-09-18", "多云", "20~27", "25%")], aliases=["Chengdu"])
    cq = weather("重庆", "多云 29°C 体感 33°C 湿度 72% 风速 6 km/h",
                 [("2026-09-16", "多云", "24~32", "20%"), ("2026-09-17", "雷阵雨", "24~31", "60%"), ("2026-09-18", "晴", "25~34", "5%")], aliases=["Chongqing"])
    before = lines(["# 跑步计划", "", "## 周四 成都", "- 天气：（待填）", "", "## 备注", "- 目标配速 6:00"])
    after = lines(["# 跑步计划", "", "## 周五 重庆", "- 天气：晴 25~34°C，降水概率 5%", "", "## 备注", "- 目标配速 6:00"])
    body = r'''
path = "运动/跑步计划.md"
rows = case["files"][path].splitlines()
assert rows == ["# 跑步计划", "", "## 周四 成都", "- 天气：（待填）", "", "## 备注", "- 目标配速 6:00"]
cd, cq = (f["report"]["daily"] for f in case["weather_fixture"])
assert cd[1]["date"] == "2026-09-17" and cq[2]["date"] == "2026-09-18"
day = cq[2]
low, high = day["temp_c"].split("~")
rows[2] = "## 周五 重庆"
rows[3] = "- 天气：%s %s~%s°C，降水概率 %s" % (day["condition"], low, high, day["rain_chance"])
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
'''
    return write_case_two(
        "hyb-9134", desc="Two turns: fills tomorrow's forecast for a run into a plan note, then the run moves to the day after tomorrow in another city and the heading and forecast line change",
        family="fam-hyb-b12e-runmove-01", level="L3", files={"运动/跑步计划.md": before}, after=after, fx=[cd, cq], body=body,
        trap_note="- TR-DEFN: turn 2 changes both day and city, so the heading line and the forecast line must both change; 周五 = 2026-09-18 = 后天, the third row of the 重庆 forecast (days >= 3).\n- TR-DECOY: 重庆 tomorrow is 雷阵雨 24~31°C 60%; 成都 tomorrow was 阵雨 19~24°C 70% from turn 1.",
        reply="已把 运动/跑步计划.md 改成周五在重庆跑：天气是晴 25~34°C，降水概率 5%。",
        why="The heading text is dictated by the prompt and the forecast line comes from the third row of 重庆's forecast.",
        alts=["跑步改到周五去重庆，标题和天气一起更新", "把跑步计划换成重庆后天的预报", "先填成都明天，再把计划挪到周五重庆", "跑步计划：周四成都改为周五重庆并更新天气", "Move the run to Friday in Chongqing and update the weather line."],
        decoy="雷阵雨 24~31°C 60%",
        prompts=["周四（明天）我在成都跑步。查一下成都明天的天气，填进 运动/跑步计划.md 里「天气：（待填）」那一行，格式固定为「- 天气：<cond> <min>~<max>°C，降水概率 <pct>」" + "，只替换这一行，其余各行和结尾换行都不要动。",
                 "跑步改到后天（周五）、地点改去重庆：把「## 周四 成都」那行改成「## 周五 重庆」，天气那一行换成重庆后天的预报，格式不变，其余各行和结尾换行都不要动。"])


def hyb_9135():
    tk = weather("Tokyo", "Clear 24°C feels 26°C humidity 60% wind 10 km/h",
                 [("2026-09-16", "Clear", "19~27", "5%"), ("2026-09-17", "Light rain", "18~24", "60%"), ("2026-09-18", "Cloudy", "18~25", "30%")], aliases=["东京"])
    os_ = weather("Osaka", "Sunny 28°C feels 31°C humidity 58% wind 8 km/h",
                  [("2026-09-16", "Sunny", "23~31", "5%"), ("2026-09-17", "Cloudy", "22~30", "25%"), ("2026-09-18", "Sunny", "22~31", "10%")], aliases=["大阪"])
    before = lines(["2026-09-14 Mon Seoul Clear 17-26C", "2026-09-15 Tue Seoul Cloudy 16-25C"])
    l1, l2 = "2026-09-17 Thu Tokyo Light rain 18-24C", "2026-09-18 Fri Osaka Sunny 22-31C"
    body = r'''
path = "logs/trip-weather.txt"
before = case["files"][path]
assert before.startswith("2026-09-14 Mon Seoul") and before.endswith(chr(10))
tk, os_ = (f["report"]["daily"] for f in case["weather_fixture"])
assert tk[1]["date"] == "2026-09-17" and os_[2]["date"] == "2026-09-18"
def line(d, wd, city):
    low, high = d["temp_c"].split("~")
    return "%s %s %s %s %s-%sC" % (d["date"], wd, city, d["condition"], low, high)
print(json.dumps({"files": {path: before + line(tk[1], "Thu", "Tokyo") + chr(10) + line(os_[2], "Fri", "Osaka") + chr(10)}}))
'''
    notes = """## Traps
- TR-DEFN: weekday abbreviations are not in the forecast (2026-09-17 is Thu, 2026-09-18 is Fri); bare C suffix, hyphenated range. Turn 2 is another city and another day (the third row), so turn 1's data is not enough and the new line is appended after the first one.
- TR-DECOY: Tokyo's day-after-tomorrow row (Cloudy 18-25C) is not what Osaka's line needs; Osaka tomorrow is Cloudy 22-30C.
Newline policy: expected = before + line1 + "\\n" + line2 + "\\n" (one trailing newline).

## Reference solution
Turn 1: get_weather {"location": "Tokyo", "days": 3}; append_file logs/trip-weather.txt with line 1; read_file to confirm.
Turn 2: get_weather {"location": "Osaka", "days": 3}; append_file with line 2; read_file to confirm.
Final answer: Appended Osaka's forecast for the day after tomorrow (Sunny, 22-31C) after the Tokyo line in logs/trip-weather.txt.

## Why the answer is unique
The line layout is spelled out; 明天/the day after tomorrow resolve to 2026-09-17 / 2026-09-18 on the fixed clock.
""" + phrasings("Log Tokyo tomorrow and Osaka the day after tomorrow in the trip weather file.", "Add two forecast lines to logs/trip-weather.txt, Tokyo first, then Osaka.", "Append tomorrow's Tokyo weather, then the day-after-tomorrow Osaka weather, in the same style.", "Record Tokyo (tomorrow) and Osaka (day after) at the end of the weather log.", "把东京明天、大阪后天的天气按原格式依次追加到日志")
    return write_case(
        "hyb-9135", desc="Two turns: appends tomorrow's forecast for one city to a trip weather log, then appends another city's day-after-tomorrow forecast in the same style",
        task_type="tool_then_write", family="fam-hyb-b12e-tripweatherlog-01", level="L2", ref_calls=6,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": None, "TR-DECOY": "Cloudy 22-30C"}, axes=["OBS"],
        files={"logs/trip-weather.txt": before}, verify=verify_src({"logs/trip-weather.txt": before}, body), notes=notes, weather_fixture=[tk, os_],
        case_expect={"files": {"logs/trip-weather.txt": {"equals": before + l1 + "\n" + l2 + "\n"}}},
        turns=[{"prompt": "Log tomorrow's Tokyo weather in logs/trip-weather.txt: one new line at the end, laid out like the lines already there (date, weekday abbreviation, city, condition, low-high with a trailing C). "
                          "The file ends with a newline and must keep ending with exactly one.", "expect": dict(WEXP)},
               {"prompt": "Now Osaka too: add one more line after it for Osaka's forecast on the day after tomorrow, same layout, still exactly one newline at the very end.", "expect": dict(WEXP)}])


def hyb_9136():
    qd = weather("青岛", "多云 23°C 体感 24°C 湿度 66% 风速 15 km/h",
                 [("2026-09-16", "晴", "18~24", "5%"), ("2026-09-17", "多云", "19~25", "15%"), ("2026-09-18", "小雨", "18~22", "65%")], aliases=["Qingdao"])
    dl = weather("大连", "晴 21°C 体感 21°C 湿度 55% 风速 17 km/h",
                 [("2026-09-16", "晴", "16~23", "0%"), ("2026-09-17", "晴", "17~24", "5%"), ("2026-09-18", "阵雨", "16~21", "55%")], aliases=["Dalian"])
    head = ["# 出游天气表", "", "| 日期 | 城市 | 天气 | 气温 |", "| --- | --- | --- | --- |", "| 09-15 | 厦门 | 晴 | 25~31°C |"]
    before = lines(head)
    after = lines(head + ["| 09-17 | 青岛 | 多云 | 19~25°C |", "| 09-18 | 大连 | 阵雨 | 16~21°C |"])
    body = r'''
path = "出游/天气表.md"
rows = case["files"][path].splitlines()
assert rows[:2] == ["# 出游天气表", ""] and rows[3] == "| --- | --- | --- | --- |" and len(rows) == 5
qd, dl = (f["report"]["daily"] for f in case["weather_fixture"])
assert qd[1]["date"] == "2026-09-17" and dl[2]["date"] == "2026-09-18"
def row(d, city):
    low, high = d["temp_c"].split("~")
    return "| %s | %s | %s | %s~%s°C |" % (d["date"][5:], city, d["condition"], low, high)
rows += [row(qd[1], "青岛"), row(dl[2], "大连")]
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
'''
    return write_case_two(
        "hyb-9136", desc="Two turns: appends a forecast row for one city to a markdown weather table, then a row for another city and day",
        family="fam-hyb-b12e-weathertable-01", level="L2", files={"出游/天气表.md": before}, after=after, fx=[qd, dl], body=body,
        trap_note="- TR-DEFN: turn 2 is another city and another day (后天 = 09-18, the third row), so a second lookup is needed and the new row goes after the first appended one; the date column is 月-日 only.\n- TR-DECOY: 大连 tomorrow is 晴 17~24°C 5%; only the third row (阵雨 16~21°C) belongs in the table.",
        reply="已把大连后天（09-18）的预报（阵雨 16~21°C）追加到 出游/天气表.md，青岛明天那一行在上面。",
        why="Row layout and dates are fixed by the prompts; the existing rows stay in place and the file ends with one newline.",
        alts=["天气表里先加青岛明天，再加大连后天", "往出游天气表追加两行：青岛（明天）和大连（后天）", "把青岛、大连的预报依次填成表格行", "出游表格追加大连后天的天气一行", "Append Qingdao's and then Dalian's forecast as table rows."],
        decoy="晴 17~24°C 5%",
        prompts=["在 出游/天气表.md 表格最后追加一行青岛明天的天气，格式「| <月-日> | 青岛 | <天气> | <最低>~<最高>°C |」，其余各行不动，文件仍以换行结尾。",
                 "再加一行大连后天的天气，格式同上，追加在刚才那行的后面，其余各行不动，文件仍以换行结尾。"])


def two_direct(cid, *, desc, family, level, fx, body, files, traps, decoys, trap_note, replies, why, alts, prompts, contains, axes=("OBS", "CHN"), landmark=False):
    notes = f"""## Traps
{trap_note}

## Reference solution
Turn 1: get_weather for the first place, answer. Turn 2: get_weather for the new place (a second lookup is needed), answer.
Final answers: {replies}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="special_tool", family=family, level=level, ref_calls=2, traps=traps, decoys=decoys, axes=list(axes),
        files=files, verify=verify_src(files, body), notes=notes, weather_fixture=fx,
        turns=[{"prompt": p, "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "output_contains": [c], "max_output_chars": 600}}
               for p, c in zip(prompts, contains)])


def hyb_9137():
    sh = weather("上海", "多云 27°C 体感 31°C 湿度 74% 风速 11 km/h",
                 [("2026-09-16", "多云", "24~30", "20%"), ("2026-09-17", "多云", "25~31", "15%"), ("2026-09-18", "阴", "24~29", "30%")], aliases=["Shanghai"])
    bj = weather("北京", "晴 22°C 体感 21°C 湿度 45% 风速 12 km/h",
                 [("2026-09-16", "晴", "15~26", "0%"), ("2026-09-17", "晴", "16~27", "5%"), ("2026-09-18", "阵雨", "17~24", "70%")], aliases=["Beijing"])
    body = r'''
sh, bj = (f["report"]["daily"] for f in case["weather_fixture"])
assert sh[1]["date"] == "2026-09-17" and bj[2]["date"] == "2026-09-18"
assert sh[1]["temp_c"].split("~")[1] == "31"
print(json.dumps({"expected_number": int(bj[2]["temp_c"].split("~")[1])}))
'''
    return two_direct(
        "hyb-9137", desc="Two turns: tomorrow's high temperature for one city, then the day after tomorrow's rain and high for another city",
        family="fam-hyb-b12e-twocities-01", level="L3", fx=[sh, bj], body=body, files={}, traps=["TR-DECOY"], decoys={"TR-DECOY": "27"},
        trap_note="- TR-DECOY: turn 2 asks 后天 (2026-09-18, third row) for 北京; 北京 tomorrow's high is 27 and 上海's numbers from turn 1 do not apply.",
        replies="上海明天最高 31°C；北京后天有阵雨（降水概率 70%），最高 24°C。",
        why="The fixed clock gives 明天 = 09-17 and 后天 = 09-18; each city has its own forecast rows.",
        alts=["明天上海最高几度，后天北京呢？", "先告诉我上海明天最高温，再看北京后天会不会下雨", "上海明天高温多少；北京后天下雨吗、最高多少", "9 月 17 日上海最高气温，以及 9 月 18 日北京的天气", "What is Shanghai's high tomorrow, and what about Beijing the day after?"],
        prompts=["明天上海最高气温多少度？", "那后天北京呢？会下雨吗，最高多少度？"], contains=["31", "24"])


def hyb_9138():
    hz = weather("杭州", "多云 25°C 体感 27°C 湿度 70% 风速 9 km/h",
                 [("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "小雨", "21~26", "65%"), ("2026-09-18", "阴", "21~27", "35%")], aliases=["Hangzhou"])
    gl = weather("桂林", "多云 30°C 体感 36°C 湿度 78% 风速 6 km/h",
                 [("2026-09-16", "多云", "25~33", "25%"), ("2026-09-17", "雷阵雨", "24~31", "70%"), ("2026-09-18", "阴", "24~30", "40%"),
                  ("2026-09-19", "晴", "25~34", "10%"), ("2026-09-20", "多云", "25~32", "20%")], aliases=["Guilin"])
    body = r'''
hz, gl = (f["report"]["daily"] for f in case["weather_fixture"])
assert hz[2]["date"] == "2026-09-18" and hz[2]["rain_chance"] == "35%"
assert gl[3]["date"] == "2026-09-19"
print(json.dumps({"expected_number": int(gl[3]["temp_c"].split("~")[1])}))
'''
    return two_direct(
        "hyb-9138", desc="Two turns: rain chance at a lake district the day after tomorrow, then Saturday's high at a river sightseeing spot; both forecasts must be looked up by their cities",
        family="fam-hyb-b12e-twolandmarks-01", level="L3", fx=[hz, gl], body=body, files={}, traps=["TR-NEARNAME", "TR-DECOY"],
        decoys={"TR-NEARNAME": "UNKNOWN", "TR-DECOY": "34"}, axes=("OBS", "CHN", "ERR"),
        trap_note="- TR-NEARNAME: 西湖 and 漓江 are sights, not cities; get_weather resolves 杭州 and 桂林. 周六 = 2026-09-19 is the 4th row for 桂林 (days must be >= 4).\n- TR-DECOY: 桂林 on Sunday is 25~32 and on 后天 30; Saturday's high is 34.",
        replies="杭州后天（9 月 18 日）降水概率 35%；桂林周六（9 月 19 日）晴，最高 34°C。",
        why="Landmarks map to their cities (杭州, 桂林) and the fixed clock fixes the days.",
        alts=["后天去西湖会下雨吗？周六漓江天气怎样、最高几度？", "西湖后天降水概率，以及漓江周六的最高气温", "后天杭州的雨，周六桂林的高温", "先查后天西湖的天气，再查周六漓江", "Chance of rain at West Lake the day after tomorrow, then the high on Saturday at the Li River?"],
        prompts=["后天我想去西湖边走走，那天会下雨吗？", "再问一下，周六我要去漓江坐竹筏，那天最高气温是多少？"], contains=["35", "34"])


BUILDERS = [hyb_9133, hyb_9134, hyb_9135, hyb_9136, hyb_9137, hyb_9138]

SPEC = {
    "hyb-9133": dict(kind="weather_write", sub="M10b"),
    "hyb-9134": dict(kind="weather_write", sub="M10b"),
    "hyb-9135": dict(kind="weather_write", sub="M10b"),
    "hyb-9136": dict(kind="weather_write", sub="M10b"),
    "hyb-9137": dict(kind="weather", sub="M10a", dates=["2026-09-18"]),
    "hyb-9138": dict(kind="weather_landmark", sub="M10a", landmark="漓江", city=("桂林", "Guilin")),
}
