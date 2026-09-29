# v1.2 state checkpoint 跑分 —— 实施规格书（交 VPS Agent 执行）

> 读者：在 VPS 上执行跑分的 Agent。文中"必须 / 不得 / 不许"都是硬约束，每条附有理由，不要为了"更快""更稳"而绕过。
> 核心章节是 §2（arm 与 state 对照表）和 §4（run 有效性判定）。前者是这次实验唯一推导不出来的东西，后者是今天实际踩过的坑。
> 实验设计（问题、判定规则）见同目录 [PLAN.md](PLAN.md)；本文只写怎么执行，两者冲突时以本文为准。

## 0. 目标

用 Cloudflare 公网端点 `https://api-7b.rwkvos.com/v1`，单队列、**总并发 64**，把 14 个 arm（2 个对照 + 12 个 v1.2 state checkpoint）
在 workbank（148 题）和 bfcl-product（60 题）上各跑一遍，采样用 `g1k-agent`，k=1。然后按 PLAN §3 的规则挑出最优 checkpoint，
写 `REPORT.md`。

**workbank 主口径是剔除泄漏种子题后的干净 112 题**，148 题全量只作参考。原因：v1.1 和 v1.2 语料都含 base700，它覆盖了 36 道 workbank 种子题，其中 35 道的原题轨迹进了训练集（t927 报告 §8 的 2026-09-29 更正）。t927 报告还专门承诺过：none 和 t927-s316 在 112 题上的数字，由这一轮同日重测给出。

最关键的取舍：**慢但稳**。2026-09-29 下午试过所有"更快"的做法，全部失败，没有产出一个有效 run（见 §2.4）。
这一轮不追速度，预计 2.5–4 小时。

## 1. 总览

| 集合 | 数量 | 来源 | 作用 |
|---|---|---|---|
| 对照 arm | 2 | none（不挂 state）、t927（上一轮最优 `t927-s316.pth`） | 同日基线 |
| suffix-only arm | 6 | train-1-2-suffixonly/lr2e-2（lr 2e-2，456 步，每 79 步存一次） | 与 t927 同参数，只换了数据 |
| mixed 筛选 arm | 6 | train-1-2-mixed/lr1.5e-2（lr 1.5e-2，576 步，每 48 步存一次），隔一个点取一个 | 数据和 lr 同时变 |
| mixed 补点（条件触发） | ≤2 | 同上，未进筛选的 6 个邻点 | 峰值两侧加密 |
| 套件 | 2 | workbank 148（含 draft）、bfcl-product 60 | 主指标 strict task_success |

**不做什么**（每条都有人试过或想过）：

1. **不走 `100.64.0.4` 内网直连**（8018 网关、8001/8004/8005 单卡）。这些是生产卡：单卡直连 64 并发时空闲显存掉到 1.8G、可用 bsz 为 0；三卡同时各 64 并发时，三张卡在 30 秒内全部拒绝连接。
2. **不开第二个队列，也不把 `--max-concurrency` 调到 64 以上**。两个队列各 64（总 128）经 Cloudflare 时，出现了 146 个 502，端点随后转为 530（tunnel 断开）。
3. **不 ssh 任何服务器**（训练机、推理机都是生产环境，用户明令禁止）。
4. **不改采样档、预算、格式，也不加跑别的套件**。这一轮只隔离 checkpoint 这一个变量；换参数会破坏和 t927 轮的可比性。
5. **不删除端点上的任何 state**（`rwkv-cli state delete` 存在，但端点是共享的，别人的 state 也在上面）。
6. **不改 harness 代码和题库**。看起来像 bug 的判分结果（比如答对了却被契约拒绝）是要写进报告的发现，不是要修的东西。

## 2. Arm 与 state（核心章节）

### 2.1 State 文件来源

- 包：`state-v12-20260929.tar`（318,984,192 字节，sha256 `2ff834acf5eedc99b3c2350807110f94ea26d39fa6fa4b7096feb76383627d0f`）。
  已由用户 scp 到 VPS 主目录：`~/state-v12-20260929.tar`。解包到 `STATE_DIR=~/state-v12`（下文所有 `<STATE_DIR>` 都指这个目录）。
  包内是 19 个 `.pth`（每个 16,785,536 字节）加一个 `SHA256SUMS`，文件名就是端点上的 state_id。
