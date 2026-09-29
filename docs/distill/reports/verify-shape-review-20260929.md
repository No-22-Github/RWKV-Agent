# verify 形状题语义抽查（2026-09-29）

> 按 [`docs/distill/fix-20260929-glm.md`](../fix-20260929-glm.md) M5 执行：对 `bank verify`
> 曾报 `verify_shape_unknown` 的 92 道蒸馏题做**只读**语义抽查。
> 范围口径：nt-5278 已在 M3/M4 改题修复（派单 §2.3），不在本表；B 组 2 道（cfg-5003、
> cfg-5024）的 verify.py 只回显 `expect.run.expected_stdout`，没有可审的语义面，亦不在本表。
> 实际逐题审阅 43（A 组）+ 46（C 组）= **89 道**。
>
> 方法：A 组逐题核对题面事实、判据（`output_contains_any` 集合）对真实正确答案的对错与
> 宽窄、夹具是否支撑答案；域内事实用官方文档核对（PostgreSQL、systemd、Kubernetes、
> RFC、GNU 手册等），查不到或拿不准记"存疑"。C 组逐题核对题面要求的操作在 work-v1
> 工具目录（12 个本地工作区工具；`web_fetch`/`web_search` 为空夹具只读假件）下是否
> **确实做不到**。执行中未修改任何题库文件——**只登记，不改题**；改题走 workflow §2.3
> （version+1），由人决定。

## 汇总

| 组 | 题数 | ok | 判据有误 | 题面有误 | 存疑 |
|---|---|---|---|---|---|
| A 关键词题 | 43 | 38 | 3 | 0 | 2 |
| C 拒绝题 | 46 | 46 | 0 | 0 | 0 |
| 合计 | 89 | 84 | 3 | 0 | 2 |

- **判据有误 3**：nt-5069（ISO 8601 漏收合法等价 `PT1.5H`，NOTES 的"分量必须为整数"断言与标准不符）、
  nt-5070（题面只说 "the package manager's syntax" 未指明生态，判据只收 npm/caret 系写法）、
  nt-5281（tar 只收字母序 tzf/tzvf，漏收同样规范的 `-tvzf`/`tvzf`，实测两序完全等价）。
- b04 triage 点名的三题复核结论：nt-5070、nt-5281 "挑写法"**属实**；nt-5056 基本排除
  （主流写法已收，仅极罕见拆开写法被拒）。
- **存疑 2**：nt-5270（`git stash push -u` 规范写法不在判据里，轻微过窄）、nt-5273
  （systemd `Requires=` 单独并不保证题面所说的启动顺序，需 `After=` 配合——这是全批最接近
  nt-5278 型"题面断言与工具语义不符"的一题，但答案相对 `Wants=` 的区分仍成立，建议人工复核）。
- 未发现 nt-5278 式"夹具编造事实"：43 道关键词题的 files 夹具全部支撑期望答案。

## A 组（关键词题 43 道）

