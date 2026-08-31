# Harness 第三轮报告:真实计数、压缩修复、检索纪律(2026-08-31,进行中)

分支 `feat/harness-round3`(自 `feat/harness-round2` 切出)。`ea6440c` 已打 tag
`round1-round2-boundary`(第一轮/第二轮分界,第一轮分支未推送,该 tag 是唯一
分界标记)。模型/端点/贪心采样/`--api-stop-tokens none` 同前两轮;所有 A/B
两臂同窗交错运行(第二轮第九节的纪律)。

状态标记:✅ 完成 · 🚧 进行中 · ⬜ 未开始。本报告随各步增量更新。

---

## 一、真实 token 对照表(第一步,✅ 测量完成)

**结论先行:项目里所有已保存语料本身就是用真词表逐 token 构造的,标称档位
即真实档位;真正的错位发生在运行时阈值一侧——估算器让 4096 的压缩阈值实际
落在英文 ~3.0k 真实 token、让 8192 的 fetch 预算实际落在英文 ~6.1k 真实
token。第三轮起运行时全部改用真词表进程内计数(1b/1c),估算器退役。**

### 方法

- 词表 `third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt`
  (sha256 `e6dee3d4…552bca89`,submodule 已 init)。
- 计数实现:trie 贪心最长匹配(`test/probes/common/rwkv_tokenizer.py`,
  镜像 rwkv_lightning_cuda `rwkv_trie.hpp`)——与生成全部语料的实现相同,
  因此本普查是"对已构造对象的复核",不是换尺子重造。
- 交叉验证:与 pysidecar `count_tokens` 用的 converter 表驱动实现
  (`rwkv_mobile/converter/rwkv_src/rwkv_tokenizer.py`)对比 8 篇跨语系文本,
  0 分歧;Go 重实现(`internal/tokenizer`)对 93 篇 / 551,860 token 的语料
  fixture 逐文本计数一致(`go test ./internal/tokenizer/`)。
- 脚本:`test/round3/token-census/census.py`(372 行数据,
  `census.json` / `census.md`);Go fixture 由
  `emit_go_fixture.py` 生成到 `internal/tokenizer/testdata/`。
  **本步零 API 调用。**

### 标称档位 → 实际 token 数

| 语料 | n | 标称 | 实际(min..max) | 结论 |
| --- | --- | --- | --- | --- |
| P1 四类型 × 五档 × 10 实例 | 200 | 500/2k/5k/10k/20k | **全部精确等于标称** | P1 全部结论的横轴无需任何重标 |
| P5 英文页(埋点后) | 20 | 5k/10k | 5022..5028 / 10022..10028 | 埋点句 +22~28 token,无实质错位 |
| P5-ZH 中文页(埋点后) | 20 | 5k/10k | 5042..**5204** / 10039..**10179** | build_page 逐段拼接最多超冲 4%;结论横轴按实际数即 5.0–5.2k/10.0–10.2k |
| e2e 校准题(文件/页正文) | 98 | 题目 id 内的标称 | 见下 | id 标称 ≈ 实际 +0–6% |
| round-1 e2e 语料 | 6 | 5k/10k | 5021 / 10019 | 同上 |

关键题目的真实档位重标(圆桌悬崖问题):

| 题目 | id 标称 | 实际 token | 第二轮校准 | 重标后含义 |
| --- | --- | --- | --- | --- |
| c1-file-4k | 4k | 4239 | 11/11 通过 | 通过带顶点 = real 4239 |
| c1-file-4k5 | 4k5 | **4673** | 4/5 | 降解起点 = real 4673(不是 4500) |
| e2e-long-extract-5k | 5k | **5021** | 0/5 全灭 | 悬崖底 = real 5021 |

**"单文件提取悬崖在 4.5k–5k token 之间"重标为:在 real 4673–5021 之间
(通过 4239 → 降解 4673 → 全灭 5021)。** 悬崖宽度比原表述更窄(约 350
token),且 c1-file-4k5 的正文实际比标称大 174 token——原来按 id 标称画横轴
会把悬崖画宽 1.6 倍。P1 的 10k/20k 降解点、P5 的 5k 检索失败点均为逐 token
构造,无需重标。

### 估算器偏差实测(为什么必须换尺子)