- 原始训练产物在训练机 `~/no22/rwkv_lighting_cuda_train/train-1-2-*/`；包里的文件就是它们改名后的样子，改名时逐一核对过 SHA256。**不要去训练机上取**（见 §1 第 3 条）。
- 端点上 state_id 等于上传时的文件名。所以**不许改文件名**，arm 表、端点和报告三处都靠文件名对齐。

解包后先校验，不通过就停：

```bash
mkdir -p ~/state-v12 && tar -xf ~/state-v12-20260929.tar -C ~/state-v12 && (cd ~/state-v12 && sha256sum -c SHA256SUMS)
```

### 2.2 Arm 对照表（arm 名 = `--prefix` = 输出子目录名）

| # | arm | state_id | 源 checkpoint | step | epoch 位置 | sha256（前 16 位） |
|---|---|---|---|---|---|---|
| 1 | `none` | （不传 `--state-id`） | – | – | – | – |
| 2 | `t927` | `t927-s316.pth` | train-1-1/lr2e-2/state-step-00000316.pth | 316 | 2.77/4 | `e99e91fc9e5c2647` |
| 3 | `v12s-s316` | `v12s-s316.pth` | suffixonly state-step-00000316 | 316 | 2.77/4 | `1afe586f43642036` |
| 4 | `v12s-s237` | `v12s-s237.pth` | suffixonly state-step-00000237 | 237 | 2.08/4 | `97b4a627dd65a9f2` |
| 5 | `v12s-s395` | `v12s-s395.pth` | suffixonly state-step-00000395 | 395 | 3.46/4 | `6c1c1df2d46fd8ce` |
| 6 | `v12s-fin` | `v12s-fin.pth` | suffixonly state-final（=step 456） | 456 | 4/4 | `9c94339c7532f220` |
| 7 | `v12s-s158` | `v12s-s158.pth` | suffixonly state-step-00000158 | 158 | 1.39/4 | `c4332ce1698fba8f` |
| 8 | `v12s-s79` | `v12s-s79.pth` | suffixonly state-step-00000079 | 79 | 0.69/4 | `f1c6ca8ede1589be` |
| 9 | `v12m-s384` | `v12m-s384.pth` | mixed state-step-00000384 | 384 | 2.67/4 | `e78b1b9f6e554ab8` |
| 10 | `v12m-s288` | `v12m-s288.pth` | mixed state-step-00000288 | 288 | 2.00/4 | `ce4723cb1545916e` |
| 11 | `v12m-s480` | `v12m-s480.pth` | mixed state-step-00000480 | 480 | 3.33/4 | `2a981a67b8dd6838` |
| 12 | `v12m-s576` | `v12m-s576.pth` | mixed state-step-00000576（=final） | 576 | 4/4 | `bd52ad85ed076f0b` |
| 13 | `v12m-s192` | `v12m-s192.pth` | mixed state-step-00000192 | 192 | 1.33/4 | `e2fd3f6f9136cc5e` |
| 14 | `v12m-s96` | `v12m-s96.pth` | mixed state-step-00000096 | 96 | 0.67/4 | `8f28cc4beb8725ef` |

补点备用（只在 §7 M3 触发时才跑）：`v12m-s48`、`v12m-s144`、`v12m-s240`、`v12m-s336`、`v12m-s432`、`v12m-s528`，都在同一个包里。

说明：

- **执行顺序就是表里的顺序**：两个对照先跑，然后从上一轮的最优步数 316 开始往两边扫。这样即使中途被迫停下，已经跑完的部分也最有信息量。
- mixed 的 `state-final.pth` 与 step-576 字节完全相同（sha256 都是 `bd52ad85…`），所以只有一个 arm，**不要再造一个 `v12m-fin`**。
- epoch 位置：suffix-only 每个 epoch 114 步，mixed 每个 epoch 144 步。两路的 step 数不能直接比，要比 epoch 位置。
- `none` 和 `t927` 必须**当天重跑**，不许直接引用 t927 报告里的 9/148 和 16/148。因为 PLAN §3 要求同日、同端点、同二进制做配对比较。

### 2.3 端点事实（2026-09-29 16:40 实测）