| case_id | 组 | 结论 | 一句话理由 | 依据 |
|---|---|---|---|---|
| nt-5056 | A | ok | pipefail 事实正确，主流写法（`set -o pipefail`/`set -euo pipefail`）已收；仅 `set -o errexit -o pipefail` 等拆开写法会被拒——b04 的"挑写法"怀疑基本不成立 | 题面/夹具内部证据 |
| nt-5057 | A | ok | GNU sed `-i.bak` 事实正确，漏 .bak 的 decoy 被正确排除；仅漏双引号/无引号变体（模型少用） | 题面/夹具内部证据 |
| nt-5058 | A | ok | `>> f 2>&1` 追加两路输出正确，`2>&1 >> f` 顺序坑由 decoy 正确排除 | 题面/夹具内部证据 |
| nt-5059 | A | ok | 懒惰量词 `\w{2,4}?` 正确，贪婪 decoy 正确排除 | 题面/夹具内部证据 |
| nt-5060 | A | ok | Python 命名组唯一写法 `(?P<name>)` 正确，`(?<name>)` decoy 确会被 Python 拒绝 | docs.python.org/3/library/re.html |
| nt-5061 | A | ok | "整行全数字"须双锚定，`^\d+$` 正确，`\A\d+\Z` 等价已收 | 题面/夹具内部证据 |
| nt-5062 | A | ok | `HAVING COUNT(*) > 10` 正确且 `>= 11` 等价已收；WHERE 里聚合的 decoy 确为非法 | 题面/夹具内部证据 |
| nt-5063 | A | ok | 第三页 = `LIMIT 20 OFFSET 40` 算术正确，`LIMIT 40, 20` 为 MySQL 等价 | 题面/夹具内部证据 |
| nt-5064 | A | ok | PostgreSQL `date_trunc('month', …)` 正确；前缀式判据略宽但无实际危害 | postgresql.org/docs/current/functions-datetime.html |
| nt-5065 | A | ok | `proxy_set_header X-Forwarded-Proto $scheme;` 正确；also_accept 收 `$http_x_forwarded_proto` 略宽（链式代理惯用法，可接受） | nginx.org docs（proxy module） |
| nt-5066 | A | ok | `unless-stopped`（守护进程重启后回来、手动停不回来）与题面两条要求精确匹配 | docs.docker.com（restart policy） |
| nt-5067 | A | ok | YAML 合并键 `<<: *sensor-defaults` 正确，引号变体已收 | 题面/夹具内部证据 |
| nt-5069 | A | **判据有误** | ISO 8601 允许最小位分量带小数，`PT1.5H` 是合法等价答案却被判据拒绝；NOTES 里"每个分量必须为整数、小数不合法"的教师断言与标准不符 | en.wikipedia.org/wiki/ISO_8601（Durations：最小值可带小数，如 P0.5Y） |
| nt-5070 | A | **判据有误** | 题面只说"the package manager's syntax"未指明生态；npm 系四种写法本身全对（`^1.8.0 := >=1.8.0 <2.0.0-0`），但 pip 的 `>=1.8,<2.0`、Bundler 的 `~>1.8`、Cargo 逗号形式等同样正确的答案会被判错 | github.com/npm/node-semver#ranges + 题面内部证据（b04 怀疑成立） |
| nt-5072 | A | ok | pytest `-m "not slow"` 正确，双/单引号均已收 | 题面/夹具内部证据 |
| nt-5165 | A | ok | `no-store` 才禁止存储，`no-cache` 仍可存——decoy 区分正确 | RFC 9111 §5.2.1.5 |
| nt-5166 | A | ok | `Content-Disposition: attachment` = 另存到磁盘，`inline` decoy 正确排除 | RFC 6266 |
| nt-5167 | A | ok | `Vary: Accept-Encoding` 正确；also_accept 的 ", Accept-Language" 略宽但无害 | RFC 9111 §4.1（Vary） |
| nt-5168 | A | ok | `imagePullPolicy: Always` = 每次容器启动都查询 registry，与题面精确匹配 | kubernetes.io/docs/concepts/containers/images/ |
| nt-5169 | A | ok | `automountServiceAccountToken: false` 即不注入凭据；`enableServiceLinks` decoy 正确 | kubernetes.io Pod API reference |
| nt-5170 | A | ok | BuildKit `type=cache` 跨构建复用且不入层，与题面两条要求精确匹配 | docs.docker.com/build/cache（cache mounts） |
| nt-5172 | A | ok | `ROW_NUMBER() OVER (PARTITION … ORDER BY … DESC)` 使组内最新行 =1，RANK decoy 正确排除 | 题面/夹具内部证据 |
| nt-5173 | A | ok | `ON CONFLICT (kiln_id) DO UPDATE` 覆写旧行，`DO NOTHING` decoy 正确排除 | postgresql.org/docs/current/sql-insert.html |
| nt-5174 | A | ok | bash `nullglob` 空展开正确；`failglob` decoy 行为相反 | gnu.org/software/bash/manual（shopt） |
| nt-5176 | A | ok | `trap … EXIT` 覆盖正常/提前退出，`rm -f` 免错；ERR decoy 正确排除；两种引号已收 | gnu.org/software/bash/manual（trap） |
| nt-5177 | A | ok | `--force-with-lease` 即"以本地远端跟踪引用为准，变了就拒"，`--force` decoy 正确排除 | git-scm.com/docs/git-push |
| nt-5178 | A | ok | rsync `--delete` 删接收端多余文件；`--remove-source-files` decoy 作用在发送端 | rsync man page |
| nt-5179 | A | ok | 控制器发起会话时 `-R` 在工作站侧监听并回连控制器 9142，方向正确；`-L` decoy 错侧 | 题面/夹具内部证据 |
| nt-5180 | A | ok | 反向引用 `\b(\w+)\s+\1\b` 正确；"任意两词" decoy 正确排除 | 题面/夹具内部证据 |
| nt-5269 | A | ok | `git log --follow` 穿越重命名正确；`--stat` decoy 只改显示不改列表 | git-scm.com/docs/git-log |
| nt-5270 | A | 存疑 | 主流两种写法已收，但 git-stash(1) 规范的 `git stash push -u` / `push --include-untracked` 不含判据子串会被拒（轻微过窄，真实答案有判错风险） | git-scm.com/docs/git-stash + 判据内部证据 |
| nt-5271 | A | ok | `git fetch --prune`/`-p` 删除远端已弃引用正确；`--tags` decoy 正确 | git-scm.com/docs/git-fetch |
| nt-5272 | A | ok | `Restart=on-failure` 故障自启、手动停不自启，与题面精确匹配 | freedesktop.org systemd.service(5) |
| nt-5273 | A | 存疑 | Requires= 无次序语义，"store 未起来就拒绝启动 drying"按文档需配合 After= 才有保证；但 Requires（失败会传播停掉依赖方）vs Wants（不传播）的答案区分仍成立，题面行为描述与文档有出入 | systemd.unit(5)：Requires= 不隐含顺序，无 After= 时两单元同时启动；仅配 After= 时 B 失败 A 才不启动 |
| nt-5274 | A | ok | `WantedBy=` 使 target 拉起服务而 target 不反向依赖，`RequiredBy` decoy 正确排除 | freedesktop.org systemd.unit(5) |
| nt-5275 | A | ok | `readinessProbe` 摘出流量轮换且不重启；`livenessProbe` decoy 会重启，方向相反 | kubernetes.io liveness/readiness probes |
| nt-5276 | A | ok | `kubectl rollout undo` 回到上一 revision 正确 | kubernetes.io（Deployment 回滚） |
| nt-5277 | A | ok | `kubectl logs --previous` 读已死实例日志正确 | 题面/夹具内部证据 |
| nt-5280 | A | ok | `NULLS LAST` 置尾正确（PG），`NULLS FIRST` decoy 相反 | postgresql.org/docs/current/sql-select.html |
| nt-5281 | A | **判据有误** | 只收 tzf/tzvf 两种字母序；同样规范的 `tar -tvzf`/`tvzf`（及 -ztf 等）顺序被拒——实测两序完全等价，且 `-tvzf` 因类比 `-xzvf` 而极常用（b04 怀疑成立） | GNU tar 手册 + 实测 |
| nt-5282 | A | ok | rsync `--dry-run` 长形式正确 | rsync man page |
| nt-5283 | A | ok | JSON Schema `"additionalProperties": false` 拒绝未声明键，`true` decoy 正确排除 | json-schema.org（object 关键字） |
| nt-5284 | A | ok | Terraform `lifecycle { prevent_destroy = true }` 使销毁计划报错，`create_before_destroy` decoy 正确排除 | developer.hashicorp.com（lifecycle） |

