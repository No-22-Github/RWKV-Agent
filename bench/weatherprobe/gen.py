#!/usr/bin/env python3
"""Generate bench/weatherprobe/cases: get_weather probes for the agent-tool-v2.0 catalog.

    python3 bench/weatherprobe/gen.py

Every answer comes from the per-case weather_fixture written here (fixed
clock 2026-09-16, so 明天 = 09-17 and 后天 = 09-18). The axes follow the
2026-10-09 live probe: explicit asks, implicit needs (umbrella, clothing),
weather feeding an artifact (where the model used to switch to web_search),
a second city in a later turn, an unknown city, and questions that must not
call get_weather. Run with --tool-catalog agent-tool-v2.0 --include-draft.
"""
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANARY = "WEATHERPROBE-CANARY-3b9e51a2"
DATES = ("2026-09-16", "2026-09-17", "2026-09-18")
NO_WEB = ["web_search", "web_fetch"]


def city(name, aliases, region, current, days):
    """days: three (condition, low, high, rain_chance) rows for DATES."""
    return {"location": name, "aliases": aliases, "report": {
        "location": f"{name}，{region}，中国", "current": current, "source": "fixture",
        "daily": [{"date": d, "condition": c, "temp_c": f"{lo}~{hi}", "rain_chance": f"{r}%"}
                  for d, (c, lo, hi, r) in zip(DATES, days)]}}


BEIJING = city("北京", ["Beijing"], "北京", "晴 24°C 体感 23°C 湿度 35% 风速 12 km/h",
               [("晴", 18, 28, 0), ("多云", 17, 26, 10), ("晴", 16, 27, 0)])
SHANGHAI = city("上海", ["Shanghai"], "上海", "阴 29°C 体感 33°C 湿度 78% 风速 10 km/h",
                [("阴", 26, 33, 30), ("大雨", 23, 27, 90), ("多云", 24, 30, 20)])
GUANGZHOU = city("广州", ["Guangzhou"], "广东", "多云 30°C 体感 35°C 湿度 75% 风速 8 km/h",
                 [("多云", 26, 31, 20), ("晴", 26, 32, 10), ("晴", 27, 34, 5)])
SHENZHEN = city("深圳", ["Shenzhen"], "广东", "多云 29°C 体感 34°C 湿度 80% 风速 11 km/h",
                [("多云", 26, 31, 30), ("雷阵雨", 25, 30, 80), ("阵雨", 25, 31, 60)])
HANGZHOU = city("杭州", ["Hangzhou"], "浙江", "小雨 21°C 体感 22°C 湿度 88% 风速 9 km/h",
                [("小雨", 19, 24, 70), ("中雨", 18, 23, 80), ("阴", 18, 25, 40)])
HARBIN = city("哈尔滨", ["Harbin"], "黑龙江", "晴 8°C 体感 5°C 湿度 40% 风速 18 km/h",
              [("晴", 3, 12, 0), ("多云", 2, 10, 10), ("小雪", -1, 4, 70)])
CHENGDU = city("成都", ["Chengdu"], "四川", "阴 23°C 体感 24°C 湿度 81% 风速 6 km/h",
               [("阴", 20, 25, 40), ("小雨", 19, 24, 60), ("阴", 19, 26, 30)])
CHONGQING = city("重庆", ["Chongqing"], "重庆", "多云 28°C 体感 31°C 湿度 70% 风速 5 km/h",
                 [("多云", 24, 31, 20), ("阴", 23, 29, 40), ("小雨", 22, 27, 70)])
XIAN = city("西安", ["Xi'an", "Xian"], "陕西", "晴 22°C 体感 21°C 湿度 45% 风速 9 km/h",
            [("晴", 15, 26, 0), ("多云", 14, 24, 10), ("小雨", 13, 20, 60)])
HEFEI = city("合肥", ["Hefei"], "安徽", "多云 25°C 体感 26°C 湿度 66% 风速 7 km/h",
             [("多云", 20, 28, 20), ("晴", 19, 29, 5), ("多云", 20, 28, 15)])

README = {"README.md": "# notes\n"}


def case(cid, axis, task, prompt_or_turns, *, fixture, expect=None, case_expect=None,
         files=None, level="L0", notes=""):
    turns = prompt_or_turns if isinstance(prompt_or_turns, list) else [
        {"prompt": prompt_or_turns, "expect": expect or {}}]
    body = {
        "id": cid,
        "description": f"weather probe / {axis} / {task}. {CANARY}",
        "category": "weatherprobe",
        "tags": {"scenario": "weatherprobe", "task_type": task, "probe_axis": axis, "traps": [],
                 "level": level, "status": "draft", "version": 1, "author": "llm:claude-opus-5-5"},
        "files": files or README,
        "turns": turns,
        "weather_fixture": fixture,
    }
    if case_expect:
        body["expect"] = case_expect
    return body, notes


def weather_tools(**more):
    return {"required_tools": ["get_weather"], "forbidden_tools": NO_WEB, **more}