| 项 | 值 |
|---|---|
| URL | `https://api-7b.rwkvos.com/v1`（sweep 的默认值） |
| 鉴权 | 两个 header：`CF-Access-Client-Id`、`CF-Access-Client-Secret`，从环境变量 `RWKV_CF_ID` / `RWKV_CF_SECRET` 注入。凭据向用户要，**不许写进任何文件** |
| 模型 id | `rwkv-g1k-7b-temp-3601`（sweep 的默认值；跑前、跑后都要核对，变了整轮作废） |
| 引擎 | `albatross-1.3.0`，每卡 `hard_max_bsz` 169。**这个数不代表能扛多少并发**：实测单卡 64 并发时可用 bsz 就已经是 0 了 |
| 后端 | 三张卡，由网关分流。上传一次会同步到三张卡，但**服务重启后所有 state 都会丢失**（16:46 发生过，别人的 state 也一起没了）。重启对我们是透明的，只能靠每个 arm 开跑前查一遍 state 列表来发现 |
| 上传 | `rwkv-cli state upload`，空闲时经 Cloudflare 约 72 秒一个，大部分时间花在服务端处理上。端点忙的时候会超过 Cloudflare 的 100 秒限制，返回 502 |
| 网络 | 如果 VPS 在国内，直连 Cloudflare 的上行可能只有几十 KB/s（Mac 上实测 66 KB/s），需要走代理。这点**待 VPS 实测**，见 M0 |

### 2.4 今天失败过的做法（不要重试）

| 时间 | 做法 | 结果 | 教训 |
|---|---|---|---|
| 16:2x | 12 个 state 并行上传 | 全部 502 | 上传必须串行 |
| 16:27 | 经 Cloudflare 开两个队列、各 64（总 128） | avail_bsz 降到 12，status 接口响应 57 秒，146 个 502，最后变成 530 | 总并发上限是 64 |
| 16:33 | 跑分的同时上传 state | 端点满载，每次上传都被 Cloudflare 切断 | **先把 state 全部传完，再开跑** |
| 16:46 | 直连三卡、各 64 | 三卡在 30 秒内全部 refused，服务重启后 state 全部丢失 | 不直连，且每个 arm 开跑前都要确认 state 还在 |
| 16:51 | 服务重启后没检查 state 就开跑 | 挂 state 的 arm 每题都报 `uploaded state not found`，每个 arm 5 秒就"跑完"了，**闸门却显示 PASS** | 见 §4.1 |

## 3. 执行

### 3.1 环境

```bash
git clone https://github.com/No-22-Github/RWKV-Agent.git && cd RWKV-Agent   # 已有就 git pull
git log --oneline -1          # 记录下 HEAD，写进报告
go version                    # go.mod 要求 go 1.26.0
go build -o local/bin/rwkv-cli ./cmd/rwkv-cli && go build -o local/bin/rwkv-lab ./cmd/rwkv-lab
git status --short            # 必须为空；不为空，这一轮只能算探索，报告里要注明
export RWKV_CF_ID=…  RWKV_CF_SECRET=…     # 向用户要；只放环境变量
AUTH=(--api-url https://api-7b.rwkvos.com/v1 --api-header-env 'CF-Access-Client-Id=RWKV_CF_ID' --api-header-env 'CF-Access-Client-Secret=RWKV_CF_SECRET')
```

- **只用 `local/bin/` 下刚编译出来的二进制**。`local/dist/` 里是旧产物，默认参数和现在不一样。
- 如果 VPS 需要代理才能访问 Cloudflare，设置 `HTTPS_PROXY`。Go 客户端会自动读取。

### 3.2 上传（M1，必须在开跑前完成）

```bash
# 先看端点上已有哪些，缺哪个补哪个，串行、失败间隔 60 s
local/bin/rwkv-cli state list "${AUTH[@]}"
for f in ~/state-v12/{t927-s316,v12s-s{79,158,237,316,395},v12s-fin,v12m-s{96,192,288,384,480,576}}.pth; do
  b=$(basename $f)
  local/bin/rwkv-cli state list "${AUTH[@]}" | awk '{print $1}' | grep -qx "$b" && continue
  until local/bin/rwkv-cli state upload "${AUTH[@]}" --file "$f"; do sleep 60; done
done
local/bin/rwkv-cli state list "${AUTH[@]}" | grep -cE '^(t927-s316|v12[sm]-s[0-9]+|v12s-fin)\.pth'    # 必须是 13
```

