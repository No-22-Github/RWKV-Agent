# 老师轨迹脚本（replay script）

> 用户 2026-09-25 拍板入库：老师轨迹是花钱买的、采样不可复现，而训练行 `rows.jsonl` 能由它在**任何 harness 版本**下重新生成
> （v22 修解析器那次，旧批次的 rows 就是这样重渲染出来的）。这与「派生数据不入库」的约定是**有意开的一个口子**，只放这一个目录。

每个文件是 `rwkv-lab corpus paths` 的产物、也是各批次 `corpus render` 实际用的那一份（`{case_id, outputs:[{text, supervised}]}`）。

| 文件 | 条目 | 涉及题 | sha256（前 16 位） | 用途 |
|---|---|---|---|---|
| `base700.jsonl` | 700 | 700 | `fecf68cbc0c4bd02` | 旧 700 条语料的动作序列（由 normalized records 转出，670 条能通过判分） |
| `b01.jsonl` | 339 | 213 | `9611d0162485033f` | b01 的 330 行由此渲染 |
| `b02.jsonl` | 346 | 210 | `26bc10eb974d2115` | b02 的 364 行由此渲染 |
| `b03.jsonl` | 321 | 199 | `3513cc47d201852a` | b03 的 341 行由此渲染 |

## 怎么用

```bash
# 1) 各批次的 rows（cases 模式；教材与题目都在库里）
bin/rwkv-lab corpus render --cases bench/distill/cases \
  --script bench/distill/scripts/b01.jsonl --source distill-b01 --out runs/distill/b01/corpus-rebuilt
# b02 / b03 同形，--source 分别是 distill-b02 / distill-b03；再 pack 时要带 --exclude bench/distill/exclude.jsonl

# 2) base700（records 模式：还需要 normalized records，见下面的注意）
bin/rwkv-lab corpus render --records <all.jsonl> --source base700 --out runs/distill/base700-rebuilt
```

- **必须用同一个 `bin/rwkv-cli` 渲染全部 rows**：harness 一变 `wire_hash` 就变，`pack` 会拒绝混合来源。当前值是
  `707c67403b1b2e5269ddfcd8ecee2bfb7ce4d8133912d102bc67f1324f8018cb`（harness `rwkv-agent-eval-v22`，scorer v3）。
- **`base700.jsonl` 不能单独重渲染**：records 模式要从 normalized records（`datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl`，
  在仓库外）重建 case，脚本只记录动作。b01–b03 的脚本配 `bench/distill/cases/` 就够了。
- 这三个批次脚本只含**最终仍在库内**的题（渲染前按题集过滤过）；`corpus paths` 的原始输出（含后来下架题的轨迹）留在本地
  `runs/distill/<batch>/script.jsonl`，不入库。
- 覆写风险：`corpus render` 的 `--out` 目录已存在时会拒绝；重渲染请用新目录，不要覆盖 `runs/distill/<batch>/corpus-*`。

## 可复现性验证（2026-09-25）

- `b03.jsonl`：重渲染出的 343 行与原 `runs/distill/b03/corpus-final/rows.jsonl` **逐行完全相同**。
- `b01.jsonl`：重渲染 334 行，其中 332 行逐行相同；差异的 2 行（`nt-5004--p1`、`nt-5005--p1`）只是 `case_tags.family`——
  b01 渲染之后修过一次超出「每族 ≤3」的 family，`text` 与 `loss_spans` 完全一致。最终数据集已用重渲染后的 `runs/distill/b01/corpus-v4/` 重建，
  与当前题面保持一致。
