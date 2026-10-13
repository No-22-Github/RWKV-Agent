# b14 出题报告（v1.42，2026-10-13）

规划见 [distill-allocation-v1.42.md](../distill-allocation-v1.42.md)，脚本见 [tools/b14](../../tools/b14/README.md)。本轮只出题、验参考解、去重；**没有跑老师、没有训练、没有跑分**。

## 1. 题数与构成

`python3 bench/distill/tools/b14/stats.py`（明细在 [b14-stats.json](b14-stats.json)）：

| 子类 | 名称 | 题数 | 中文 | 多轮 | 首轮零调用 |
|---|---|---:|---:|---:|---:|
| M9a | 跨文件聚合 | 54 | 33 | 13 | 0 |
| M9c | 长文件 | 17 | 7 | 3 | 0 |
| M9g | 精确匹配 | 24 | 11 | 6 | 0 |
| M9b | 批量编辑 | 40 | 21 | 9 | 0 |
| M9d | 缺命令恢复 | 18 | 9 | 3 | 0 |
| M9f | cwd 不保留 | 7 | 4 | 7 | 0 |
| M9e | 该不该用 bash（负例） | 40 | 26 | 5 | 30 |
| M10a | 直接天气/地标 | 18 | 12 | 2 | 0 |
| M10d | 隐式需求/本地规则 | 14 | 9 | 2 | 0 |
| M10b | 天气写产物 | 22 | 16 | 8 | 0 |
| M10f | 多轮换城市 | 12 | 9 | 12 | 0 |
| M10g | 查不到的地点 | 9 | 7 | 2 | 0 |
| M10c | 复合请求 | 10 | 7 | 2 | 0 |
| M10e | 概念负例 | 15 | 11 | 5 | 15 |
| **合计** | | **300** | **182（60.7%）** | **79（26.3%）** | **45（15.0%）** |

- bash 200 题：中文 55.5%、多轮 23.0%、首轮零调用 15.0%；天气 100 题：中文 71.0%、多轮 33.0%、首轮零调用 15.0%。
- 按用户的分类口径：聚合 66（M9a 54 + 放在 m9agg 里的 12 道长单文件）、精确匹配 24、批量编辑 40、出错恢复 30（缺命令 18 + cwd 7 + 答案在长文件末尾 5）、负例 40；天气 100（明后天/地标 18、隐式 14、写产物 22、换城市 12、查不到 9、复合 10、概念负例 15）。
- 用户轮共 379 行。
- 数据量：87 道非目录树的聚合/精确匹配题 fixture 合计 70–181KB（构建时不足 70KB 的世界自动放大行数）；17 道 M9c 单文件 78–172KB；8 道扩展名计数题是 171–235 个文件的嵌套目录。缺命令复算题（M9d）数据 18–56KB，有意不放大：这类题考的是换方法，不是读不完。

## 2. 闸门

| 检查 | 结果 |
|---|---|
| `gate.sh v1.42` → `bank verify --strict-shape`（含破坏测试） | **300/300 通过** |
| `bank lint --canary-prefix DISTILL-CANARY` | 只剩 300 条 `dir_structure`：5 位题号不符合 lint 写死的 4 位规则（§6.1）。其余规则（tool_name、forbidden_word、level、trap_decoys、axes、answer_contract、notes 段落、web_fixture）全部通过 |
| 重跑一致性 | `build.py` 连续两次构建，300 题所有文件 sha256 一致 |
| `behavior.py` | 用三条手造轨迹冒烟：ask_then_run、weather_switch 判 covered；单问一个查不到地点的路径被判 reject（unclean，见 §6.2） |

## 3. 参考解验证

本会话用 `scripts/build-justbash.sh`（需要 bun，本环境已装）构建了 `local/bin/justbash-sidecar`，`build.py` 在 sidecar 里逐题回放参考解：

- **166 道有 bash 参考解的题全部跑通并对上答案**：聚合/精确匹配/长文件逐轮回放并核对该轮答案（含千分位两种写法）；批量编辑用 sidecar 的 `read` op 回读 overlay，逐文件比对 expect.files（equals / unchanged / absent）；缺命令题回放的是 awk/jq 复算（不是去跑 python）；cwd 题回放「cd + ls」和带完整路径的读取；先问后跑的 5 题回放第二轮命令；注入题回放计数命令。
- **134 道没有 bash 参考解**，因为它们本来就不该用 bash，或判据不靠命令输出：天气 100 题（答案由 verify.py 从 weather_fixture 计算；写产物题的期望文件由 verify 与 expect 同源生成，**没有在 sidecar 里执行写入**，是否写得对要看老师轨迹）、只问命令/已贴内容 25 题、单文件读取 5 题、curl→网页 4 题。
- 没有「构建不了、跳过验证」的 bash 题。