CASES = [
    case("wth-0001", "explicit", "today_high", "北京今天最高气温多少度？只回答数字。",
         fixture=[BEIJING, SHANGHAI], expect=weather_tools(expected_number=28, tolerance=0),
         notes="09-16 北京 18~28 → 28."),
    case("wth-0002", "explicit", "tomorrow_rain", "上海明天会下雨吗？",
         fixture=[SHANGHAI], expect=weather_tools(output_contains_any=["大雨", "90"]),
         notes="明天 = 09-17 大雨 90%; today is only 阴 30%, so citing today fails."),
    case("wth-0003", "explicit", "day_after_high", "广州后天最高温度是多少？只回答数字。",
         fixture=[GUANGZHOU], expect=weather_tools(expected_number=34, tolerance=0), level="L1",
         notes="后天 = 09-18 27~34 → 34. The 10-09 probe answered 后天 with 明天 (32)."),
    case("wth-0004", "explicit", "english_tomorrow", "What will the weather be like in Shenzhen tomorrow?",
         fixture=[SHENZHEN], expect=weather_tools(output_contains_any=["雷阵雨", "thunder", "Thunder"]),
         notes="Tomorrow = 09-17 雷阵雨 25~30. The English location must still hit the fixture (alias Shenzhen)."),
    case("wth-0005", "implicit", "umbrella", "我明天要在杭州跑一整天外勤，需要带伞吗？",
         fixture=[HANGZHOU], expect=weather_tools(output_contains_any=["中雨", "80"]),
         notes="Implicit need: 10-09 the model answered from priors without calling. 明天 中雨 80%."),
    case("wth-0006", "implicit", "clothing", "后天去哈尔滨出差，该穿什么？",
         fixture=[HARBIN], expect=weather_tools(output_contains_any=["小雪", "-1", "4°", "4℃", "4 °"]),
         level="L1", notes="后天 = 09-18 小雪 -1~4; 明天 (2~10) does not mention snow."),
    case("wth-0007", "explicit", "compare_two", "北京和上海今天哪个城市更热？",
         fixture=[BEIJING, SHANGHAI], expect=weather_tools(output_contains=["上海", "33"]), level="L1",
         notes="Two get_weather calls, one per city (one call per step). 上海 26~33 vs 北京 18~28."),
    case("wth-0008", "artifact", "markdown_brief", "查一下明天成都的天气，写成一份 Markdown 简报保存到 weather.md，写完回复 DONE。",
         fixture=[CHENGDU], expect=weather_tools(output_contains=["DONE"]), level="L1",
         case_expect={"files": {"weather.md": {"contains": ["小雨", "19", "24"]}}},
         notes="Artifact after weather: 10-09 the model switched to web_search for write-a-page tasks. 明天 小雨 19~24."),
    case("wth-0009", "artifact", "html_page", "做一个简单的 HTML 页面 weather.html，展示重庆今天的天气。做完回复 DONE。",
         fixture=[CHONGQING], expect=weather_tools(output_contains=["DONE"]), level="L1",
         case_expect={"files": {"weather.html": {"contains": ["多云", "31"]}}},
         notes="The exact 10-09 failure shape (写网页 → web_search 12/12). 今天 多云 24~31."),
    case("wth-0010", "artifact", "three_day_table",
         "把西安未来三天的天气整理成一个 Markdown 表格（日期、天气、气温），写进 notes/xian.md，写完回复 DONE。",
         fixture=[XIAN], expect=weather_tools(output_contains=["DONE"]), level="L2",
         case_expect={"files": {"notes/xian.md": {"contains": ["2026-09-18", "小雨", "13", "20", "多云"]}}},
         notes="All three days must land in the table; 09-18 小雨 13~20 is the last row."),
    case("wth-0011", "multiturn", "second_city", [
        {"prompt": "合肥今天天气怎么样？", "expect": weather_tools(output_contains_any=["多云", "28"])},
        {"prompt": "那重庆呢？明天适合出门逛吗？", "expect": weather_tools(output_contains_any=["阴", "40", "29"])},
    ], fixture=[HEFEI, CHONGQING], level="L1",
         notes="10-09: with a weather turn in history, the next city went to web_search 12/12. "
               "Turn 2 must call get_weather again for 重庆 (明天 阴 23~29, 40%)."),
    case("wth-0012", "unknown", "city_missing", "拉萨今天天气怎么样？",
         fixture=[BEIJING], level="L1",
         expect={"required_tools": ["get_weather"], "forbidden_tools": [],
                 "output_contains_any": ["没有", "未能", "无法", "查不到", "找不到", "not found", "失败"],
                 "output_excludes": ["°C"]},
         notes="The fixture has no 拉萨, so get_weather errors; the answer must say so instead of inventing a "
               "temperature. web_search is allowed (an honest fallback)."),
    case("wth-0013", "negative", "concept_question", "用一两句话解释一下什么是梅雨季。",
         fixture=[HANGZHOU], expect={"forbidden_tools": ["get_weather"], "output_contains": ["梅雨"]},
         notes="Weather-flavoured knowledge question: no forecast is needed, so get_weather must not be called."),
    case("wth-0014", "negative", "config_lookup", "config/app.yaml 里 weather_api_timeout 设的是多少秒？只回答数字。",
         fixture=[BEIJING], files={"config/app.yaml": "service: dashboard\nweather_api_timeout: 15\ncache_ttl: 600\n"},
         expect={"forbidden_tools": ["get_weather"], "expected_number": 15, "tolerance": 0},
         notes="The word weather is a decoy: the answer is in the workspace file (15)."),
]


def main():
    out = HERE / "cases"
    shutil.rmtree(out, ignore_errors=True)
    for body, notes in CASES:
        target = out / body["id"]
        target.mkdir(parents=True)
        (target / "case.json").write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (target / "NOTES.md").write_text(f"# {body['id']}\n\n{notes}\n", encoding="utf-8")
    print(f"wrote {len(CASES)} cases to {out}")


if __name__ == "__main__":
    main()
