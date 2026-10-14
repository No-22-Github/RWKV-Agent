# b20d 日常问答批：出题报告

批次 b20d，题号 nt-21001 – nt-21200，共 200 题；生成脚本 `bench/distill/tools/b20d/build.py`（种子 20210，重跑逐字节一致）。

## 来源与署名

题面（instruction）取自 Hugging Face 数据集 `dengxiaodi/deepseek-v4.1-flash-distill-zh-2k`（CC BY 4.0，教师模型 DeepSeek-V4.1-Flash），每题 tags 带 source_dataset / source_id / source_category / license。原数据集的 thinking 与 response 一律不使用；回答由我们的环境里的老师重新生成。署名：dengxiaodi, "DeepSeek-V4.1-Flash-Distill-ZH-2K", CC BY 4.0, https://huggingface.co/datasets/dengxiaodi/deepseek-v4.1-flash-distill-zh-2k 。

## 选题规则（确定性，无手工挑选）

1. 排除 completion_tokens > 2048。
2. 排除时效题（正则 TIME_RE：最新/现在/目前/近期/当前/新闻/实时/最近/今年/本周/20xx 年等）。
3. 排除需要本地文件或个人数据的题（LOCAL_RE：我的/附件/上传/刚才/上面的/截图/链接/这个文件等）。
4. 排除题面含工具名的题（lint 规则 prompt.tool_name，例如“写一个 bash 命令”）。
5. 先从剩余题里抽 12 道精确计算类（数学应用题，或含数字且含 计算/等于/多少/求），每类不超过 4 道；再按 category 轮转补满到 200，每类封顶 8；顺序由种子 20210 的 shuffle 决定。
6. 互相去重：8 字符片段（去空白）集合的 Jaccard ≥ 0.4 视为近似重复，后到者跳过（共跳过 18 次）。
7. 选中后按源 id 升序编号为 nt-21001…。

## 被排除原因计数（源 2000 题，按判断顺序，每题只计第一个原因）

- completion_tokens>2048：1095
- time-sensitive：4
- mentions a tool name (lint prompt.tool_name)：1
- 合格候选：900；其中被选中 200

## 计算类题数

按 is_calc 规则（数学应用题，或含数字且含 计算/等于/多少/求）判定，选中里共 16 道（其中配额抽取 12 道，其余为轮转时碰巧命中）。题号：nt-21005 nt-21020 nt-21023 nt-21060 nt-21090 nt-21095 nt-21102 nt-21119 nt-21132 nt-21149 nt-21157 nt-21165 nt-21176 nt-21180 nt-21187 nt-21195。

## 去重自检

200 题两两比较：存在至少一个共同 8 字符片段的题对 1056 个；最大 Jaccard 0.395（阈值 0.4）。
同一模板句式（如“和我们的日常生活有什么关系”）的题允许出现，只要主题不同。

## 各 category 题数（family 编号 cNN 对应）

| family | category | 题数 |
|---|---|---|
| c01 | 世界历史 | 5 |
| c02 | 中国历史 | 4 |
| c03 | 人工智能 | 6 |
| c04 | 体育 | 5 |
| c05 | 其他语言 | 3 |
| c06 | 创意写作 | 6 |
| c07 | 化学 | 4 |
| c08 | 医学健康 | 5 |
| c09 | 哲学 | 4 |
| c10 | 地球科学 | 4 |
| c11 | 地理 | 4 |
| c12 | 天文 | 4 |
| c13 | 头脑风暴 | 4 |
| c14 | 宠物与植物 | 5 |
| c15 | 工程与制造 | 5 |
| c16 | 建筑 | 4 |
| c17 | 建议咨询 | 4 |
| c18 | 心理学 | 5 |
| c19 | 教育 | 5 |
| c20 | 数学应用题 | 8 |
| c21 | 数学概念 | 5 |
| c22 | 文本处理 | 5 |
| c23 | 汽车 | 5 |
| c24 | 法律 | 5 |
| c25 | 游戏 | 5 |
| c26 | 烹饪与食材 | 4 |
| c27 | 物理 | 5 |
| c28 | 生活技巧 | 4 |
| c29 | 生物 | 4 |
| c30 | 电影 | 4 |
| c31 | 经济学 | 4 |
| c32 | 编程 | 5 |
| c33 | 美术 | 5 |
| c34 | 翻译 | 5 |
| c35 | 能源与环境 | 5 |
| c36 | 英语学习 | 4 |
| c37 | 计算机基础 | 6 |
| c38 | 语文与文学 | 5 |
| c39 | 软件与互联网 | 5 |
| c40 | 逻辑与谜题 | 8 |
| c41 | 金融 | 4 |
| c42 | 音乐 | 4 |

## 题目形态

- 场景 notool，files {}，web_fixture []，单轮；turns[0].prompt = instruction 原文；expect 只有一条 output_excludes ["UNKNOWN"]（见下“与规格的两处偏差”），不写 tools、tool_policy、max_output_chars。
- task_type=concept，level=L0，ref_calls=0，traps 为空（TR-NOTOOLNEED 要求 trap_decoys 非 null，对无确定答案的题不适用，故不挂）。

## 与规格的两处偏差（均不改 Go 代码）

1. 加载器（caseio.go）要求每轮至少声明一种工具期望或结果期望，完全空的 expect 会让 `corpus loadcheck` 报错。最小处理：每轮写 `output_excludes: ["UNKNOWN"]`。它不约束工具，也不限长度，只排除裸 UNKNOWN 弃权（日常问答里本就不该出现）。
2. `gate.sh` 的 verify 用 --strict-shape，对没有任何答案期望的题会报 verify_shape_unknown。最小处理：verify.py 输出 `{"files": {}}`（空夹具快照，已知形状），并断言题面、标签、署名字段自洽。lint 的 TR-NOTOOLNEED 要求 trap_decoys 非 null，不适用于无确定答案的题，所以不挂 trap（traps 为空，level L0）。

- 全部中文题；answer_style=natural，不带英文答题契约。