- **不许并行上传**。12 个同时上传时，全部被 Cloudflare 切成 502。
- 上传期间**不许跑分**，否则端点满载，上传永远超时。

### 3.3 跑分循环

把下面的内容存成 `local/run_v12.sh`，用 `nohup bash local/run_v12.sh > local/run_v12.log 2>&1 &` 启动。**同一时间只能有一个实例**。

```bash
#!/bin/bash
set -u
cd "$(dirname "$0")/.."
AUTH=(--api-url https://api-7b.rwkvos.com/v1 --api-header-env 'CF-Access-Client-Id=RWKV_CF_ID' --api-header-env 'CF-Access-Client-Secret=RWKV_CF_SECRET')
OUT=local/runs/bench-v12            # 所有 arm 都在这下面，每个 arm 一个子目录
mkdir -p $OUT/logs
ARMS=${ARMS:-"none t927 v12s-s316 v12s-s237 v12s-s395 v12s-fin v12s-s158 v12s-s79 v12m-s384 v12m-s288 v12m-s480 v12m-s576 v12m-s192 v12m-s96"}
for arm in $ARMS; do
  [ -f $OUT/$arm/DONE ] && continue                       # 断点续跑：已完成的跳过
  st=()
  if [ $arm != none ]; then
    sid=$arm.pth; [ $arm = t927 ] && sid=t927-s316.pth
    # 开跑前确认 state 还在（服务重启会把 state 清空，见 §2.4 16:51）
    if ! local/bin/rwkv-cli state list "${AUTH[@]}" | awk '{print $1}' | grep -qx "$sid"; then
      echo "$(date +%T) STOP: $sid missing on endpoint — re-run §3.2 upload, then restart this script"; exit 2
    fi
    st=(--state-id $sid)
  fi
  echo "$(date +%T) start $arm"
  local/bin/rwkv-lab bench sweep --out $OUT/$arm --prefix $arm "${st[@]}" \
      --arms g1k-agent --suites workbank,bfcl-product --k 0 --max-concurrency 64 > $OUT/logs/$arm.log 2>&1
  rc=$?
  python3 docs/evaluations/state-v12-20260929/check_v12.py $OUT/$arm || { echo "$(date +%T) STOP: $arm invalid (rc=$rc), see §4"; exit 3; }
  touch $OUT/$arm/DONE
  echo "$(date +%T) done $arm"
done
echo "$(date +%T) ALL DONE"
```

- sweep 默认就是 Cloudflare 的 URL 和 `rwkv-g1k-7b-temp-3601`。sweep 本身会拍端点快照，并在每个 arm 开跑前核对模型 id。预算、`--remote-batch-wait 0s`、30 分钟单题超时这些参数也由 sweep 自动带上，**不要手拼 `rwkv-cli agent-eval` 命令**。
- 用 `--max-concurrency 64` 时，sweep 会把并发按 workbank 48 + bfcl-product 16 分给两个套件，同时跑。这就是规程里的 64，不要再往上加。
- 脚本碰到无效的 run 会**直接退出，不会自己重试**。为什么要这样设计，见 §4.2。
- `check_v12.py` 已入库，就在本文旁边（[check_v12.py](check_v12.py)），逻辑见 §4.1。

## 4. Run 有效性判定（核心章节）

### 4.1 为什么不能信 `gate PASS`

sweep 对每个 run 打印的 `KEEP … gate PASS`，只说明**参数配对了**（格式、采样、预算、题数），**不说明题真的跑了**。
2026-09-29 下午有 10 个 run 是全部 148 题作废、2 秒就结束的，sweep 照样打印 `gate PASS`，`experiment.json` 里 `gate_passed: true`：

```
KEEP v12s-s158-workbank-g1k-agent-k0  strict 0/148  invalid 148  infra_errors 296  gate PASS  1s
```

所以每个 arm 跑完必须过 [`check_v12.py`](check_v12.py)。脚本读每个 run 目录下的 `experiment.json` 和 `summary.json`，只要有一条不满足就判这个 arm 无效（退出码 1）：

