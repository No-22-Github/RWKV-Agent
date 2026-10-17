# b21l 出题报告（v2.1 第三波，题号 33301–33380，共 80 题）

主题：需要多个工具配合的组合任务。生成脚本 `bench/distill/tools/b21l/`，每题的 `compute(files, web)` 嵌入 verify.py，从 fixture 与 web_fixture 重算期望文件与答案。

## 构成
- 子类（各 16）：web_then_edit 33301–16、tool_then_write 33317–32、web_then_calc 33333–48、compound_request 33349–64、multi_turn 33365–80。
- 中文 43（53.8%）/ 英文 37；多轮 33（41.3%，其中 multi_turn 16 全为多轮；另 web_edit 4、calc 6、compound 7 题）。
- 难度：单轮 L1、多轮 L2 为主（由 trap 数与 ref_calls 推出），无 L0。
- tool_policy：全部写 must_offer（web 题含 web_search+web_fetch，写文件题含 write_file，计算题含 bash/calculator），无 never_offer。

## 判据设计
- 改文件题 `expect.files` 用 equals（单值替换）；报告类和追加类文件用 contains（题面规定了 `键=值` 格式）；无关文件 unchanged。
- 答案数字 ≥1000 或带小数的题用 `output_contains_any`（plain/千分位/两位小数）+ `output_contains_any_token`；1–3 位裸数字开 `output_contains_token`。
- 网页题带过期/备用页诱饵（旧博客、镜像页、回溯版本），靠 equals 与答案值区分；网页题加 `required_tools: web_fetch`（搜索摘要不含答案）。
- 多轮：第二轮问另一个文件/字段/另一个网页（33365–70、33341–46、33360）、用户补充新信息（33375–80），以及 4 题用 `review_before`：33371、33373 拒绝暂存改动后追问当前文件内容；33372 接受后读回；33374 拒绝后改做另一处修改。
- `output_excludes` 基本不用（诚实回答也会复述旧值）。

## 自检
- build.py 连跑两次，80 题目录内容哈希一致。
- `gate.sh v2.1 'hyb-333[0-8]?'`：lint 0 违规，verify 80/80。
- `corpus loadcheck`：1064 题全部加载。

## 已知风险
- 33310 代码改动用 equals（`fetchV3(u, {})` 空格写法需一致），33313/33363 追加行靠 contains。
- 33352 英文答案用同义词表，33361 要求照日志写法给时间，措辞仍可能漏收。
- query_match 依赖模型搜索词含产品名（已用 Latin 名或用户原词）；搜不到时只能靠题面里给的域名直接 fetch。
- 33371/33373/33374 假设 App 的读文件读磁盘/暂存叠加后的真实状态；若 harness 读取暂存内容，拒绝后的答案以磁盘为准的假设需复核。
- 数据为程序生成，主题词（订单、日志）有重复，去污染若撞题直接删。

## 老师最可能答错的题
1. 33374：拒绝后只改 mode，容易把 retries 的旧改动带回去。
2. 33345：体积重向上取整，三件货分别 5/13/4 公斤。
3. 33342：税页与价页分开，第二轮要含 12% 税与每晚度假费。
4. 33379：备用页标注过期，必须说以主站 10 月 20 日为准。
5. 33332：重复记录的 id 只算一次。
6. 33307：只删 3.9，不动 setup.cfg。