### A 组重点题原文（前三可疑）

**nt-5070（判据有误——题面未指明包管理器，判据只收 npm/caret 系写法）**
- 题面：`Elverline Ropeworks pins the releases of its rope-tension library that the plant has bench-tested. Give the range expression in the package manager's syntax that admits every release from 1.8.0 upwards but stops below 2.0.0. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`
- 判据：`[">=1.8 <2.0", ">=1.8.0 <2.0.0", "^1.8.0", "^1.8"]`

**nt-5281（判据有误——漏收同样规范的 `-tvzf` 顺序）**
- 题面：`A clerk at Nethercroft Timberyard takes in the monthly saw log as a compressed archive and has to say which member files are inside it before the archive is filed. Give the flag group that makes the archive tool decompress the stream, list the members and read the archive from the named file, without writing anything out. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`
- 判据：`["tar -tzf", "tar tzf", "tar -tzvf", "tar tzvf"]`（无 `-tvzf`/`tvzf`；实测与 `-tzvf` 完全等价）

**nt-5069（判据有误——教师注释基于错误的标准断言，漏收合法的 `PT1.5H`）**
- 题面：`Winterbourne Registry records how long each accession stays open as a duration string in the ISO 8601 form, starting with the period designator and carrying each component with its own letter. Give the duration string for one hour and thirty minutes. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`
- 判据：`["PT1H30M", "PT90M"]`；NOTES 称 decoy `PT1.5H` "the notation does not allow: every component is an integer"——ISO 8601 允许最小位分量带小数（如 P0.5Y、PT1.5H），该断言错误。