| 检查 | 字段 | 阈值 | 防的是什么 |
|---|---|---|---|
| state 还在 | `experiment.json` → `infrastructure_errors[]` 里不能出现 `uploaded state not found` | 0 次 | 服务重启后 state 丢失（16:51 实际发生过） |
| state 挂对了 | `experiment.json` → `state_id` | 等于 §2.2 表里的值（none 为空串） | arm 名和 state 对错位 |
| 参数闸门 | `experiment.json` → `gate_passed` | true | 参数配错 |
| 题数 | `experiment.json` → `strict.total` | workbank 148，bfclp 60 | 题库变了、只跑了一部分 |
| 作废题数 | `summary.json` → `metrics.invalid_cases` | ≤ 3 | 502 / 530 / stream error 这类传输错误 |
| 耗时 | `experiment.json` → `elapsed_seconds` | ≥ 120 秒 | 秒退的空跑（真实 run 要 9–18 分钟） |

- 阈值 **≤ 3 作废**：这几题按失败计入分母（和规程一致，作废计失败），并在报告里注明是哪几题。之所以不要求 0，是因为 t927 轮 14 个 run 全是 0；偶尔出一两次传输错误就重跑整个 arm，代价太大。
- **负向测试已经做过**：用 2026-09-29 本地 4 个作废的 arm 测试，脚本全部判为无效；把其中一个改成正常值，脚本放行。
  VPS 上复验的方法见 §7 M0。

### 4.2 无效时怎么办

`run_v12.sh` 碰到无效的 arm 会**直接退出，不会自动重试**。这是故意的：今天每一次失败都是端点出了问题（过载、重启、tunnel 断开），自动重试只会往一个已经坏掉的端点上继续加压。

按这个顺序处理：

1. 看 `local/runs/bench-v12/logs/<arm>.log` 最后 30 行，以及 `check_v12.py` 打印的第一条错误。
2. **`uploaded state not found`**：服务重启过。重新执行 §3.2 把 state 传齐（13/13），删掉这个 arm 的目录，重新启动 `run_v12.sh`（已完成的 arm 有 `DONE` 标记，会自动跳过）。
3. **502 / 530 / `stream error` / `context deadline exceeded`**：先停 **15 分钟**，然后用下面的命令确认端点恢复（连续 3 次 200，且 `available_bsz` ≥ 100），再删掉这个 arm 的目录重启。
   ```bash
   curl -sS https://api-7b.rwkvos.com/v1/server/status -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET" | python3 -c 'import json,sys;q=json.load(sys.stdin)["prefill_queue"];print(q["available_bsz"],q["free_vram_bytes"]/1e9)'
   ```
4. **同一个 arm 连续无效 2 次，或者当天累计 3 次无效：停下来，通知用户**，不要再试。这时候通常是推理服务本身需要人去处理。
5. **不许为了让 arm 通过而降低阈值、改 `check_v12.py`、或者把几次部分成功的 run 拼起来。**

### 4.3 端点快照

sweep 会在每个 arm 开跑前、跑完后各拍一次快照：`<arm>/endpoint-{before,after}-*-{models,server-status}.json`。

- **after 快照里的模型 id 必须仍是 `rwkv-g1k-7b-temp-3601`**。sweep 发现不一致会打印 `ENDPOINT CHANGED … void`，这时整个 arm 作废。
- 今天出现过 after 快照本身拍失败的情况：日志里是 `invalid character 'e' looking for beginning of value`（Cloudflare 返回了错误页，不是 JSON）。遇到这种情况，用 §4.2 第 3 步的 curl 命令手动补拍，模型 id 没变就不算作废，并在报告里注明。

## 5. 统计与分析

所有数字都只从**通过 §4.1 检查的 run** 里取。run 目录结构（每个 arm 一个子目录）：

```
local/runs/bench-v12/<arm>/
  <arm>-workbank-g1k-agent-k0/{experiment.json, summary.json, run.json, trace.jsonl}
  <arm>-bfclp-g1k-agent-k0/{同上}
  endpoint-{before,after}-*.json
  aborted/            # sweep 自动挪进来的失败尝试，不参与统计
```

### 5.1 必须报的数

