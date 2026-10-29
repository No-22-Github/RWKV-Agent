# b23f (v2.3: the tool the task needs is not in the catalog, ids 35401-35450)

    cd bench/distill/tools/b23f && python3 build.py

- F1 (20): `tool_policy.never_offer` removes the natural tool (calculator, data_query, replace_lines, search_text, list_files, datetime, ...); a workaround with the remaining tools exists. Judged on the result only (`expected_number`, `output_contains`, `expect.files.equals`).
- F2 (15): the task cannot be done at all (no web, no write/bash, no weather, no run). TR-NOCAP, so lint treats them as refusal cases: `output_contains_any` refusal words, `output_excludes` UNKNOWN + fake-completion wording, `forbidden_tools` = the never_offer tools, files `unchanged`. Edit requests also require the new content in the reply; follow-up turns ask for a way forward or repeat the request.
- F0 (15): same kind of task, proper tool offered (calculator / data_query / replace_lines / append_file / list_files / datetime); `required_tools` where the tool is the clear choice.
- `common.py` `mk()`: `truth(files)` is the single source of expected numbers / file contents, embedded in verify.py; shell reference commands replay in the just-bash sandbox on every build. TR-NOCAP is only for F2 (lint classifies any TR-NOCAP case as a refusal); F1/F0 use TR-DECOY / TR-NEARNAME / TR-NUMFMT.
- No web fixtures, no test-set files. Fixed seeds; reruns are byte-identical.
- Sandbox note: `date -d '… + N days'` is rejected by just-bash; epoch arithmetic (`date -d @$(( … ))`) works.