| 语料类型 | est/real(中位) | 估算器方向 |
| --- | --- | --- |
| 英文散文(P1 prose / P5-EN) | **1.354–1.358** | 高估 +35% |
| 英文代码体 | 1.16–1.40(随档位) | 高估 |
| 英文重复体 | 1.32–1.35 | 高估 |
| **英文列表体** | **0.952–0.967** | **低估 −3~−5%** |
| **中文页(P5-ZH / 诊断题)** | **0.979–0.989** | **低估 −1~−2%** |
| 中文原始 wiki 池 | 1.001 | ≈精确 |

代码注释里"对散文高估约 30%、对 CJK 偏置更大"两句都被实测否定:散文高估
实际约 35%;**CJK 不是高估、是 ~2% 低估**(World 词表把常用汉字按 ~1.08
token/汉字编码,与 1.1/rune 的假设几乎抵消)。列表体的 −4% 低估意味着旧
fetch 预算对列表页放过 ~4% 超额——方向与"安全"相反,只是幅度小。

### 运行时阈值的真实落点(换尺前 → 换尺后)

| 阈值 | 换尺前(估算) | 换尺前实际落点(EN/ZH) | 换尺后(真实计数) |
| --- | --- | --- | --- |
| 压缩阈值 `FetchCompressionThresholdTokens = 4096` | est 4096 | EN real ~3020–3112 就触发;ZH real ~4178 | real 4096 恒定 |
| fetch 预算 `maxFetchedContentTokens = 8192` | est 8192 | EN real ~6040–6225 就切;ZH real ~8356 | real 8192 恒定 |

含义(如实记录,不做效果声称):

1. 英文页的压缩触发带从 real ~3.0k 上移到 4.1k:real 3.0k–4.1k 的英文页不再
   被压缩。第二轮诊断集(5k–6k real)仍全部在触发带内。
2. 英文 fetch 预算的实际放行量从 real ~6.1k 上移到 8.2k。real 6.2k 的
   c1-web 页此前会在预算处被切(est 8200 > 8192,贴边),现在整页放行——
   第二轮"5k–6k band 无 E1 切片混淆"的前提在换尺后依然成立且更干净。
3. 中文页(ZH est≈real)两阈值位置几乎不动(4178/8356)。

### 1b/1c 落地(代码)

- 新包 `internal/tokenizer`:`OpenWorld`/`OpenWorldCached` 加载真词表,
  `Count`/`Encode` trie 贪心最长匹配(镜像 `rwkv_trie.hpp`),词表 sha256
  随对象携带;单测含 551,860 token 的 Python 真值 fixture 与逐字节词表
  解析测试(含 `b'…'` 字节字面量 486 行)。
- `agent.Options.TokenCount func(string) int`(nil = 无本地词表):
  - **压缩钩子**(runner_compression.go):阈值判断改真实计数;**TokenCount
    为 nil 时压缩整体关闭**——绝不退回估算器决定是否压缩(估算器对 CJK
    低估 2%,会让真实超额的中文页读作未超额,而中文正是 extract 指令
    污染页面的重灾区;P5-ZH-1)。该行为已写进代码注释与本报告。
  - **fetch 预算**(tools/web.go):预算切片改真实计数;TokenCount 为 nil
    时回退估算器——预算是上下文安全线,早切是安全方向,且实测回退误差
    有界(CJK/列表 −2~−4%,英文 +16~40%)。两个常数从此不再共用一把尺子
    (1c 完成)。
- 接线:eval(`agenteval.Config.TokenCount` + manifest 记录
  `token_count_vocab_sha256`)、CLI(`resolveTokenCounter`:显式 --tokenizer
  → 模型旁词表 → 仓库内置副本;显式指定但损坏 = 硬错误)、App
  (`api/session.go` 从 `Config.TokenizerPath` 加载,失败则压缩关闭)。
- 单测:`runner_compression_test.go` 断言 nil 计数器不触发压缩、真实计数
  触发/不触发两分支;`internal/tokenizer` 语料 fixture 测试。
- pysidecar(评测侧)与 `/v1/tokens/count` 保持原职责,未接进运行时。

---

## 二、压缩路径修复(第二步)

🚧 待第二步实施后填写。

---

## 三、同窗补跑(第三步)

⬜ 待第三步。

---

## 四、检索纪律探针(第四步)

⬜ 待第四步。

---

## 五、其他(HIG / PREFERENCES 整理)

⬜ 待第五步。

---

## 六、遗留与建议

(随各步增量补充)

1. 【新】Go tokenizer 与 Python 三实现(trie/converter/pysidecar)在语料
   fixture 上等价,但 fixture 只覆盖语料族样本;若未来换词表文件,需重跑
   `emit_go_fixture.py` 再生成真值。