| # | 指标 | 来源 / 命令 |
|---|---|---|
| 1 | strict 分（每 arm × 套件），148 全量 | `experiment.json` → `strict.correct / strict.total`（作废题计失败） |
| 1b | **workbank 干净 112 题分（主指标）** | `local/bin/rwkv-lab run compare --exclude-cases bench/workbank/seeded-base700.txt <arm 的 workbank run> <none 的 workbank run>`，输出 JSON 里 `passed.a` 就是该 arm 在 112 题上的通过数（`common_cases` 必须是 112，`excluded_cases` 必须是 36） |
| 2 | 与 `none`、与 `t927` 的逐题翻转和符号检验 | workbank 用上一行同一条命令（带 `--exclude-cases`），翻转在 `flips.a_pass_b_fail` / `flips.a_fail_b_pass`，另有按题族 bootstrap 的 95% 置信区间 `bootstrap.ci95_a_minus_b`；148 全量再不带 `--exclude-cases` 比一次作参考。bfcl-product 与泄漏无关，直接比 |
| 3 | 按类别拆分 | `summary.json` → `cases[].category` 分组，统计 `cases[].passed` |
| 4 | 终答续写 `✿` 题数 | 最后一轮 `cases[].turns[-1].result.output` 含 `✿` 的题数（参照 t927 报告 §6：t927-s316 在 workbank 上有 25 题被契约拒绝，其中 12 题是 `✿` 续写） |
| 5 | 答案契约拒绝题数 | 最后一轮 `output` 以下面两句之一开头（常量定义在 `internal/agent/runner_config.go:59-60`）：`I could not provide a reliable answer because the model output violated the answer contract. Please retry.` / `模型输出不符合答案契约，因此无法可靠展示。请重试。` |
| 6 | 结局分布 | 最后一轮 `cases[].turns[-1].outcome`（字符串）计数。**注意**：因传输错误作废的题，outcome 也记成 `decision_protocol_invalid`，和模型真正的协议错误混在一起。报告里要把这一类减去该 run 的 `invalid_cases`，再解释为协议错误 |
| 7 | 失分分层 | `local/bin/rwkv-lab run gate <run 目录…> --label <arm>`，只有 capability 层才算"模型不会" |

第 4、5 项是这一轮最重要的次指标：v1.2 语料在每条终答后面接了 `\n\nUser:`，专门用来修"答完不停、续写 `✿textN✿User:`"的问题。**如果 v1.2 的 `✿` 题数没有明显下降，要在报告里单独写出来**，这说明 EOS 修复没有生效，比分数高低更重要。

第 4、5、6 项用这段统计（存成 `local/v12_stats.py`）：

```python
import json, sys, collections
FALLBACK = ("I could not provide a reliable answer because the model output violated the answer contract.",
            "模型输出不符合答案契约，因此无法可靠展示。")
for run in sys.argv[1:]:
    cases = json.load(open(run + "/summary.json"))["cases"]
    last = [c["turns"][-1] for c in cases]
    flower = sum("✿" in (t["result"].get("output") or "") for t in last)
    rejected = sum((t["result"].get("output") or "").startswith(FALLBACK) for t in last)
    outcomes = collections.Counter(t["outcome"] for t in last)
    print(run.rsplit("/", 1)[-1], f"flower={flower} contract_rejected={rejected}", dict(outcomes.most_common()))
```

```bash
python3 local/v12_stats.py local/runs/bench-v12/*/*-g1k-agent-k0
```

### 5.2 判定

按 [PLAN.md](PLAN.md) §3 的预注册规则，不许事后改：

1. 主排序：**workbank 干净 112 题** strict；差 ≤ 2 题时看 bfcl-product；还分不出来就取 step 小的那个，并标"无法区分"。
2. 与 `t927` 或 `none` 的差 ≤ 2 题 → 写"无法区分"，不许宣称提升。
3. 全场最优 arm 对 `t927` 的配对翻转（干净 112 题）单侧 p > 0.05 → 对这两个 arm 各补跑 k=1、2 两个副本（§7 M4），再判一次。
4. suffix-only 和 mixed 的差异**只陈述，不归因于 lr**：mixed 同时改了数据和 lr，两个变量混在一起。

## 6. 实现注意事项（这一轮特有的坑）

**端点层**

