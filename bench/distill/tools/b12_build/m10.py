"""M10: special-purpose tool first -- get_weather over web search (b12 pilot, part 1)."""
from common import lines, weather, write_case

REFS = {}


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))

# Every weather fixture starts at the work catalog's fixed today, 2026-09-16 (Wed).
VERIFY_DAY = '''
import json
case = json.load(open("case.json"))
for path, text in case["files"].items():
    assert text.startswith(%r), path
report = case["weather_fixture"][0]["report"]
day = report["daily"][%d]
'''


def hyb_9013():
    fx = [weather("厦门", "多云 28°C 体感 31°C 湿度 76% 风速 11 km/h",
                  [("2026-09-16", "多云", "25~31", "20%"), ("2026-09-17", "阵雨", "24~29", "60%"),
                   ("2026-09-18", "晴", "25~32", "10%")], aliases=["Xiamen"])]
    files = {"出差/行程.md": lines(["# 出差行程", "", "9 月 17 日 厦门 客户拜访"])}
    verify = VERIFY_DAY % ("# 出差行程", 1) + 'print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))\n'
    notes = """## Traps
- TR-DECOY: today's high is 31; tomorrow (2026-09-17) is 29.

## Reference solution
1. get_weather {"location": "厦门", "days": 3}
Final answer: 厦门明天（9 月 17 日）有阵雨，最高 29°C、最低 24°C。

## Why the answer is unique
The fixed clock makes 明天 = 2026-09-17; the forecast row is labelled 明天.
""" + phrasings("明天厦门热不热，最高几度？", "厦门明天气温多少？", "明天去厦门，最高温度会到多少？", "厦门 9 月 17 日最高气温", "What is tomorrow's high in Xiamen?")
    return write_case(
        "hyb-9013", desc="Asks tomorrow's high temperature for a city; get_weather answers it directly",
        task_type="special_tool", family="fam-hyb-b12-weatherhigh-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "31"}, axes=["OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "厦门明天最高气温多少度？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "output_contains": ["29"], "output_contains_token": True, "max_output_chars": 600}}])


def hyb_9014():
    fx = [weather("厦门", "晴 27°C 体感 29°C 湿度 70% 风速 9 km/h",
                  [("2026-09-16", "晴", "24~30", "10%"), ("2026-09-17", "多云", "24~29", "30%"),
                   ("2026-09-18", "中雨", "23~27", "75%")], aliases=["Xiamen"])]
    files = {"旅行/清单.md": lines(["# 旅行清单", "", "- 9 月 18 日 上鼓浪屿"])}
    verify = VERIFY_DAY % ("# 旅行清单", 2) + 'print(json.dumps({"expected_string": day["rain_chance"]}))\n'
    notes = """## Traps
- TR-NEARNAME: 鼓浪屿 is an island district of 厦门, not a city; get_weather resolves cities, so asking for 鼓浪屿 returns location not found and the retry is 厦门.
- TR-DECOY: tomorrow is 30%; 后天 (2026-09-18) is 75%.

## Reference solution
1. get_weather {"location": "厦门", "days": 3} (or 鼓浪屿 first, then 厦门 after the not-found error)
Final answer: 后天（9 月 18 日）厦门有中雨，降水概率 75%，上鼓浪屿记得带伞；鼓浪屿属于厦门，按厦门的预报看。

## Why the answer is unique
后天 is the third forecast row; the island has no separate forecast.
""" + phrasings("鼓浪屿后天天气怎么样？", "后天上鼓浪屿要带伞吗？", "厦门后天下不下雨？", "9 月 18 日鼓浪屿会下雨吗？", "Will it rain on Gulangyu the day after tomorrow?")
    return write_case(
        "hyb-9014", desc="Asks about rain at a landmark the day after tomorrow; the forecast must be looked up by its city",
        task_type="special_tool", family="fam-hyb-b12-landmarkrain-01", level="L2", ref_calls=1,
        traps=["TR-NEARNAME", "TR-DECOY"], decoys={"TR-NEARNAME": "UNKNOWN", "TR-DECOY": "30%"}, axes=["ERR", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "我后天去鼓浪屿玩，会下雨吗？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "output_contains": ["75%"], "max_output_chars": 600}}])


def hyb_9015():
    fx = [weather("青岛", "晴 22°C 体感 22°C 湿度 64% 风速 15 km/h",
                  [("2026-09-16", "晴", "18~24", "5%"), ("2026-09-17", "多云", "19~25", "15%"),
                   ("2026-09-18", "小雨", "18~22", "65%")], aliases=["Qingdao"])]
    before = lines(["# 青岛三日行程", "", "## 天气", "（示例行：- 09-01 周一 晴 20~28°C）", "", "## 安排",
                    "- 周三 栈桥、天主教堂", "- 周四 崂山", "- 周五 啤酒博物馆"])
    weekdays = ["周三", "周四", "周五"]
    rows = [f"- {d[5:]} {w} {c} {t}°C" for (d, c, t, _), w in zip(
        [("2026-09-16", "晴", "18~24", ""), ("2026-09-17", "多云", "19~25", ""), ("2026-09-18", "小雨", "18~22", "")], weekdays)]
    after = before.replace("（示例行：- 09-01 周一 晴 20~28°C）\n", "（示例行：- 09-01 周一 晴 20~28°C）\n" + "".join(r + "\n" for r in rows))
    files = {"行程/青岛.md": before}
    verify = '''
import json
case = json.load(open("case.json"))
before = case["files"]["行程/青岛.md"]
anchor = "（示例行：- 09-01 周一 晴 20~28°C）" + chr(10)
assert before.startswith("# 青岛三日行程") and anchor in before
week = ["周三", "周四", "周五"]
rows = "".join("- %s %s %s %s°C" % (d["date"][5:], w, d["condition"], d["temp_c"]) + chr(10)
               for d, w in zip(case["weather_fixture"][0]["report"]["daily"], week))
print(json.dumps({"files": {"行程/青岛.md": before.replace(anchor, anchor + rows)}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the example row carries a weekday; 2026-09-16..18 are 周三..周五, which the forecast does not state.
Lesson: closing the loop -- weather in hand, write the artifact instead of searching more (2026-10-09 App failure).

## Reference solution
1. read_file 行程/青岛.md (example row format)
2. get_weather {"location": "青岛", "days": 3}
3. replace_lines / write_file: three rows under the example line
4. read_file 行程/青岛.md once to confirm
Final answer: 已把青岛 9 月 16–18 日的天气按示例格式写进 行程/青岛.md 的「天气」小节（周五有小雨）。

## Why the answer is unique
Row format comes from the example line; dates and weekdays follow the fixed clock.
""" + phrasings("把青岛未来三天天气补进行程文件", "青岛三天天气写到行程的天气小节", "按示例格式记录青岛这三天的天气", "行程/青岛.md 的天气部分帮我填上", "Fill in the Qingdao trip note with the 3-day forecast.")
    return write_case(
        "hyb-9015", desc="Looks up a three-day forecast and writes it into a trip note in the format of its example row",
        task_type="tool_then_write", family="fam-hyb-b12-weathernote-01", level="L1", ref_calls=4,
        traps=["TR-DEFN"], decoys={"TR-DEFN": None}, axes=["OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"行程/青岛.md": {"equals": after}}},
        turns=[{"prompt": "查一下青岛这三天的天气，按 行程/青岛.md 里示例行的格式，写到「天气」小节的示例行下面，每天一行。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "max_output_chars": 600}}])


def hyb_9016():
    fx = [weather("Shenzhen", "Partly cloudy 29°C feels 33°C humidity 78% wind 12 km/h",
                  [("2026-09-16", "Partly cloudy", "26~31", "20%"), ("2026-09-17", "Thundery showers", "25~30", "70%"),
                   ("2026-09-18", "Sunny", "26~32", "10%")], aliases=["深圳"])]
    before = lines(["# Site visit: Shenzhen assembly line", "", "Date: Thursday 2026-09-17", "Attendees: QA, procurement", ""])
    line = "Weather: Thundery showers, 25-30°C, 70% chance of rain"
    files = {"ops/site-visit.md": before}
    verify = '''
import json
case = json.load(open("case.json"))
before = case["files"]["ops/site-visit.md"]
assert before.startswith("# Site visit: Shenzhen") and "Thursday 2026-09-17" in before
day = case["weather_fixture"][0]["report"]["daily"][1]
low, high = day["temp_c"].split("~")
line = "Weather: %s, %s-%s°C, %s chance of rain" % (day["condition"], low, high, day["rain_chance"])
print(json.dumps({"files": {"ops/site-visit.md": before + line + chr(10)}}, ensure_ascii=False))
'''
    notes = """## Traps
None: weather lookup followed by an append in the exact line format the prompt gives.

## Reference solution
1. get_weather {"location": "Shenzhen", "days": 3}
2. append_file ops/site-visit.md with the line
3. read_file ops/site-visit.md to confirm
Final answer: Added Thursday's forecast (thundery showers, 25-30°C, 70% rain) to the end of ops/site-visit.md.

## Why the answer is unique
The visit date is Thursday 2026-09-17, the second forecast row; the line format is spelled out.
""" + phrasings("Put the Shenzhen forecast for Thursday into the visit notes.", "Note the weather for the site visit day.", "What's the weather for our Shenzhen visit? Add it to the notes.", "Append Thursday's Shenzhen weather to ops/site-visit.md.", "把周四深圳的天气记到拜访纪要里")
    return write_case(
        "hyb-9016", desc="Appends the forecast for a site visit day to a notes file in a prescribed line format",
        task_type="tool_then_write", family="fam-hyb-b12-sitevisit-01", level="L0", ref_calls=3,
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"ops/site-visit.md": {"equals": before + line + "\n"}}},
        turns=[{"prompt": "Add the forecast for the visit day to the end of ops/site-visit.md as one line: "
                          "Weather: <condition>, <low>-<high>°C, <rain chance> chance of rain",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "max_output_chars": 600}}])


BUILDERS = [hyb_9013, hyb_9014, hyb_9015, hyb_9016]
