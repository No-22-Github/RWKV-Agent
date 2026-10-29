# b23c 出题报告（v2.3，35101–35170，共 70 题）

## 分布
| 子类 | 题数 | 英文 | 多轮 | 平均首轮题面字符 | L0 |
|---|---:|---:|---:|---:|---:|
| C1 缺关键信息先追问 | 50（cfg 16、doc 14、hyb 12、fs 8） | 27（54%） | 20（40%，第一轮追问、第二轮用户回答后执行） | 32 | 0 |
| C0 信息足够直接做 | 20（cfg 6、doc 5、hyb 5、fs 4） | 11（55%） | 4（20%） | 52 | 8（占全批 11%） |

全批多轮 24/70（34%）。C0 题面比 C1 长（C0 要把目标说清楚），这是对照组固有差别；题面风格相同。
歧义类型：同键多文件（env/服务/客户端）、只有用户知道的值（新负责人、新主机、新税率、新比例）、互相矛盾的材料（两位评审结论相反、银行汇率 vs 内部结算价、14 天 vs 30 天退款）、两个同样"标准"的模板、fs 里的多个候选删除/重命名对象。
C1 全部是 TR-AMBIG；C0 有 12 题带 TR-DECOY（相似的干扰文件必须不变）。

## 判据
- C1 第一轮：`forbidden_tools` = write_file/replace_lines/append_file（fs 题加 bash）；`output_contains_any` = 中英追问词表（含 `?`/`？`，约 120 项）；`output_contains` = 一个候选名或当前值（证明看到了歧义）；`output_excludes` = 第一人称假完成说法（"我已修改/I've updated/Done!" 等，不含 "尚未修改""I haven't changed"）。
- C1 两轮：第二轮用 case 级 `expect.files` 判终态（equals/contains/absent/unchanged；新建/重命名文件用 equals/contains），`output_excludes` 放"又在追问"的说法。单轮题所有文件 `unchanged`。
- C0：`expect.files` 判结果，`output_excludes` = 不该出现的追问句（"你指的是/do you mean/which one do you…"）。
- tool_policy：must_offer 含 list_files/read_file/write_file/replace_lines（fs 为 list_files/read_file/bash，bash 在首轮被 forbidden；计算类加 calculator）；约一半非 fs 题 never_offer bash。
- 自测 `tools/b23c/selftest.py`：7 种追问说法（中英）全命中，2 句不追问不误过，4 句假完成全命中，3 句否定/未完成说法不误杀，重复追问 2 句命中、正常完成说明 2 句不误杀。

## 自检
- build.py 连跑两次，70 题文件 sha 汇总一致。
- `gate.sh v2.3 '*-351[0-7]?'`：70 checked，0 violation；verify 70/70。
- `corpus loadcheck`：197 题（含其他批次）全部加载通过。

## 走错方向的答法与判据
- C1：(1) 读完直接改 staging.yaml 并说"已改好" → write_file 命中 forbidden_tools，文件被改，假完成词命中；(2) 只回"两个文件都有 timeout=20"但不提问 → 无追问词/问号，判不过；(3) 泛泛追问"你想改什么？"但不点候选 → 缺 output_contains 的候选名。
- C0：(1) 条件齐全却回"请问您指的是哪个环境？" → REASK 命中且文件未改；(2) 把 decoy（production/H1/其他 .bak）也改了 → 对应文件 unchanged 失败。

## 风险与老师最可能答错的题
- 候选名关键词：cfg-35103/35109/35137/hyb-35142 的 output_contains 是"当前值"（smtp-eu1、eu-west-2、3%、6），老师若只泛泛追问不引用当前值会误判；hyb-35135（签收单）、doc-35119 同类。
- 老师可能对 doc-35124、hyb-35133、hyb-35136 这类冲突题直接"两个都列出并推荐一个"后动手；hyb-35131 等计算题老师可能用"两张都改"来规避。
- 两轮 equals 对格式敏感：cfg-35112/35116（YAML 缩进）、doc-35128、doc-35130；计算填表题（hyb-35138/39/41/42）用 contains，老师若把数字写成 "24.5" 或 "2,180" 会误杀。
- fs-35144（两组重复照片）、fs-35146（保留几份）追问点多，老师可能只问一半，仍能过。
- fs 题 turn 2 要求 bash（req2），老师若用 list_files 之外没调 bash 但文件已变是不可能的，风险低。
- C0 hyb-35163 把折后价写在 Discount 行只判含 "4224"，写成 "4,224" 会误杀。