1. 总并发 64 是上限，不是起点。不要"先试 96 看看"，今天试过 128，结果是 502 海啸和 tunnel 断开（§2.4）。
2. 上传和跑分不能同时进行。上传只在队列停着的时候做。
3. `hard_max_bsz`（169）不是可用并发。别拿它来算并发该开多少。
4. 端点是共享的，空闲时也可能有十来个别人的请求。`status` 里 `active_requests` 不为 0 是正常的，不代表有问题。

**执行层**

5. 不要手拼 `rwkv-cli agent-eval` 命令。sweep 会带上一串容易漏的参数（`--decision-max-tokens 2048`、`--remote-batch-wait 0s`、`--case-timeout 30m`、`--profile g1k --strict-spec`），漏掉任何一个都会静默产出无效结果。
6. 不要给 sweep 传 `--k 0-2`：k=1 是筛选轮，副本只在 §5.2 第 3 条触发时才补。
7. 每个 arm 用独立的 `--out` 子目录。多个 arm 共用一个目录时，端点快照文件会互相覆盖。
8. 不要为了"省时间"把 workbank 和 bfcl-product 拆成两个队列同时跑。sweep 已经在 64 的预算内让两个套件并行了。

**统计层**

9. 作废题计失败，留在分母里（规程规定）。**不要把分母改成"有效题数"**，否则作废多的 arm 反而占便宜。
10. `summary.json` 里的 `metrics.task_success.total` 是排除作废题之后的数，**不能拿来当分母**。分母只用 `experiment.json` 的 `strict.total`。
11. 被契约拒绝的题**不要**自己重新判对（t927 报告 §6 做过人工重判，那是另一回事）。这一轮只统计有多少题被拒，不改分。

**这不是 bug**

12. `none` 在 bfcl-product 上分数很高（t927 轮是 47/60），而所有 state 都更低，这是已知现象（state 会把弃权行为洗掉），不是 harness 出了问题。
13. `t927` 这次的分数和 t927 报告里的 16/148 不一样，属于正常波动（k=1 单副本），不要去"修正"它。另外，09-29 远端提交 a22cde0 改过 nt-5278 这道题（v3），题库本身也和 09-27 不同。
14. 不要自己维护种子题清单，也不要按题目 id 前缀去猜哪些是种子题。只用入库的 `bench/workbank/seeded-base700.txt`（36 行）。

## 7. 里程碑

| M | 内容 | 耗时 | 阻塞 |
|---|---|---|---|
| M0 | 环境、网络、闸门自检 | 15 分钟 | **阻塞**：不做的话，可能跑到第 3 个 arm 才发现网络或凭据有问题 |
| M1 | 校验 state 包，串行上传，确认 13/13 | 5–20 分钟 | **阻塞**：端点上缺 state 时，挂 state 的 arm 会秒退作废 |
| M2 | 14 个 arm 主矩阵 | 2.5–4 小时 | |
| M3 | mixed 峰值两侧补点（条件触发） | 0–40 分钟 | 依赖 M2 |
| M4 | 最优 arm 与 t927 各补 2 个副本（条件触发） | 0–80 分钟 | 依赖 M2/M3 |
| M5 | 写 REPORT.md | 1 小时 | |

**M0**

```bash
# 1) 凭据和模型
curl -sS https://api-7b.rwkvos.com/v1/models -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
#    期望：data[0].id == "rwkv-g1k-7b-temp-3601"
# 2) 上行速度：传一个 8 MB 随机文件（请求会被拒，只看 speed_upload）
head -c 8000000 /dev/urandom > /tmp/p.bin && curl -sS -o /dev/null -m 120 -w '%{speed_upload}\n' -X POST --data-binary @/tmp/p.bin \
  https://api-7b.rwkvos.com/v1/models -H "CF-Access-Client-Id: $RWKV_CF_ID" -H "CF-Access-Client-Secret: $RWKV_CF_SECRET"
#    期望 > 500000（B/s）。低于这个值，说明需要配 HTTPS_PROXY（Mac 直连只有 66 KB/s，走代理是 2.2 MB/s）
# 3) 检查脚本的负向测试：拿一个没跑过的空 arm 目录，必须判为无效
mkdir -p /tmp/fake/v12s-s79/v12s-s79-workbank-g1k-agent-k0 && python3 docs/evaluations/state-v12-20260929/check_v12.py /tmp/fake/v12s-s79; echo "exit=$?"
#    期望：打印 INVALID，exit=1
```

