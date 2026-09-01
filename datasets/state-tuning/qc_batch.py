"""QC gates for state-tuning semantic batches.

Usage:
    python3 qc_batch.py semantic/batch-001.json [more.json ...]

Exit code is the number of hard failures. Gates prefixed GATE are hard;
WARN lines are for human review.
"""
import json
import re
import sys
import glob
import collections

SCHEMA = {
    'read_lines': {'path', 'start_line', 'end_line'},
    'write_file': {'path', 'content'},
    'replace_lines': {'path', 'start_line', 'end_line', 'content'},
    'append_file': {'path', 'content'},
    'web_search': {'query', 'max_results'},
    'web_fetch': {'urls'},
    'datetime': {'op', 'args'},
    'spawn_agents': {'tasks'},
}
# Keys the tool's JSON Schema declares in "required". Nullable-but-required
# keys must be present as null, never omitted (fileedit.go:78).
REQUIRED = {
    'read_lines': {'path', 'start_line', 'end_line'},
    'write_file': {'path', 'content'},
    'replace_lines': {'path', 'start_line', 'end_line', 'content'},
    'append_file': {'path', 'content'},
    'web_search': {'query'},
    'web_fetch': {'urls'},
    'datetime': {'op'},
    'spawn_agents': {'tasks'},
}
SUBTYPES = {'pure_knowledge', 'pure_calculation', 'chitchat',
            'trap_capability', 'near_neighbor', 'positive', 'multi_step'}

# Result shapes the tools actually return, from their Go implementations. A
# state trained on an invented envelope learns to read a payload the tools never
# produce, so the keys are checked rather than trusted.
RESULT_KEYS = {
    'read_lines': {'path', 'start_line', 'end_line', 'total_lines', 'content'},
    'write_file': {'path', 'bytes'},
    'replace_lines': {'path', 'replaced_from', 'replaced_to', 'total_lines'},
    'append_file': {'path', 'appended_bytes'},
    'web_search': {'query', 'results'},
    'web_fetch': {'pages'},
    'datetime': None,   # shape varies by op; checked separately
    'spawn_agents': {'results'},
}

# Real JSON Schemas exported from the Go source by export_schemas_test.go.
# Validating against these catches maxItems/enum/minimum violations that a
# key-name check cannot see.
_SCHEMA_FILE = __file__.rsplit('/', 1)[0] + '/tool_schemas.json'
try:
    TOOL_SCHEMAS = {k: v['parameters']
                    for k, v in json.load(open(_SCHEMA_FILE)).items()}
except (OSError, ValueError):
    TOOL_SCHEMAS = {}


# datetime.args is typed only as "object" in the schema, so its real contract
# lives in the Go implementation (assistant.go): parseRowTime accepts RFC3339,
# "YYYY-MM-DD HH:MM:SS", or "YYYY-MM-DD"; duration goes through Go's
# time.ParseDuration, which has NO day unit -- "45d" is an error, "1080h" is not.
GO_DURATION = re.compile(r'^-?(\d+(\.\d+)?(ns|us|µs|ms|s|m|h))+$')
TIME_FORMATS = (
    re.compile(r'^\d{4}-\d{2}-\d{2}$'),
    re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'),
    re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'),
)


def check_datetime(args):
    errors = []
    op = args.get('op')
    inner = args.get('args')
    if not isinstance(inner, dict):
        return [f'args must be an object, got {type(inner).__name__}']
    if op == 'now':
        if inner:
            errors.append(f'op=now takes empty args, got keys {sorted(inner)}')
    elif op == 'compare':
        for key in ('left', 'right'):
            value = inner.get(key)
            if value is None:
                errors.append(f'op=compare needs {key!r}')
            elif not any(p.match(str(value)) for p in TIME_FORMATS):
                errors.append(f'{key}={value!r} is not RFC3339 or YYYY-MM-DD')
        for key in set(inner) - {'left', 'right'}:
            errors.append(f'op=compare: unexpected key {key!r}')
    elif op == 'add':
        value = inner.get('time')
        if value is None:
            errors.append("op=add needs 'time'")
        elif not any(p.match(str(value)) for p in TIME_FORMATS):
            errors.append(f'time={value!r} is not RFC3339 or YYYY-MM-DD')
        duration = inner.get('duration')
        if duration is None:
            errors.append("op=add needs 'duration'")
        elif not GO_DURATION.match(str(duration)):
            errors.append(
                f'duration={duration!r} is not a Go duration '
                '(ns/us/ms/s/m/h only; there is no day unit)')
        for key in set(inner) - {'time', 'duration'}:
            errors.append(f'op=add: unexpected key {key!r}')
    return errors