## 4. 去重与去污染

**8 字符片段重叠**（`tools/b14/dedup.py`，[b14-dedup.json](b14-dedup.json)）：题面所有轮 prompt 拼接、小写、去空白和标点后取 8 字符窗口，得分 = 新题片段在参考题中出现的比例（取最大）。参考库只由脚本读取，输出只有题号和分数。

| 参考库 | 题数 | 最高分 | 超过 0.3 |
|---|---:|---|---:|
| bench/distill/*/cases（含 cases-shelved，不含 v1.42） | 3030 | 0.276（log-10015 vs tab-8217） | 0 |
| bench/bashprobe/cases | 26 | 0.196（fs-10067 vs bsh-0026） | 0 |
| bench/weatherprobe/cases | 14 | 0.182（cfg-10192 vs wth-0014） | 0 |
| bench/workbank/cases* | 152 | 0.206（scr-10136 vs code-0003） | 0 |

首轮有 7 题超过 0.3（全部是对 distill 旧题），已改写到 0.3 以下：nt-10293（0.886，原题与 nt-9159 都问「天气和气候的区别」，换成「零星阵雨是否整天都下」）、fs-10069（0.581 vs fs-9011，改问法）、hyb-10203（0.452 vs hyb-9135，「the day after tomorrow」改成「Friday night」）、nt-10174（0.400 vs nt-9120）、web-10145（0.356 vs web-9008）、log-10059（0.333 vs log-7524）、nt-10286（0.316 vs nt-9140）。

**仓库自带的去污染**（`rwkv-lab corpus decontam`，与 b12 run_teacher.sh 相同的面，另加 weatherprobe）：workbank/cases、workbank/cases-shelved、holdout/p13、v1/cases-shelved、bashprobe、weatherprobe **六面全部 0 flagged**。首轮 bashprobe 面报了 4 题：hyb-10214 题面 CJK 3-gram 0.44（改写措辞）；code-10101 与一道 bashprobe 编辑题共用 `DB_HOST`、`db-old.internal`、`db-new.internal` 三个标识符（实质撞题，整题改成缓存地址 cache-a → cache-b）；cfg-10149 的 `main.go`、nt-10176 的 `access.log` 是通用名（改名）。为定位撞的是哪个标识符，我用脚本打印了**我题里**与该 probe 题标识符的交集（就是上面这几个名字），没有打印 probe 的题面或文件。

**禁读范围**：没有打开 b10-scale-prompt §0 列出的目录，也没有读 bashprobe / weatherprobe 的 cases、gen.py、cases_data.py；只读了两个 README 的题目轴表格。上面的脚本比对是唯一接触。

## 5. 出题中发现的问题

1. **just-bash 的几个坑（老师和学生在沙箱里也会遇到）**：
   - `find logs -not -path 'logs/web-3/*'` 不排除任何东西（相对路径开头的 `-path` 模式不匹配），`-path '*/web-3/*'` 才生效。
   - `find <中文目录> … | while read f; do mv "$f" …; done` 静默不改名（ASCII 路径正常）；`for f in $(find …)` 和通配循环正常。
   - jq 不接受中文键的点号写法：`.岗位` 报 parse error，要写 `.["岗位"]`；`.[0].["k"]` 也报错，要写 `.[0]["k"]`。
   - 没有 `xargs -I`、`bc`、`du -b`，`paste -sd+` 不认合写参数。
   - 参考解都已绕开这些写法；M9 题的 NOTES 里写了实际可用的命令。
2. **casegen.check_reference 看不到编辑结果**：sidecar 是写时复制的（`native/justbash/sidecar.ts` 不写宿主文件），而 `casegen.check_reference` 在命令跑完后直接读宿主临时目录。实测 `sed -i` 之后宿主文件不变，所以 b12 系列 build.py 的编辑题参考解在当前 sidecar 下必然报失败（或者在旧版 sidecar 下才通过过）。b14 改用 sidecar 的 `read` op 回读；v1.41 的脚本按要求没有改。
3. **5 位题号与 lint 冲突**：见 §6.1。

## 6. 需要你在本地处理的事

### 6.1 题号规则（先决定）

`internal/lab/bank/lint.go` 的 `caseIDRe = ^([a-z]+)-(\d{4})$` 和 `internal/lab/runs/compare.go` 的 `excludeIDRe = ^[a-z]+-\d{4}$` 只认 4 位题号。b14 按要求从 10001 开始，lint 每题报一条 `dir_structure`；`runs compare --exclude` 读到 5 位题号会直接报错。其余工具（verify、decontam、corpus paths、exclude_lib.py、behavior.py）不受影响。

建议的两行改法（我在云端改过并准备跑 `go test ./internal/lab/bank/ ./internal/lab/runs/`，但这一步被权限拦下，所以已撤回，没有提交）：

```diff
-	caseIDRe  = regexp.MustCompile(`^([a-z]+)-(\d{4})$`)
+	caseIDRe  = regexp.MustCompile(`^([a-z]+)-(\d{4,5})$`)
-			bad("dir_structure", fmt.Sprintf("case id %s must be <scenario abbrev>-<4 digits>", pyReprValue(dirname)))
+			bad("dir_structure", fmt.Sprintf("case id %s must be <scenario abbrev>-<4 or 5 digits>", pyReprValue(dirname)))
-var excludeIDRe = regexp.MustCompile(`^[a-z]+-\d{4}$`)
+var excludeIDRe = regexp.MustCompile(`^[a-z]+-\d{4,5}$`)
```

不想改 Go 的话，另一个办法是把 b14 整体重编到 4 位空号段，`build.py` 只需改各模块里的题号。

### 6.2 查不到地点的路径会被 corpus paths 剔除（需要你定）

`internal/lab/corpus/paths.go` 的 `fixtureWeatherMiss` 只放过「同一轮后面有成功的 get_weather」的 `location not found`。M10g 里单问一个地点的 4 题（10267–10270）和两轮题第二轮（10274、10275）正确路径就是「查一次、失败、如实说查不到」，必然被当成工具错误剔除；两地对比的 3 题（10271–10273）只有先查查不到的地点、再查已知城市的顺序才保留。若要这类行进训练集，需要在 paths.go 里加一条有范围的放行（例如：未恢复的 location not found，且该轮 expect 有 output_contains_any 的「查不到」判据并且通过）；不改的话这 6 题只能算 0 行，规划 §5 已按此口径写。

### 6.3 老师跑题、可解性验证、行为验收（照 b12 流程）

```bash
scripts/build-justbash.sh && go build -o local/bin/rwkv-lab ./cmd/rwkv-lab && go build -o local/bin/rwkv-cli ./cmd/rwkv-cli
cd bench/distill/tools/b14 && python3 build.py && cd -          # 重建并复验参考解（逐字节应与提交一致）
bench/distill/tools/gate.sh v1.42                                 # 预期 verify 300/300，lint 只剩 dir_structure（或 §6.1 改完后为 0）
for b in "b14a 10001 10040" "b14b 10041 10080" "b14c 10081 10120" "b14d 10121 10160" \
         "b14e 10161 10200" "b14f 10201 10240" "b14g 10241 10270" "b14h 10271 10300"; do
  bench/distill/tools/b14/run_teacher.sh $b                       # 去污染六面 + deepseek-flash k=3 + behavior.py
done
```

- `run_teacher.sh` 与 `tools/b12/run_teacher.sh` 参数相同（T=0.3、top_p=1、k=3、work-v2、`--file-tools lines`、沿用 `v1.41/teacher/b12-suffix.txt`），只是按题号区间选题、结果写到 `local/runs/distill/v142/<批次>/`、去污染多一面 weatherprobe、行为验收用 `tools/b14/behavior.py`（复用 b12 判据，另加 ask_then_run / weather_switch / weather_unknown / concept_then_weather 四种）。
- 每批先看 0/3 题：超过 25% 先分诊（题面、判据还是老师），再决定改题或剔除，不放宽判据凑数。最可能卡住的是 M10b（整文件相等）和 M9b（相似行、保护范围），这正是要教的东西。
- S5 之后照 v1.41 流程：`corpus paths` → 逐条读弱判据/写任务/恢复类路径 → 剔除登记 `common/exclude.jsonl` → render 出老师脚本 `v1.42/teacher/b14?.jsonl` → 每批写报告并在 `common/batches.jsonl` 登记（本轮没有老师结果，所以没有登记）。
- 渲染、think-full、全集打包、后缀处理仍按 v1.41 §5 的待办，不在本批范围。

### 6.4 其他

- `casegen.check_reference` 的写时复制问题（§5.2）要不要在共用模块里修，由你决定；修法就是 `tools/b14/common.py` 的 `run_reference`。
- 中文占比 60.7% 刚过线。如果老师跑完后中文题的 covered 率明显低于英文题，有效行的中文占比可能跌破 60%，届时优先补中文的 M9a/M9g。