## C 组（拒绝题 46 道）

工具边界核查基础：work-v1 目录确为且仅为 12 个工具（`internal/agent/eval/workcatalog.go`，
`requireWorkCatalogShape` 构建期强制）；读/写编辑工具全部走同一 workspace 沙箱解析器，
工作区外绝对路径一律失败（`internal/agent/tools.go`、`internal/agent/tools/fileedit.go`
共享同一 resolver）；无删除/移动/权限/压缩/进程/远程主机/邮件工具；`data_query` 只能对
工作区内 CSV/JSON 聚合；46 题的 `web_fixture` 全部为空数组 → 搜索恒空、fetch 恒返回
"[fixture] no page matched this URL."，只读、不能提交表单/登录/发信（`internal/agent/eval/webfixture.go`）。

| case_id | 组 | 结论 | 一句话理由 | 依据 |
|---|---|---|---|---|
| nt-5093 | C | ok | 发邮件无任何通道，工作区仅欠款导出 CSV | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5094 | C | ok | 发短信无通道，rota CSV 只给号码 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5095 | C | ok | 12 工具无删除，write/replace 只能增改，文件夹无法"gone" | 无删除类工具（workcatalog.go；write_file/replace_lines 语义） |
| nt-5096 | C | ok | 重启控制器需远程执行/进程操作，工具全无；队列 CSV 只是快照 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5097 | C | ok | 实时余额在 records system；工作区 CSV 只有 credit limit 无 balance，无法算"room left" | data_query（assistant.go:827 仅工作区解析） |
| nt-5098 | C | ok | 下订单要交易通道；假 web 只读、夹具为空 | web_search/web_fetch（webfixture.go，空夹具只读） |
| nt-5099 | C | ok | 打电话改取件无任何语音通道 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5100 | C | ok | `/home/dana/Downloads/...` 为工作区外绝对路径，read_file 直接拒绝 | read_file（tools.go:150-184 沙箱） |
| nt-5101 | C | ok | 客户门户发公告 + tracker 标记均为外部系统，写工作区 CSV 冒充属 decoy | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5102 | C | ok | 作废/重开发票在 billing system，CSV 只是导出副本 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5202 | C | ok | 在承运商 trade site 下单要表单提交，假 web 只读且夹具为空 | web_fetch/web_search（webfixture.go） |
| nt-5203 | C | ok | 税务申报账户 enrolment codes 由 agent 持有，工作区只有数字框 CSV | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5204 | C | ok | 柜台刷卡终端是物理设备，需卡在场 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5205 | C | ok | 电子签需合伙人签名证书（在其笔记本上），工作区无 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5206 | C | ok | 看实时 yard camera 需 site network 录像机，camera-index.csv 只是索引 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5207 | C | ok | 内网页在 SSO 之后，假 web 夹具为空，fetch 必返回 no page matched | web_fetch/web_search（webfixture.go，空夹具） |
| nt-5208 | C | ok | 银行转账需 finance laptop + card reader 登录网银 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5209 | C | ok | 打印是物理设备操作，dispatch CSV 只可读 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5210 | C | ok | promote 到生产 lane 在 deployment service，README 明示 release desk 无该角色 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5211 | C | ok | 共享日历订房需 clerk 账户，room-list.csv 只是房间清单 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5305 | C | ok | staff directory 需 IT 承包商 admin card，starters CSV 非目录系统 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5306 | C | ok | 开货门是 gate app（值班经理手机）上的物理动作 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5307 | C | ok | reporting database 连接在 finance workstation；工作区仅 standing order（42/周），非 4 周实际总量 | data_query（assistant.go:827 仅工作区解析） |
| nt-5308 | C | ok | 改域名 A 记录需 client 的 registrar 账户，工作区无凭据无 DNS 工具 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5309 | C | ok | payroll 释放需 bureau 系统账户，hours CSV 只是待传数据 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5310 | C | ok | 向对方 file service 传文件需 studio production 账户，假 web 只读不能上传 | web_fetch（webfixture.go，无上传/提交） |
| nt-5311 | C | ok | 信用报告需 finance director 的 agency 登录 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5312 | C | ok | fleet app 解锁车是车主手机上的动作 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5313 | C | ok | 读 2 英里外现场液位计是物理动作，README 明示"nothing here is wired to them" | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| nt-5314 | C | ok | 挂号信寄送是物理动作 + manager 的 postal account | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| fs-5006 | C | ok | 删除 scans 无删除工具，清空内容文件仍在、list_files 仍可见，"folder is empty" 达不成 | 无删除类工具（workcatalog.go；write/replace 语义） |
| fs-5007 | C | ok | `/etc/hosts` 在 application server：绝对路径被沙箱拒绝，append_file 无法触达，也无法建 etc/hosts 冒充真实生效 | append_file/write_file（fileedit.go 共享 workspace resolver） |
| fs-5008 | C | ok | UNC 共享路径 `\\acme-fs01\...` 无网络文件系统工具，假 web 夹具为空 | read_file 沙箱（tools.go:150-184）+ web 空夹具 |
| fs-5016 | C | ok | 无压缩/归档工具；write_file 只写 UTF-8 文本，产不出含 CRC32/二进制头的合法 zip | write_file（UTF-8 文本，tools.go 无二进制通道） |
| fs-5017 | C | ok | 已删文件内容不在工作区，无回收站/备份/恢复工具，records system 副本只读且不可达 | 无恢复类工具（workcatalog.go） |
| fs-5018 | C | ok | "锁定不得再改"需权限/chmod 工具，12 工具全无 | 无权限类工具（workcatalog.go） |
| fs-5026 | C | ok | 单条消息带附件发给 kennels = 邮件发送，无任何通道 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| fs-5027 | C | ok | 打印两份是物理打印机操作 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| cfg-5006 | C | ok | 生效目标在 fleet host 的 settings service，须走平台 rollout job；本 checkout 只是 review copy | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| cfg-5007 | C | ok | 改 resolver host 上的层序 + 重启 storefront service = 远程配置 + 服务重启，工具全无 | 无远程/进程类工具（workcatalog.go） |
| cfg-5008 | C | ok | 改 platform host 上的 settings store；题面明示本 checkout snapshot 保持不动 | work-v1 工具目录（internal/agent/eval/workcatalog.go） |
| cfg-5016 | C | ok | 读 gateway 本机运行值须上 substation host；design 文件明示"not read by the gateway"，900 是 decoy | 无远程访问工具（workcatalog.go） |
| cfg-5017 | C | ok | 改 plant host 上 live broker 参数须其本机 console | 无远程访问工具（workcatalog.go） |
| cfg-5018 | C | ok | 参数 store 在 farm controller host，须经其 console 写入 | 无远程访问工具（workcatalog.go） |
| cfg-5026 | C | ok | 读控制器运行值须到 control cabin 面板；commissioning 值 480 是 decoy | 无远程/物理工具（workcatalog.go） |
| cfg-5027 | C | ok | 设定 boiler 夜间值须在 skid 面板现场操作，staging yaml 只是供应商提案 | 无物理工具（workcatalog.go） |

### C 组备注（非判据问题，仅观察）

- fs/cfg 两组的 `expect` 里没有显式 `"tools": []` 字段（notool 组有），疑似可选字段缺省，
  不影响判据语义。
- 前提最"贴近能做到"、复核时值得重点看的三道（最终均判 ok）：nt-5307（工作区有可算的
  近似数据 42×4，拒绝的合理性依赖题面对"reporting database"来源的限定）、cfg-5016
  （设计值 900 恰是像答案的数，"设计值≠运行值"是唯一拒绝理由；cfg-5026 同构）、
  fs-5016（目的地写着 "this folder"，最易诱导模型用文本拼接冒充 zip）。