def validate_against_schema(schema, value, path='args'):
    """Minimal JSON Schema check for the subset the tool schemas use."""
    errors = []
    types = schema.get('type')
    if types:
        allowed = types if isinstance(types, list) else [types]
        ok = any(
            (t == 'object' and isinstance(value, dict)) or
            (t == 'array' and isinstance(value, list)) or
            (t == 'string' and isinstance(value, str)) or
            (t == 'integer' and isinstance(value, int) and not isinstance(value, bool)) or
            (t == 'number' and isinstance(value, (int, float)) and not isinstance(value, bool)) or
            (t == 'boolean' and isinstance(value, bool)) or
            (t == 'null' and value is None)
            for t in allowed)
        if not ok:
            errors.append(f'{path}: want {allowed}, got {type(value).__name__}')
            return errors
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: {value!r} not in {schema["enum"]}')
    if isinstance(value, str):
        if 'minLength' in schema and len(value) < schema['minLength']:
            errors.append(f'{path}: shorter than minLength {schema["minLength"]}')
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            errors.append(f'{path}: longer than maxLength {schema["maxLength"]}')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{path}: {value} below minimum {schema["minimum"]}')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{path}: {value} above maximum {schema["maximum"]}')
    if isinstance(value, list):
        if 'minItems' in schema and len(value) < schema['minItems']:
            errors.append(f'{path}: {len(value)} items, minItems {schema["minItems"]}')
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            errors.append(f'{path}: {len(value)} items, maxItems {schema["maxItems"]}')
        item_schema = schema.get('items')
        if item_schema:
            for index, item in enumerate(value):
                errors += validate_against_schema(item_schema, item, f'{path}[{index}]')
    if isinstance(value, dict):
        props = schema.get('properties') or {}
        for key in schema.get('required') or ():
            if key not in value:
                errors.append(f'{path}: required key {key!r} missing')
        if schema.get('additionalProperties') is False:
            for key in value:
                if key not in props:
                    errors.append(f'{path}: unexpected key {key!r}')
        for key, sub in props.items():
            if key in value:
                errors += validate_against_schema(sub, value[key], f'{path}.{key}')
    return errors
THINK_MAX_TOKENS = 80  # verify precisely with internal/tokenizer; this is a char-based guard
BAD_THINK = re.compile(r'\b(wait|actually|hmm|let me reconsider)\b', re.I)
# Self-doubt only. A bare 让我 is too broad: "不是让我现在改" is an ordinary
# negation, not hesitation, and matching it rejects well-formed think lines.
BAD_THINK_ZH = re.compile(r'(让我(重新|再)[想考看]|重新考虑|^等等|，等等|不过话说|不对，)')
ENUMERATED = re.compile(r'(^|\s)(1\.|2\.|首先|其次|第一|第二)')
CONTAM = re.compile(r'\bsubmit\b|list_files|read_file\b|run_file|chmod|'
                    r'run_tests|run_awk|run_lua|BFCL|expected_submit')