**M1**：按 §2.1 解包校验，按 §3.2 上传。验收：`state list` 里我们的 13 个都在。

**M2**：`nohup bash local/run_v12.sh > local/run_v12.log 2>&1 &`。验收：日志最后一行是 `ALL DONE`，14 个 arm 目录下都有 `DONE`，并且：

```bash
for d in local/runs/bench-v12/*/; do [ "$(basename $d)" = logs ] || python3 docs/evaluations/state-v12-20260929/check_v12.py $d; done | grep -c '^OK'   # 必须是 28
```

**M3**（mixed 补点）：在 6 个 mixed arm 里，按 §5.2 第 1 条选出最好的 `v12m-sK`，补跑 K−48 和 K+48 两个点（只补 48–576 范围内、且不在已跑列表里的点）。
先按 §3.2 上传这两个点（`~/state-v12/v12m-s{K-48,K+48}.pth`），再执行 `ARMS="v12m-s<K-48> v12m-s<K+48>" bash local/run_v12.sh`。
例：最好的是 `v12m-s384`，就补 `v12m-s336` 和 `v12m-s432`。

**M4**（副本）：只在 §5.2 第 3 条触发时做。副本不能和 k0 放在同一个 arm 目录里，否则 `DONE` 标记会让它被跳过：

```bash
for arm in <最优arm> t927; do
  sid=$arm.pth; [ $arm = t927 ] && sid=t927-s316.pth
  local/bin/rwkv-lab bench sweep --out local/runs/bench-v12-rep/$arm --prefix $arm --state-id $sid \
      --arms g1k-agent --suites workbank,bfcl-product --k 1-2 --max-concurrency 64 > local/runs/bench-v12-rep/$arm.log 2>&1
done
```

k1、k2 两个副本是串行跑的（sweep 内部按副本顺序执行），总并发仍是 64。汇总：`local/bin/rwkv-lab run replicate <3 个 workbank run 目录> --k 3 --out <arm>-rep.json`。

## 8. 报告（M5）

写到 `docs/evaluations/state-v12-20260929/REPORT.md`，结构照 [`../state-t927-20260927/REPORT.md`](../state-t927-20260927/REPORT.md)，必须包含：

1. **结论**（3–5 条）：最优 checkpoint 是哪个，对 none、对 t927 的差多少、翻转多少、p 值是多少（**先报干净 112 题，再报 148 全量**）；suffix-only 和 mixed 哪路更好；`✿` 问题是否修好了。
2. **可比性表**：HEAD、二进制 sha256（来自 `experiment.json` 的 `binary_sha256`）、端点前后快照里的模型 id、并发 64、采样 `g1k-agent`、每个 arm 的耗时。
3. **有效性**：每个 arm 的 `check_v12.py` 输出；每次作废、重跑的时间和原因。**被 §4.2 挡下的尝试也要列出来**，不能只报成功的。
4. **主矩阵**：arm × {workbank 干净 112, workbank 148, bfcl-product 60} 的 strict 分，外加 `✿` 题数、契约拒绝题数。其中 none 和 t927 两行在 112 题上的数字，就是 t927 报告 §8 承诺补上的那两个，要在报告里明确指出来。
5. 按类别拆分；与 none、与 t927 的配对翻转表。
6. 训练曲线：两路各自按 epoch 位置画 workbank 分数（表格即可），标出峰值。
7. **局限**：k=1；mixed 的数据和 lr 是混在一起的；端点是共享的，存在负载噪声。

**能说什么、不能说什么**：
- 可以说"v1.2 在 workbank 干净 112 题上比 t927 高/低 N 题（配对 +a/−b，p=…）"。
- 148 全量上的提升**不能**单独作为结论，因为里面有 36 道泄漏题。
- 差 ≤ 2 题时只能写"无法区分"。
- **不能**说"lr 1.5e-2 更好"，只能说"mixed 这一路更好"。
- **不能**把 t927 报告里 09-27 的分数和今天的分数直接放在一起比。

`local/runs/` 不入库。凭据不许出现在任何要入库的文件里。REPORT.md 要不要提交、推到哪个分支，**听用户的**。
