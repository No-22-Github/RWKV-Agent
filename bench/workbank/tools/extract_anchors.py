#!/usr/bin/env python3
"""Wash out corpus rows whose prompt is byte-identical to a workbank eval prompt.

Selects rendered ws700 rows by scope (anchor rows = the 36 seed anchors, family =
anchor + variants, all), optionally re-verifies that each anchor's prompt prefix
equals the step-1 prompt the harness actually sent in a recorded run, and writes a
text-only JSONL plus a provenance manifest.

The identity check compares the harness-recorded prompt (summary.json
cases[].turns[0].result.steps[0].request.prompt) with the corpus text truncated at
the first "\nAssistant:". The corpus appends " " + the assistant turn after that
boundary, so a match means the model was trained on exactly the prompt it is later
evaluated on.

Refuses to overwrite existing outputs. Text is copied verbatim; loss_spans and meta
are kept only in the rendered sidecar.
"""
import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

DEFAULT_RENDERED = 'outputs/workspace-agent-700/generated/rendered/none-ctx4096/train.jsonl'
ASSISTANT = '\nAssistant:'
CALL = re.compile(r'<tool_call>(\s*\{.*?\}\s*)</tool_call>', re.S)


def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def tool_calls(text):
    """Every tool call in the assistant turns, in order, as {name, arguments}.

    Scanning starts after the first "\nAssistant:" boundary: the System block
    carries a <tool_call> template whose arguments are `{...}`, which is not
    valid JSON and must not be mistaken for the trajectory's first call.
    """
    boundary = text.find(ASSISTANT)
    if boundary >= 0:
        text = text[boundary + len(ASSISTANT):]
    calls = []
    for match in CALL.finditer(text):
        try:
            payload = json.loads(match.group(1))
        except ValueError:
            calls.append({'name': None, 'arguments': None})
            continue
        calls.append({'name': payload.get('name'), 'arguments': payload.get('arguments')})
    return calls


def assistant_turns(text):
    return len(text.split(ASSISTANT)) - 1


def prompt_prefix(text):
    index = text.find(ASSISTANT)
    if index < 0:
        return None
    return text[:index + len(ASSISTANT)]