# A concrete object: a path-like token, a URL, a digit run, a Chinese numeral
# quantity, or a capitalised named entity. Note \b\d+\b does NOT work here:
# CJK chars are \w in Python, so "9月1日" has no word boundary around the 9.
OBJ = re.compile(r'[\w./-]+\.(?:ya?ml|json|jsonl|md|txt|py|csv|tsv|log|toml|ini'
                 r'|conf|js|ts|go|sh|bash|sql|env|lock|rs|java|rb|php|xml|html)'
                 r'|https?://[\w./?=&%-]+'
                 r'|\d+'
                 r'|[一二三四五六七八九十百千]+(?=[个条行页天月日次])'
                 r'|\b[A-Z][A-Za-z]{2,}(?:\.[a-z]+)?\b')


def objects(text):
    return set(m.group(0).lower() for m in OBJ.finditer(text))


def tokens(text):
    return set(re.findall(r'[一-鿿]|[a-z_]+', text.lower()))


def main(paths):
    cases = []
    skipped = []
    for p in paths:
        try:
            loaded = json.load(open(p))
        except ValueError as err:
            # A batch still being written in chunks is not yet valid JSON.
            # Report it and carry on rather than failing the whole corpus run.
            skipped.append((p.split('/')[-1], str(err)[:60]))
            continue
        for c in loaded:
            c['_src'] = p.split('/')[-1]
        cases.extend(loaded)
    print(f'loaded {len(cases)} cases from {len(paths) - len(skipped)} file(s)')
    for name, err in skipped:
        print(f'  SKIPPED (incomplete JSON): {name} — {err}')
    if not cases:
        return 0

    fails = collections.defaultdict(list)
    warns = collections.defaultdict(list)
    sub = collections.Counter()
    lang = collections.Counter()
    ids = collections.Counter()
    bysub = collections.defaultdict(list)

    for c in cases:
        cid = c.get('id', '<no-id>')
        ids[cid] += 1
        st = c.get('subtype')
        sub[st] += 1
        lang[c.get('lang')] += 1
        bysub[st].append(c)
        if st not in SUBTYPES:
            fails['GATE0_bad_subtype'].append((cid, st))
        ts = set(c.get('tools') or ())
        if not ts <= set(SCHEMA):
            fails['GATE0_unknown_tool'].append((cid, sorted(ts - set(SCHEMA))))
        if not 3 <= len(ts) <= 6:
            fails['GATE0_subset_size'].append((cid, len(ts)))

        # multi_step cases carry action/call/think/answer inside `steps`, not at
        # the top level (see SPEC.md's worked example) -- GATE10 below checks
        # those per-step instead of duplicating the checks here.
        if st != 'multi_step':
            action = c.get('action')
            if action == 'abstain':
                if c.get('call') is not None:
                    fails['GATE1_abstain_has_call'].append(cid)
            elif action == 'call':
                call = c.get('call')
                if not isinstance(call, dict):
                    fails['GATE1_call_not_object'].append(cid)
                else:
                    name, args = call.get('name'), call.get('arguments')
                    if name not in SCHEMA:
                        fails['GATE1_bad_tool_name'].append((cid, name))
                    else:
                        if name not in ts:
                            fails['GATE2_tool_not_visible'].append((cid, name, sorted(ts)))
                        if not isinstance(args, dict):
                            fails['GATE1_args_not_object'].append((cid, type(args).__name__))
                        else:
                            extra = set(args) - SCHEMA[name]
                            missing = REQUIRED[name] - set(args)
                            if extra:
                                fails['GATE1_args_extra'].append((cid, name, sorted(extra)))
                            if missing:
                                fails['GATE1b_required_key_omitted'].append(
                                    (cid, name, sorted(missing)))
                            schema = TOOL_SCHEMAS.get(name)
                            if schema:
                                for problem in validate_against_schema(schema, args):
                                    fails['GATE1c_schema_violation'].append(
                                        (cid, name, problem))
                            if name == 'datetime':
                                for problem in check_datetime(args):
                                    fails['GATE1d_datetime_args'].append(
                                        (cid, problem))
            else:
                fails['GATE0_bad_action'].append((cid, action))

            think = (c.get('think') or '').strip()
            if not think:
                fails['GATE4_think_empty'].append(cid)
            if BAD_THINK.search(think) or BAD_THINK_ZH.search(think):
                fails['GATE4_think_selfdoubt'].append((cid, think[:40]))
            if ENUMERATED.search(think):
                fails['GATE4_think_enumerated'].append((cid, think[:40]))

            answer = c.get('answer') or ''
            cjk = bool(re.search(r'[一-鿿]', answer))
            if c.get('lang') == 'zh' and not cjk:
                fails['GATE6_lang_mismatch'].append(cid)
            if c.get('lang') == 'en' and cjk:
                fails['GATE6_lang_mismatch'].append(cid)
        if CONTAM.search(json.dumps(c, ensure_ascii=False)):
            fails['GATE7_contamination'].append(cid)

    for cid, n in ids.items():
        if n > 1:
            fails['GATE0_duplicate_id'].append((cid, n))

    # GATE10: multi_step chains. Each step but the last is a call carrying a
    # result in the tool's real shape; the last is the answer stage.
    for c in bysub.get('multi_step', []):
        cid = c['id']
        steps = c.get('steps') or []
        if len(steps) < 2:
            fails['GATE10_too_few_steps'].append((cid, len(steps)))
            continue
        if len(steps) > 5:
            fails['GATE10_too_many_steps'].append((cid, len(steps)))
        seen_calls = []
        for index, step in enumerate(steps):
            last = index == len(steps) - 1
            action = step.get('action')
            if not last and action != 'call':
                fails['GATE10_nonfinal_not_call'].append((cid, index, action))
                continue
            if last and action not in ('answer', 'abstain'):
                fails['GATE10_final_not_answer'].append((cid, action))

            # Per-step think/language checks mirror GATE4/GATE6, since a
            # multi_step case's think and answer text lives on each step
            # rather than at the case's top level.
            step_think = (step.get('think') or '').strip()
            if not step_think:
                fails['GATE4_think_empty'].append((cid, index))
            if BAD_THINK.search(step_think) or BAD_THINK_ZH.search(step_think):
                fails['GATE4_think_selfdoubt'].append((cid, index, step_think[:40]))
            if ENUMERATED.search(step_think):
                fails['GATE4_think_enumerated'].append((cid, index, step_think[:40]))

            if action != 'call':
                step_answer = (step.get('answer') or '').strip()
                if not step_answer:
                    fails['GATE10_answer_empty'].append((cid, index))
                cjk = bool(re.search(r'[一-鿿]', step_answer))
                if c.get('lang') == 'zh' and not cjk:
                    fails['GATE6_lang_mismatch'].append((cid, index))
                if c.get('lang') == 'en' and cjk:
                    fails['GATE6_lang_mismatch'].append((cid, index))
                continue
            call = step.get('call') or {}
            name, args = call.get('name'), call.get('arguments')
            if name not in SCHEMA:
                fails['GATE10_bad_tool'].append((cid, index, name))
                continue
            if name not in (c.get('tools') or ()):
                fails['GATE10_tool_not_visible'].append((cid, index, name))
            if not isinstance(args, dict):
                fails['GATE1_args_not_object'].append((cid, index))
            else:
                schema = TOOL_SCHEMAS.get(name)
                if schema:
                    for problem in validate_against_schema(schema, args):
                        fails['GATE1c_schema_violation'].append((cid, index, problem))
                if name == 'datetime':
                    for problem in check_datetime(args):
                        fails['GATE1d_datetime_args'].append((cid, index, problem))
            # The runner rejects a repeated successful call, so training one
            # teaches a move that gets refused.
            signature = json.dumps([name, args], sort_keys=True, ensure_ascii=False)
            if signature in seen_calls:
                fails['GATE10_duplicate_call'].append((cid, index, name))
            seen_calls.append(signature)
            # Result envelope and payload shape.
            result = step.get('result')
            if not isinstance(result, dict):
                fails['GATE10_result_missing'].append((cid, index))
                continue
            if result.get('tool') != name:
                fails['GATE10_result_tool_mismatch'].append(
                    (cid, index, result.get('tool'), name))
            if result.get('ok') is True:
                payload = result.get('result')
                wanted = RESULT_KEYS.get(name)
                if wanted is not None:
                    if not isinstance(payload, dict):
                        fails['GATE10_result_payload_shape'].append(
                            (cid, index, type(payload).__name__))
                    else:
                        missing = wanted - set(payload)
                        extra = set(payload) - wanted
                        if missing:
                            fails['GATE10_result_keys_missing'].append(
                                (cid, index, name, sorted(missing)))
                        if extra:
                            fails['GATE10_result_keys_extra'].append(
                                (cid, index, name, sorted(extra)))
            elif result.get('ok') is not False:
                fails['GATE10_result_no_ok'].append((cid, index))

    # GATE8: near_neighbor must share a concrete object with a positive and
    # name a paired tool. This is what catches "generic domain knowledge"
    # masquerading as a near neighbour.
    positives = bysub.get('positive', [])
    pos_objs = set()
    for c in positives:
        pos_objs |= objects(c.get('user', ''))
    for c in bysub.get('near_neighbor', []):
        cid = c['id']
        pair = c.get('paired_with')
        if not pair:
            fails['GATE8_no_paired_with'].append(cid)
        elif pair not in (c.get('tools') or ()):
            fails['GATE8_pair_not_visible'].append((cid, pair))
        if not objects(c.get('user', '')):
            fails['GATE8_no_concrete_object'].append((cid, c.get('user', '')[:46]))
    # A near_neighbor is only useful when the corpus also holds the positive it
    # is one word away from, sharing the same concrete object. Report the ones
    # that stand alone — they still test restraint, but they do not test the
    # boundary, which is the point of the subtype.
    unpaired = []
    for c in bysub.get('near_neighbor', []):
        if not (objects(c.get('user', '')) & pos_objs):
            unpaired.append(c['id'])
    if unpaired:
        warns['WARN_nn_without_paired_positive'].append(
            f'{len(unpaired)}/{len(bysub.get("near_neighbor", []))}: '
            + ','.join(unpaired[:10]))

    # WARN: trap_capability phrasing balance
    traps = bysub.get('trap_capability', [])
    explicit = [c['id'] for c in traps
                if any(t in (c.get('user') or '') for t in SCHEMA)]
    if traps:
        ratio = len(explicit) / len(traps)
        line = f'{len(explicit)}/{len(traps)} spell a literal tool name ({ratio:.0%})'
        (warns if ratio <= 0.45 else fails)['WARN_trap_phrasing_skew'].append(line)

    # GATE5: near-duplicate user strings across the whole corpus
    seen = [(c['id'], tokens(c.get('user', ''))) for c in cases]
    for i in range(len(seen)):
        for j in range(i + 1, len(seen)):
            a, b = seen[i][1], seen[j][1]
            if a and b:
                jac = len(a & b) / len(a | b)
                if jac > 0.7:
                    fails['GATE5_near_duplicate'].append(
                        (seen[i][0], seen[j][0], round(jac, 2)))

    print('subtypes', dict(sub))
    print('lang', dict(lang), f'zh={lang["zh"]/max(len(cases),1):.0%}')
    print()
    hard = 0
    for key in sorted(fails):
        rows = fails[key]
        hard += len(rows)
        print(f'{key}: {len(rows)}')
        for row in rows[:8]:
            print('    ', row)
    for key in sorted(warns):
        rows = warns[key]
        print(f'{key}: {len(rows)}')
        for row in rows[:8]:
            print('    ', row)
    print()
    print('HARD FAILURES:', hard)
    return hard


if __name__ == '__main__':
    args = sys.argv[1:] or sorted(glob.glob('datasets/state-tuning/semantic/batch-*.json'))
    sys.exit(min(main(args), 120))
