"""M7 (v1.4 §3.7) pilot, part A: official page vs second-hand page that disagree."""
from common import write_case

def page(q, url_match, url, title, snippet, content, date, error=None):
    d = {"query_match": q, "url_match": url_match, "url": url, "title": title, "snippet": snippet, "published_at": date}
    if error:
        d["error"] = error
    else:
        d["content"] = content
    return d

def phr(items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, x) for i, x in enumerate(items))

# ---------------------------------------------------------------- web-8003
web = [
    page("quarrel", "kafkanotes.cn/quarrel-retention", "https://kafkanotes.cn/quarrel-retention",
         "Quarrel 消息保留调优笔记", "Quarrel 默认保留 48 小时，生产上建议调大。",
         "# Quarrel 消息保留调优笔记\n\n2025 年 11 月。Quarrel 默认把消息保留 48 小时，生产环境建议调到 7 天。\n", "2025-11-20"),
    page("quarrel", "quarrelmq.io/docs/4.x/retention", "https://quarrelmq.io/docs/4.x/retention",
         "Retention | Quarrel 4.x Documentation", "Message retention settings in Quarrel 4.x.",
         "# Retention (Quarrel 4.x)\n\nLast updated 2026-07-14.\n\n`retention.hours` defaults to 72. Changed in 4.0: the default was raised from 48 to 72 hours.\n", "2026-07-14"),
]
write_case(
    "web-8003",
    desc="Default message retention of a queue's 4.x line: a 2025 blog repeats the pre-4.0 default while the official 4.x docs give the current one",
    task_type="lookup_value", family="fam-web-b10-queueretention-01", level="L1", ref_calls=2,
    traps=["TR-WEBSTALE"], decoys={"TR-WEBSTALE": "48"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Quarrel 消息队列 4.x 版本默认把消息保留多少小时？",
            "expect": {"output_contains": ["72"], "output_contains_token": True, "output_excludes": ["48 小时", "48小时", "48 hours"],
                       "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
doc = [w for w in case["web_fixture"] if w["url"].startswith("https://quarrelmq.io/")][0]["content"]
print(json.dumps({"expected_number": int(re.search(r"defaults to (\\d+)", doc).group(1))}))
''',
    notes='''
## Traps
- TR-WEBSTALE: 搜索结果第一条是 2025 年 11 月的博客，说默认 48 小时；官方 4.x 文档（2026-07-14 更新）写明 4.0 起默认值从 48 提到 72 小时。

## Reference solution
1. 搜索 Quarrel 4.x 消息保留：两条结果，博客和官方文档。
2. 抓取官方文档 https://quarrelmq.io/docs/4.x/retention：retention.hours 默认 72。
终答 1–2 句：4.x 默认保留 72 小时，依据是官方 4.x 文档；网上一些旧文章写的是 4.0 之前的默认值，已经不适用。判据：包含 72（独立词元），不出现「48 小时」，抓取过页面。

## Why the answer is unique
题面限定 4.x，官方文档明确 4.0 起改为 72；博客早于此且不是官方来源。
''' + phr(["Quarrel 4.x 消息保留时长 默认", "quarrel retention hours default", "Quarrel 消息队列 默认保留", "quarrel 4.x retention.hours", "Quarrel MQ 消息保留多久"]),
)

# ---------------------------------------------------------------- web-8004
web = [
    page("larkspur", "stackanswers.dev/q/larkspur-timeout", "https://stackanswers.dev/q/larkspur-timeout",
         "What is Larkspur's default timeout?", "Accepted answer: the default request timeout is 60 seconds.",
         "# What is Larkspur's default timeout?\n\nAsked 2025-04-02. Accepted answer: Larkspur waits 60 seconds by default before raising TimeoutError.\n", "2025-04-02"),
    page("larkspur", "larkspur.dev/changelog", "https://larkspur.dev/changelog",
         "Larkspur changelog", "Release notes for the Larkspur HTTP client.",
         "# Larkspur changelog\n\n## 3.2.0 (2026-06-30)\n- Default request timeout lowered from 60 s to 30 s.\n- New `retry_on` option.\n\n## 3.1.4 (2026-03-11)\n- Fix proxy auth header.\n", "2026-06-30"),
]
write_case(
    "web-8004",
    desc="Default request timeout of an HTTP client 3.2: an older Q&A answer gives the old value while the official changelog records the 3.2 change",
    task_type="lookup_value", family="fam-web-b10-clienttimeout-01", level="L1", ref_calls=2,
    traps=["TR-WEBSTALE"], decoys={"TR-WEBSTALE": "60"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "What is the default request timeout in the Larkspur HTTP client 3.2?",
            "expect": {"output_contains": ["30"], "output_contains_token": True, "output_excludes": ["60 seconds", "60s", "60 s "],
                       "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
log = [w for w in case["web_fixture"] if w["url"] == "https://larkspur.dev/changelog"][0]["content"]
print(json.dumps({"expected_number": int(re.search(r"lowered from \\d+ s to (\\d+) s", log).group(1))}))
''',
    notes='''
## Traps
- TR-WEBSTALE: the first hit is a 2025 Q&A answer saying 60 seconds; the official changelog's 3.2.0 entry (2026-06-30) lowered the default to 30 s.

## Reference solution
1. Search Larkspur default timeout: a Q&A page and the official changelog.
2. Fetch https://larkspur.dev/changelog: 3.2.0 lowered the default from 60 s to 30 s.
Final answer, 1-2 sentences: 30 seconds in 3.2, per the official changelog (3.2.0 lowered it); older answers online describe pre-3.2 behaviour. Criteria: contains 30 as a token, no "60 seconds", a fetch happened.

## Why the answer is unique
The question names 3.2; the official changelog states the 3.2 default directly.
''' + phr(["Larkspur default timeout", "larkspur http client 3.2 timeout", "Larkspur request timeout default value", "larkspur changelog timeout", "Larkspur 3.2 release notes"]),
)

# ---------------------------------------------------------------- web-8005
web = [
    page("meridian", "dbwiki.cn/meridian", "https://dbwiki.cn/meridian",
         "Meridian 数据库 - 数据库百科", "Meridian 最新版本 7.3.2，发布于 2026-06-10。",
         "# Meridian 数据库\n\n社区维护词条。最新版本：7.3.2（2026-06-10）。\n", "2026-06-12"),
    page("meridian", "meridiandb.org/releases", "https://meridiandb.org/releases",
         "Meridian releases", "Official release notes for MeridianDB.",
         "# MeridianDB releases\n\n| Version | Date | Notes |\n|---|---|---|\n| 7.4.0 | 2026-08-27 | GA. Parallel vacuum, new planner hints. |\n| 7.3.2 | 2026-06-10 | Bug fixes. |\n| 7.3.1 | 2026-05-02 | Bug fixes. |\n", "2026-08-27"),
]
write_case(
    "web-8005",
    desc="Release date of a database's newest GA version: a community wiki is out of date, the official releases page lists a newer GA",
    task_type="latest_version", family="fam-web-b10-dbrelease-01", level="L1", ref_calls=2,
    traps=["TR-WEBSTALE"], decoys={"TR-WEBSTALE": "2026-06-10"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Meridian 数据库最新的正式版是哪天发布的？",
            "expect": {"output_contains": ["7.4.0"], "output_contains_any": ["2026-08-27", "8 月 27 日", "8月27日"],
                       "output_excludes": ["2026-06-10 发布", "6 月 10 日发布"], "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if w["url"] == "https://meridiandb.org/releases"][0]["content"]
ver = re.search(r"\\| (\\d+\\.\\d+\\.\\d+) \\| \\d{4}-\\d\\d-\\d\\d \\| GA", rel).group(1)
print(json.dumps({"expected_string": ver}))
''',
    notes='''
## Traps
- TR-WEBSTALE: 社区词条（2026-06-12）写最新版本 7.3.2、2026-06-10；官方发布页显示 7.4.0 在 2026-08-27 GA。

## Reference solution
1. 搜索 Meridian 最新正式版：社区词条与官方发布页。
2. 抓取 https://meridiandb.org/releases：最新 GA 是 7.4.0，2026-08-27。
终答 1–2 句：最新正式版是 7.4.0，2026 年 8 月 27 日发布（官方发布页）；社区词条还停在 7.3.2。判据：包含 7.4.0 与 8 月 27 日的任一写法，抓取过页面。

## Why the answer is unique
官方发布页是版本信息的一手来源，7.4.0 标明 GA 且日期最新；词条早于该发布。
''' + phr(["Meridian 数据库 最新版本", "meridiandb releases", "Meridian 最新正式版 发布日期", "meridian database latest GA", "Meridian 数据库 7.4"]),
)

# ---------------------------------------------------------------- web-8006
web = [
    page("ostrander", "paymentsweekly.io/ostrander-v1-batch", "https://paymentsweekly.io/ostrander-v1-batch",
         "Ostrander deprecates v1 batch endpoint", "Ostrander says /v1/batch will be removed around mid-2027.",
         "# Ostrander deprecates v1 batch endpoint\n\nMarch 2026. Ostrander told partners the /v1/batch endpoint is deprecated and will likely be removed around mid-2027.\n", "2026-03-18"),
    page("ostrander", "docs.ostrander.com/deprecations", "https://docs.ostrander.com/deprecations",
         "Deprecations and sunsets | Ostrander API", "Current deprecation schedule for the Ostrander Payments API.",
         "# Deprecations and sunsets\n\nUpdated 2026-08-04.\n\n| Endpoint | Status | Sunset |\n|---|---|---|\n| /v1/batch | deprecated; use /v2/batch-jobs | 2026-12-01 (requests return 410 after this date) |\n| /v1/refunds/legacy | removed | 2026-05-01 |\n", "2026-08-04"),
]
write_case(
    "web-8006",
    desc="When an API endpoint is switched off: a trade article from March gives a vague later date, the official deprecation page has the updated sunset date",
    task_type="deprecation", family="fam-web-b10-endpointsunset-01", level="L1", ref_calls=2,
    traps=["TR-WEBSTALE"], decoys={"TR-WEBSTALE": "mid-2027"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Is the /v1/batch endpoint of the Ostrander Payments API still supported? If it's going away, when exactly does it stop working?",
            "expect": {"output_contains_any": ["2026-12-01", "December 1, 2026", "1 December 2026", "Dec 1, 2026"],
                       "output_excludes": ["mid-2027"], "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
dep = [w for w in case["web_fixture"] if w["url"] == "https://docs.ostrander.com/deprecations"][0]["content"]
assert re.search(r"\\| /v1/batch \\| deprecated.*\\| 2026-12-01", dep)
print(json.dumps({"expected_contains_any": ["2026-12-01", "December 1, 2026", "1 December 2026", "Dec 1, 2026"]}))
''',
    notes='''
## Traps
- TR-WEBSTALE: a March 2026 trade article says removal "around mid-2027"; the official deprecations page (updated 2026-08-04) sets the /v1/batch sunset to 2026-12-01, after which requests return 410.

## Reference solution
1. Search Ostrander /v1/batch deprecation: the article and the official deprecations page.
2. Fetch https://docs.ostrander.com/deprecations.
Final answer, 1-2 sentences: /v1/batch is deprecated and stops working on 2026-12-01 (requests return 410 after that), per Ostrander's deprecation page; migrate to /v2/batch-jobs. Criteria: contains the date in any listed form, no "mid-2027", a fetch happened.

## Why the answer is unique
The official schedule is newer than the article and states an exact sunset date.
''' + phr(["Ostrander /v1/batch deprecation", "ostrander payments api v1 batch sunset", "Ostrander API deprecations", "ostrander batch endpoint removed", "Ostrander v1 batch end of life"]),
)

# ---------------------------------------------------------------- web-8007
web = [
    page("halyard", "devforum.net/t/halyard-e4127", "https://devforum.net/t/halyard-e4127",
         "Halyard E4127 again??", "E4127 is just a network timeout, retry the command.",
         "# Halyard E4127 again??\n\nReply (2025-12-02): E4127 is just a network timeout talking to the registry, retry and it goes away.\n", "2025-12-02"),
    page("halyard", "halyard.sh/docs/errors", "https://halyard.sh/docs/errors",
         "Error reference | Halyard", "Every Halyard CLI error code and what it means.",
         "# Halyard error reference\n\nUpdated 2026-07-21.\n\n- E4126: registry unreachable (network). Retry or check proxy settings.\n- E4127: the lockfile was written by a newer Halyard version than the one running. Upgrade Halyard, or regenerate the lockfile with this version.\n- E4128: lockfile checksum invalid.\n", "2026-07-21"),
]
write_case(
    "web-8007",
    desc="Meaning of a CLI error code: a forum reply calls it a network timeout, the official error reference says it is a lockfile-version mismatch",
    task_type="error_meaning", family="fam-web-b10-clierror-01", level="L1", ref_calls=2, version=2,
    traps=["TR-WEBSTALE"], decoys={"TR-WEBSTALE": "network timeout"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Our CI keeps failing with Halyard error E4127. What does that error mean?",
            "expect": {"output_contains": ["newer"], "output_contains_any": ["lockfile", "lock file"], "output_excludes": ["is just a network timeout", "means a network timeout"],
                       "required_tools": ["web_fetch"], "max_output_chars": 600}}],
    verify='''
import json

case = json.load(open("case.json"))
ref = [w for w in case["web_fixture"] if w["url"] == "https://halyard.sh/docs/errors"][0]["content"]
line = [l for l in ref.splitlines() if l.startswith("- E4127:")][0]
assert "newer" in line
print(json.dumps({"expected_contains_any": ["lockfile", "lock file"]}))
''',
    notes='''
## Traps
- TR-WEBSTALE: the first hit is a 2025 forum reply calling E4127 a network timeout (that is E4126 in the official reference). The official error reference says E4127 means the lockfile was written by a newer Halyard version.

## Reference solution
1. Search Halyard E4127: forum thread and the official error reference.
2. Fetch https://halyard.sh/docs/errors.
Final answer, 1-2 sentences: E4127 means the lockfile was written by a newer Halyard than the one CI runs; upgrade Halyard in CI or regenerate the lockfile with the CI version (official error reference). Criteria: contains "newer" and lockfile; does not present it as a network timeout.

## Why the answer is unique
The official reference defines each code; the forum reply conflates E4127 with E4126.

## Changelog
- v2: max_output_chars raised to 600, the §4.2 limit; the pilot answer (490 chars) was correct and within the spec limit but over the stricter limit this case had set.
''' + phr(["Halyard error E4127", "halyard E4127 meaning", "Halyard CLI error codes", "halyard lockfile E4127", "what is halyard error E4127"]),
)
