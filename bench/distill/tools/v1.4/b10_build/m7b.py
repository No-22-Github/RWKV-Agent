"""M7 (v1.4 §3.7) pilot, part B: official page unreachable; preview vs stable."""
from common import write_case
from m7a_helpers import page, phr

UNVER_ZH = ["未核实", "没有核实", "无法核实", "没能核实", "未经官方", "没有经过官方", "未得到官方", "尚未经官方", "无法确认", "没能确认", "未能确认"]
UNVER_EN = ["unverified", "not verified", "couldn't verify", "could not verify", "unable to verify", "not been verified", "couldn't confirm", "could not confirm", "unable to confirm", "not confirmed"]

# ---------------------------------------------------------------- web-8008
web = [
    page("fennel", "fennel-lang.org/roadmap", "https://fennel-lang.org/roadmap", "Fennel 编译器路线图",
         "Fennel 2.0 发布计划与里程碑。", None, "2026-09-01", error="HTTP 503 Service Unavailable"),
    page("fennel", "techdaily.cn/news/fennel-2", "https://techdaily.cn/news/fennel-2", "Fennel 2.0 有望年底前发布",
         "据社区维护者透露，Fennel 2.0 正式版预计 2026 年 11 月发布。",
         "# Fennel 2.0 有望年底前发布\n\n科技日报 2026-09-05。据一位社区维护者在会议上透露，Fennel 2.0 正式版预计 2026 年 11 月发布，具体以官方公告为准。\n", "2026-09-05"),
]
write_case(
    "web-8008",
    desc="Planned release month of a compiler's 2.0: the official roadmap page fails to load, only a news article quoting a maintainer is available",
    task_type="latest_version", family="fam-web-b10-roadmapdown-01", level="L1", ref_calls=3,
    traps=["TR-FETCHFAIL"], decoys={"TR-FETCHFAIL": "UNKNOWN"}, axes=["ERR"], web=web, files={},
    turns=[{"prompt": "Fennel 编译器 2.0 正式版计划什么时候发布？",
            "expect": {"output_contains": ["11 月"], "output_contains_any": UNVER_ZH, "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if "fennel-lang.org" in w["url"]][0]
news = [w for w in case["web_fixture"] if "techdaily.cn" in w["url"]][0]["content"]
assert off.get("error") and "2026 年 11 月" in news
print(json.dumps({"expected_string": "11 月"}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-FETCHFAIL: 官方路线图 https://fennel-lang.org/roadmap 抓取返回 503。唯一能读到的是科技日报转述社区维护者的说法：预计 2026 年 11 月。

## Reference solution
1. 搜索 Fennel 2.0 发布时间：官方路线图和一篇新闻。
2. 抓取官方路线图：503。
3. 抓取新闻页：维护者透露预计 2026 年 11 月，「以官方公告为准」。
终答 2–3 句：官方路线图打不开，没能核实；目前只有科技日报转述的社区维护者说法，预计 2026 年 11 月发布正式版，这不是官方公告。可以稍后再看官方路线图确认。判据：包含「11 月」和一个「未核实/无法确认」说法。

## Why the answer is unique
唯一可得的信息来自二手报道；官方来源不可达，所以答案必须给出该说法并标明未经官方核实。
''' + phr(["Fennel 2.0 发布时间", "fennel 编译器 2.0 正式版", "Fennel 2.0 roadmap", "fennel compiler 2.0 release date", "Fennel 编译器 路线图"]),
)

# ---------------------------------------------------------------- web-8009
web = [
    page("sablewood", "docs.sablewood.io/uploads/limits", "https://docs.sablewood.io/uploads/limits", "Upload limits | Sablewood Docs",
         "Size and rate limits for the Sablewood upload API.", None, "2026-08-11", error="HTTP 404 Not Found"),
    page("sablewood", "wiki.devcommons.org/Sablewood_upload_API", "https://wiki.devcommons.org/Sablewood_upload_API", "Sablewood upload API - DevCommons wiki",
         "Community notes: uploads are capped at 250 MB per file.",
         "# Sablewood upload API\n\nCommunity-maintained page, last edited 2026-05-30. Uploads are capped at 250 MB per file; larger files need multipart sessions.\n", "2026-05-30"),
]
write_case(
    "web-8009",
    desc="Maximum upload size of an API: the official limits page returns 404, a community wiki gives a figure that has to be reported as unverified",
    task_type="lookup_value", family="fam-web-b10-uploadcap-01", level="L1", ref_calls=3, version=2,
    traps=["TR-FETCHFAIL"], decoys={"TR-FETCHFAIL": "UNKNOWN"}, axes=["ERR"], web=web, files={},
    turns=[{"prompt": "What's the maximum file size the Sablewood upload API accepts per file?",
            "expect": {"output_contains": ["250"], "output_contains_token": True, "output_contains_any": UNVER_EN, "required_tools": ["web_fetch"], "max_output_chars": 600}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if "docs.sablewood.io" in w["url"]][0]
wiki = [w for w in case["web_fixture"] if "devcommons" in w["url"]][0]["content"]
assert off.get("error")
print(json.dumps({"expected_number": int(re.search(r"capped at (\\d+) MB", wiki).group(1))}))
''',
    notes='''
## Traps
- TR-FETCHFAIL: the official limits page returns 404. The only figure comes from a community wiki (last edited 2026-05-30): 250 MB per file.

## Reference solution
1. Search Sablewood upload size limit: the official docs page and the community wiki.
2. Fetch the official page: 404.
3. Fetch the wiki: 250 MB per file, multipart for larger.
Final answer, 2-3 sentences: Sablewood's own limits page returned 404, so I couldn't verify it with them; a community wiki says uploads are capped at 250 MB per file (larger files need multipart). Treat that as unconfirmed until it is checked with Sablewood. Criteria: contains 250 as a token and an unverified/couldn't-confirm phrase.

## Why the answer is unique
The wiki figure is the only one available; the official source is unreachable, so the answer has to carry the caveat.

## Changelog
- v2: max_output_chars raised to 600, the §4.2 limit; the pilot answer (448 chars) was correct and within the spec limit but over the stricter limit this case had set.
''' + phr(["Sablewood upload API max file size", "sablewood upload limits", "Sablewood API file size limit", "sablewood upload 250 MB", "Sablewood upload API limits per file"]),
)

# ---------------------------------------------------------------- web-8010
web = [
    page("tessera", "gatewayweekly.cn/tessera-6", "https://gatewayweekly.cn/tessera-6", "Tessera 6.0 来了！",
         "Tessera 数据网关 6.0 带来全新插件体系。",
         "# Tessera 6.0 来了！\n\n2026-09-11。Tessera 6.0.0-rc.2 已经可以试用，全新插件体系……\n", "2026-09-11"),
    page("tessera", "tessera.io/releases", "https://tessera.io/releases", "Tessera 发布记录", "Tessera 数据网关各通道版本。",
         "# Tessera releases\n\n| 版本 | 通道 | 日期 |\n|---|---|---|\n| 6.0.0-rc.2 | preview（不提供商业支持） | 2026-09-10 |\n| 5.8.3 | stable | 2026-09-01 |\n| 5.8.2 | stable | 2026-07-22 |\n", "2026-09-10"),
]
write_case(
    "web-8010",
    desc="Which version customers can install today: the official releases page lists a 6.0 release candidate on the preview channel above the latest stable",
    task_type="latest_version", family="fam-web-b10-stablechannel-01", level="L1", ref_calls=2,
    traps=["TR-SUPERSEDE"], decoys={"TR-SUPERSEDE": "6.0.0-rc.2"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "客户现在能正式装上用的 Tessera 数据网关最新版本是哪个？",
            "expect": {"output_contains": ["5.8.3"], "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if w["url"] == "https://tessera.io/releases"][0]["content"]
print(json.dumps({"expected_string": re.search(r"\\| (\\d+\\.\\d+\\.\\d+) \\| stable", rel).group(1)}))
''',
    notes='''
## Traps
- TR-SUPERSEDE: 官方发布页最上面是 6.0.0-rc.2（preview 通道、不提供商业支持），新闻也在宣传 6.0；客户能正式使用的是 stable 通道最新的 5.8.3。

## Reference solution
1. 搜索 Tessera 最新版本：新闻和官方发布页。
2. 抓取 https://tessera.io/releases：stable 最新为 5.8.3（2026-09-01）。
终答 1–2 句：客户能正式使用的最新版本是 5.8.3（stable，2026-09-01）；6.0.0-rc.2 只是预览版、不提供商业支持。判据：包含 5.8.3，抓取过页面。

## Why the answer is unique
「客户能正式装上用的」限定 stable 通道，官方发布页上 stable 最新只有 5.8.3。
''' + phr(["Tessera 数据网关 最新版本", "tessera releases", "Tessera 6.0", "tessera gateway stable version", "Tessera 数据网关 发布记录"]),
)

# ---------------------------------------------------------------- web-8011
web = [
    page("kestrel", "github.com/kestrel-labs/sdk/releases", "https://github.com/kestrel-labs/sdk/releases", "Releases - kestrel-labs/sdk",
         "Kestrel SDK release history.",
         "# kestrel-labs/sdk releases\n\n## v2.15.0-beta.1 (pre-release) 2026-09-09\nNew streaming client. Not recommended for production.\n\n## v2.14.0 (latest) 2026-08-19\nStable. Retries honour Retry-After.\n\n## v2.13.2 2026-07-02\nBug fixes.\n", "2026-09-09"),
    page("kestrel", "medium.example-dev.net/kestrel-2-15", "https://medium.example-dev.net/kestrel-2-15", "Why we upgraded to Kestrel SDK 2.15",
         "Kestrel SDK 2.15 is out and it's great.",
         "# Why we upgraded to Kestrel SDK 2.15\n\nThe 2.15 beta's streaming client cut our latency in half. Upgrade today!\n", "2026-09-12"),
]
write_case(
    "web-8011",
    desc="Which SDK version to pin for production: the official releases list a 2.15 beta pre-release above the latest stable 2.14.0, and a blog post promotes the beta",
    task_type="latest_version", family="fam-web-b10-sdkpin-01", level="L1", ref_calls=2,
    traps=["TR-SUPERSEDE"], decoys={"TR-SUPERSEDE": "2.15.0-beta.1"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Which Kestrel SDK version should we pin for our production services?",
            "expect": {"output_contains": ["2.14.0"], "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if "github.com/kestrel-labs" in w["url"]][0]["content"]
print(json.dumps({"expected_string": re.search(r"## v(\\d+\\.\\d+\\.\\d+) \\(latest\\)", rel).group(1)}))
''',
    notes='''
## Traps
- TR-SUPERSEDE: v2.15.0-beta.1 sits at the top of the official releases and a blog post urges upgrading, but it is a pre-release marked not recommended for production; the latest stable is v2.14.0.

## Reference solution
1. Search Kestrel SDK releases: the official GitHub releases and a blog post.
2. Fetch https://github.com/kestrel-labs/sdk/releases.
Final answer, 1-2 sentences: pin 2.14.0, the latest stable release (2026-08-19); 2.15.0-beta.1 is a pre-release the maintainers do not recommend for production. Criteria: contains 2.14.0; a fetch happened.

## Why the answer is unique
Production pins need a stable release; v2.14.0 is the newest one marked latest/stable on the official page.
''' + phr(["Kestrel SDK releases", "kestrel sdk latest stable version", "Kestrel SDK 2.15", "kestrel sdk production version", "kestrel-labs sdk release notes"]),
)

# ---------------------------------------------------------------- web-8012
web = [
    page("orchid", "fe-weekly.cn/orchid-9-1", "https://fe-weekly.cn/orchid-9-1", "Orchid 9.1.4 升级指南",
         "Orchid 最新稳定版 9.1.4 升级要点。",
         "# Orchid 9.1.4 升级指南\n\n2026-06-03。Orchid 最新稳定版 9.1.4……\n", "2026-06-03"),
    page("orchid", "orchidjs.dev/versions", "https://orchidjs.dev/versions", "Orchid 版本与发布通道", "Orchid 前端框架各发布通道的当前版本。",
         "# Orchid 版本与发布通道\n\n更新于 2026-09-08。\n\n| 通道 | 当前版本 | 说明 |\n|---|---|---|\n| latest（正式） | 9.2.0 | 2026-08-20 发布，推荐生产使用 |\n| next（预发布） | 9.3.0-next.4 | 每周更新，API 可能变动 |\n| lts | 8.6.7 | 维护到 2027-03 |\n", "2026-09-08"),
]
write_case(
    "web-8012",
    desc="Current version on a frontend framework's official channel: a June article is stale, and the official channel page also lists a next pre-release and an LTS line",
    task_type="latest_version", family="fam-web-b10-fechannel-01", level="L2", ref_calls=2,
    traps=["TR-SUPERSEDE", "TR-WEBSTALE"], decoys={"TR-SUPERSEDE": "9.3.0-next.4", "TR-WEBSTALE": "9.1.4"}, axes=["VER"], web=web, files={},
    turns=[{"prompt": "Orchid 前端框架的正式通道现在是哪个版本？",
            "expect": {"output_contains": ["9.2.0"], "output_excludes": ["9.1.4 是"], "required_tools": ["web_fetch"], "max_output_chars": 400}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
page = [w for w in case["web_fixture"] if w["url"] == "https://orchidjs.dev/versions"][0]["content"]
print(json.dumps({"expected_string": re.search(r"\\| latest（正式） \\| (\\S+) \\|", page).group(1)}))
''',
    notes='''
## Traps
- TR-WEBSTALE: 第一条结果是 2026-06 的文章，说最新稳定版 9.1.4。
- TR-SUPERSEDE: 官方通道页上 next 通道是 9.3.0-next.4（预发布），lts 是 8.6.7；正式通道（latest）是 9.2.0。

## Reference solution
1. 搜索 Orchid 正式版本：旧文章与官方通道页。
2. 抓取 https://orchidjs.dev/versions：latest（正式）9.2.0，2026-08-20 发布。
终答 1–2 句：正式通道当前是 9.2.0（官方版本页，8 月 20 日发布）；9.3.0-next.4 是预发布通道，旧文章里的 9.1.4 已经过时。判据：包含 9.2.0，抓取过页面。

## Why the answer is unique
题问「正式通道」，官方页上 latest（正式）只有 9.2.0。
''' + phr(["Orchid 前端框架 正式版本", "orchidjs versions", "Orchid latest 通道 版本", "orchid frontend framework release channel", "Orchid 9.2"]),
)
