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