def eval_prompts(run):
    summary = json.loads((Path(run) / 'summary.json').read_text())
    prompts = {}
    for case in summary['cases']:
        steps = case['turns'][0]['result'].get('steps') or []
        if steps:
            prompts[case['id']] = steps[0]['request']['prompt']
    return prompts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='output directory; must not exist')
    parser.add_argument('--rendered', default=DEFAULT_RENDERED)
    parser.add_argument('--scope', choices=['anchor', 'family', 'all'], default='anchor')
    parser.add_argument('--eval-run', default='runs/state-check-20260920/final-s0-20260920-workbank',
                        help='run directory whose step-1 prompts are compared against the corpus prompts')
    parser.add_argument('--allow-missing-eval', action='store_true',
                        help='write the export even when the eval run is absent (identity then unverified)')
    args = parser.parse_args()

    output = args.output
    if output.exists():
        parser.error(f'refusing to overwrite {output}')
    rendered = Path(args.rendered)
    rows = []
    for number, line in enumerate(rendered.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row.get('text'), str):
            raise ValueError(f'{rendered}:{number}: expected rendered record with string text')
        rows.append(row)
    families = {row['meta']['parent_seed_id'] for row in rows if row['meta'].get('is_seed_anchor')}
    if args.scope == 'anchor':
        selected = [row for row in rows if row['meta'].get('is_seed_anchor')]
    elif args.scope == 'family':
        selected = [row for row in rows if row['meta']['parent_seed_id'] in families]
    else:
        selected = list(rows)

    prompts = {}
    eval_run = Path(args.eval_run)
    if (eval_run / 'summary.json').exists():
        prompts = eval_prompts(eval_run)
    elif not args.allow_missing_eval:
        parser.error(f'{eval_run}/summary.json not found; pass --allow-missing-eval to export unverified')

    manifest_rows = []
    verified = 0
    compared = 0
    for row in selected:
        text = row['text']
        meta = row['meta']
        prefix = prompt_prefix(text)
        case_id = meta['parent_seed_id']
        expected = prompts.get(case_id)
        identical = None
        if expected is not None and prefix is not None:
            compared += 1
            identical = prefix == expected
            verified += bool(identical)
        calls = tool_calls(text)
        first = calls[0] if calls else None
        manifest_rows.append({
            'corpus_id': meta['id'],
            'workbank_case': case_id,
            'is_seed_anchor': bool(meta.get('is_seed_anchor')),
            'generator_branch': meta.get('generator_branch'),
            'scenario': meta.get('scenario'),
            'split': meta.get('split'),
            'prefill': meta.get('prefill'),
            'n_tok': meta.get('n_tok'),
            'n_supervised_tok': meta.get('n_supervised_tok'),
            'text_chars': len(text),
            'text_sha256': sha256(text),
            'prompt_prefix_sha256': sha256(prefix) if prefix is not None else None,
            'eval_prompt_sha256': sha256(expected) if expected is not None else None,
            'prompt_identical_to_eval': identical,
            'assistant_turns': assistant_turns(text),
            'tool_calls': len(calls),
            'first_tool': (first or {}).get('name'),
            'first_arguments': (first or {}).get('arguments'),
            'tool_sequence': [call['name'] for call in calls],
        })

    output.mkdir(parents=True)
    textonly = output / f'ws700-{args.scope}-textonly.jsonl'
    with textonly.open('x', encoding='utf-8', newline='\n') as handle:
        for row in selected:
            handle.write(json.dumps({'text': row['text']}, ensure_ascii=False, separators=(',', ':')) + '\n')
    rendered_out = output / f'ws700-{args.scope}-rendered.jsonl'
    with rendered_out.open('x', encoding='utf-8', newline='\n') as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')

    manifest = {
        'source': str(rendered),
        'source_sha256': hashlib.sha256(rendered.read_bytes()).hexdigest(),
        'scope': args.scope,
        'rows': len(selected),
        'anchor_families': sorted(families),
        'cases_missing_from_corpus': sorted(set(prompts) - families),
        'eval_run': str(eval_run) if prompts else None,
        'prompt_comparisons': compared,
        'prompt_identical': verified,
        'total_text_chars': sum(len(row['text']) for row in selected),
        'total_corpus_tokens': sum(row['meta'].get('n_tok', 0) for row in selected),
        'total_supervised_tokens': sum(row['meta'].get('n_supervised_tok', 0) for row in selected),
        'files': {'textonly': textonly.name, 'rendered': rendered_out.name},
        'rows_detail': manifest_rows,
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

    table = ['# 导出行与 workbank 用例对照', '',
             f'来源 `{rendered}`（sha256 `{manifest["source_sha256"][:16]}…`），scope=`{args.scope}`，共 {len(selected)} 行。',
             '',
             '`prompt_identical_to_eval` 比较的是 harness 记录的首步 prompt 与语料文本截到第一个 `\\nAssistant:` 的前缀；'
             '语料在该边界之后接 `" " + assistant 轮`，因此相等即"训练用的正是评测要发的那个 prompt"。',
             '',
             '| corpus_id | workbank case | branch | n_tok | n_sup_tok | prompt 相同 | text sha256 |',
             '|---|---|---|---:|---:|---|---|']
    for row in manifest_rows:
        same = '未比较' if row['prompt_identical_to_eval'] is None else ('是' if row['prompt_identical_to_eval'] else '否')
        table.append(f'| {row["corpus_id"]} | {row["workbank_case"]} | {row["generator_branch"]} | '
                     f'{row["n_tok"]} | {row["n_supervised_tok"]} | {same} | `{row["text_sha256"][:12]}` |')
    table += ['', f'workbank 有、语料没有的用例：{", ".join(manifest["cases_missing_from_corpus"]) or "无"}',
              '', '这三个数字决定了"焊接"的信息量：',
              f'- 全文 token（dense loss 下参与梯度的总量）：{manifest["total_corpus_tokens"]}',
              f'- 原监督 token（masked SFT 口径下真正属于 assistant 动作的量）：{manifest["total_supervised_tokens"]}',
              '']
    (output / 'identity.md').write_text('\n'.join(table) + '\n')

    # First-step inventory: the anchors do NOT share one opening action, so the
    # export records each row's own target instead of assuming a common step.
    first_dist = Counter(row['first_tool'] or '(无调用)' for row in manifest_rows)
    args_seen = {}
    for row in manifest_rows:
        key = (row['first_tool'], json.dumps(row['first_arguments'], sort_keys=True, ensure_ascii=False))
        args_seen[key] = args_seen.get(key, 0) + 1
    steps = ['# 逐行首步动作清单', '',
             f'共 {len(manifest_rows)} 行；首步动作分布：' +
             '、'.join(f'`{name}` {count}' for name, count in first_dist.most_common()) + '。',
             '',
             '首步指每行轨迹里第一次 assistant 输出所调用的工具，**不是所有行共用一个动作**——'
             '所以"首步一致率"存在一个必须报出的常数基线（恒选众数动作的得分）。',
             '',
             '| workbank case | 首步工具 | 首步参数 | 工具序列 | 步数 |',
             '|---|---|---|---|---:|']
    for row in manifest_rows:
        shown = json.dumps(row['first_arguments'], ensure_ascii=False)
        if len(shown) > 70:
            shown = shown[:67] + '…'
        sequence = ' → '.join(call or '(未解析)' for call in row['tool_sequence'])
        steps.append(f'| {row["workbank_case"]} | {row["first_tool"] or "(未解析)"} | `{shown}` | '
                     f'{sequence} | {row["assistant_turns"]} |')
    steps += ['', '首步 (工具, 参数) 组合重复情况：', '']
    for (tool_name, tool_args), count in sorted(args_seen.items(), key=lambda item: -item[1]):
        steps.append(f'- {count}× `{tool_name}` `{tool_args[:120]}`')
    steps += ['', '首步后的整条序列在同一场景内并不统一，逐行可见上表；'
              '`manifest.json` 的 `tool_sequence` 字段给出完整序列，可直接用于核对。', '']
    (output / 'first-steps.md').write_text('\n'.join(steps) + '\n')

    readme = [f'# ws700 {args.scope} 行导出（state 训练用）', '',
              f'- `{textonly.name}`：{len(selected)} 行，只有 `text` 字段，供 `rwkv_state_tune` 直接读取。',
              f'- `{rendered_out.name}`：同样的行，保留 `loss_spans` 与 `meta`，用于核对与将来做 masked 对照。',
              '- `manifest.json`：逐行 sha256、token 计数、首步动作与完整工具序列、与评测 prompt 的一致性判定。',
              '- `identity.md`：逐行对照表。',
              '- `first-steps.md`：逐行首步动作（工具 + 参数）与工具序列，含首步分布与常数基线提示。', '',
              '## 这批数据是什么', '',
              f'`{args.scope}` 范围的 ws700 渲染行。其中 {verified}/{compared} 行的 prompt 与 '
              f'`{args.eval_run}` 的 workbank 首步 prompt **逐字节相同**；'
              f'语料里没有 {", ".join(manifest["cases_missing_from_corpus"]) or "（无）"} 的对应行。', '',
              '## 训练', '',
              '```sh',
              './rwkv_state_tune --model ./rwkv-g1k-7b-temp-3601.pth \\',
              f'  --data ./{textonly.name} --output ./state_output \\',
              '  --ctx 4096 --lr 0.00001 --lr-final 0.00001 \\',
              f'  --warmup-steps 10 --save-every {len(selected)} --epochs <自行设定>',
              '```', '',
              '`rwkv_state_tune` 对整个 `text` 做因果 next-token loss，不读 `loss_spans`；'
              '因此除了 assistant 动作，System/User/Tool 文本同样被监督（本批次中 assistant 侧约占 '
              f'{100 * manifest["total_supervised_tokens"] / max(1, manifest["total_corpus_tokens"]):.1f}% 的 token）。',
              '若要只监督动作，需要训练器支持 mask，本导出不含该能力。', '',
              '## 多步段的对齐缺口（重要）', '',
              '这批行的 prompt 只覆盖**第一步决策**。评测从第二步起，harness 会在每次工具回执后追加一段 User 提醒',
              '（`internal/agent/protocol_g1.go` 的 `PostToolReminder`，`Use the Tool results above to continue the current task. …`），',
              '重复调用被拒时改用 `duplicateToolAnswerReminder`，协议出错时还有修复提示；',
              '而 ws700 渲染器（`tooling/workv1_wire.py`）只写 `<tool_response>`，**700 行语料里这三类提醒一条都没有**。',
              '因此：首步 prompt 与评测逐字节相同，第二步及以后每一条评测 prompt 都不在语料分布内。',
              '想让"焊接"覆盖多步动作，需要先在渲染器里补上这些提醒再重渲，否则步骤 ≥2 仍是在训练一个评测不会出现的转写形态。', '',
              '## 评价口径（重要）', '',
              '- 这 36 行的 prompt 就是 workbank 评测的 prompt，所以在这 36 题上提升属于**分布内记忆**，'
              '不能当作通用能力提升报告；`nt-0001..0004` 在语料中没有对应行，仍是未见过任务。',
              '- workbank 判分同时约束工具使用与答案契约（如 `tools=[]`、`output_equals`、plain number），'
              '只把证据"焊"进轨迹、不修答案形态，仍会判负。',
              '- 训练后请用与历史 run 相同的配置评测（同二进制、`--state-id`、wire profile 与并发），'
              '并与零 state 对照臂同批比较。', '']
    (output / 'README.md').write_text('\n'.join(readme) + '\n')
    print(f'{output}: {len(selected)} rows, {manifest["total_corpus_tokens"]} corpus tokens, '
          f'{manifest["total_supervised_tokens"]} supervised tokens')
    if compared:
        print(f'prompt identity vs {args.eval_run}: {verified}/{compared} byte-identical')
    else:
        print('prompt identity: not verified (no eval run provided)')
    missing = manifest['cases_missing_from_corpus']
    if missing:
        print(f'workbank cases with no corpus row: {missing}')


if __name__ == '__main__':
    main()
