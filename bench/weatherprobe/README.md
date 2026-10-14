# weatherprobe：get_weather 能力探针

14 道题，测模型在 `work-v2` 工具目录下会不会用 `get_weather`、用得对不对。题目由 [`gen.py`](gen.py) 生成，答案全部来自每道题自带的 `weather_fixture`，固定时钟是 2026-09-16（周三），所以"明天"是 09-17，"后天"是 09-18。
**改题只改生成器，不手改 `cases/`。**

```bash
python3 bench/weatherprobe/gen.py
./local/bin/rwkv-cli agent-eval ... --profile g1k --strict-spec \
  --cases bench/weatherprobe/cases --tool-catalog work-v2 --file-tools lines --include-draft \
  --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m --remote-batch-wait 0s
```

## 题目轴（`tags.probe_axis`）

| 轴 | 题 | 想看什么 |
|---|---|---|
| explicit | 0001–0004、0007 | 直接问今天、明天、后天、英文城市名、两城对比；"后天"在 10-09 的实测中被答成了"明天" |
| implicit | 0005–0006 | "要带伞吗""穿什么"：10-09 实测时模型不调工具，凭常识回答 |
| artifact | 0008–0010 | 查完天气后写 Markdown、HTML 或三天表格；10-09 实测时，写网页一类的请求 12 次全都去搜网页 |
| multiturn | 0011 | 上一轮已经查过一个城市，这一轮换一个城市，仍要调用 get_weather |
| unknown | 0012 | fixture 里没有的城市：要如实说查不到，不能编造温度 |
| negative | 0013–0014 | 天气概念题、文件里带 weather 字样的配置题：不该调用 get_weather |

天气正例都禁止调用 `web_search`/`web_fetch`。所有题 `status: draft`，跑时带 `--include-draft`。
与 v1.4/v1.41 出题集按 8 字符片段算重叠：wth-0004 0.57、wth-0012 0.33，都只是通用句式（"what will the weather be like … tomorrow""今天天气怎么样"），城市和题意不同。

**这是评测集，不得作为出题种子或训练数据。**

## 第二部分：cases-b14（wth-0101–0130，30 题）

2026-10-14 从 b14 固定选出（名单 [`probe_ids.json`](../distill/tools/b14/probe_ids.json)，不再重抽），放在 `cases-b14/`，**旧的 14 题（`cases/`）原样冻结**，两部分分开跑、分开报。生成器同 bashprobe 第二部分（`bench/distill/tools/b14`，`m10w.py` + `export_probe.py`）。fixture 时钟同样是 2026-09-16。

| 轴 | 题 | 想看什么 |
|---|---|---|
| explicit | 0101–0105 | 明天/后天/周六/下周一对到正确的行；2 题地标（故宫、洪崖洞）归到城市 |
| implicit | 0106–0109 | 带伞、户外、穿衣、马拉松；含按本地规则文件判断，1 题两轮换日期 |
| artifact | 0110–0116 | 按文件已有格式写一行（Markdown 列表、日志、CSV、JSONL、HTML li 等），整文件相等判分：不能漏换行、不能重复写 |
| multiturn | 0117–0119 | 两轮，第二轮换城市，必须重新查 |
| unknown | 0120–0122 | 查不到的地点：单问、两地对比、两轮各 1 题；不编数字、不拿邻近城市冒充 |
| compound | 0123–0125 | 天气 + 一次网页查询（景点闭馆、活动日期） |
| negative | 0126–0130 | 概念题零调用；2 题第二轮问到具体城市，必须调用 |

中文 23、多轮 11、首轮零调用 5。参考：DeepSeek-flash（T=0.3，k=3，带 b12 老师附加指令）80/90，三次全过 25 题（不带附加指令单跑一次 20/30，多出的失败是长 Markdown 超字数上限）；两地对比题（wth-0121）DeepSeek 会换拼写连查两次失败、触发连续失败锁，连已知城市也查不了，3 次全挂。

## 备选区：reserve/（70 题）

b14 其余天气题，保留原题号，不参与跑分，用于轮换或补充；**同样是测试数据，不得进训练集或当出题种子**。
