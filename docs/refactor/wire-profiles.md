# Wire profiles (generated)

Generated from the wire registry by `go test ./internal/agent/wire -update-wire-docs`. Do not edit by hand.

## Registered presets

| preset | canonical | short |
| --- | --- | --- |
| `bfcl-md-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=deep-fence;abstain=no-tool;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+deep-fence+no-tool+route-progressive+progressive` |
| `bfcl-xml-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `route-progressive+progressive` |
| `default` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `default` |
| `md-fakethink-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=fake-think-half;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+fake-think-half+no-tool` |
| `md-fence-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=fence;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+fence+no-tool` |
| `md-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=deep-fence;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+deep-fence+no-tool` |
| `native-v1` | `format=xml;transcript=product;transport=native;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `native` |
| `primitive-v1` | `format=md-fence;transcript=benchmark;transport=text;thinking=off;prefill=fence;abstain=none;terminal=submit;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+benchmark+fence+submit` |
| `xml-progressive-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `route-progressive+progressive` |
| `xml-route-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=envelope;abstain=none;terminal=none;route=respond-inspect;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `envelope+route-respond-inspect` |
| `xml-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;loop=0,0,0,0,0,0,0,0,0,0,false` | `default` |

## Axis domain

| axis | values |
| --- | --- |
| `format` | `xml`, `md-fence` |
| `transcript` | `product`, `benchmark` |
| `transport` | `text`, `native` |
| `thinking` | `off`, `fast`, `full` |
| `prefill` | `none`, `envelope`, `fence`, `deep-fence`, `fake-think-half`, `fake-think-closed` |
| `abstain` | `none`, `no-tool`, `no-tool+gate-state`, `no-tool+gate-evidence` |
| `terminal` | `none`, `any tool name (e.g. submit)` |
| `route` | `none`, `respond-inspect`, `progressive` |
| `catalog` | `full`, `progressive` |
| `control` | `base`, `fewshot` |
| `feedback` | `raw`, `compress-fetch` |
| `subagent` | `block`, `raw` |

## Recovery vocabulary

| transcript | recoveries |
| --- | --- |
| `xml` | `think_stripped`, `array_envelope`, `envelope_recovered`, `json_repaired`, `function_wrapper`, `key_alias`, `arguments_hoisted`, `stringified_arguments`, `nested_name`, `name_inferred`, `tool_renamed`, `path_argument`, `legacy_xml_call`, `xml_path_alias` |
| `md-fence` | `think_stripped`, `array_envelope`, `envelope_recovered`, `json_repaired`, `function_wrapper`, `key_alias`, `arguments_hoisted`, `stringified_arguments`, `nested_name`, `name_inferred` |

## Modifiers

`anchor`, `compress-fetch`, `deep-fence`, `envelope`, `fake-think`, `fake-think-closed`, `fence`, `fewshot`, `gate-evidence`, `gate-state`, `native`, `no-tool`, `prefill-none`, `progressive`, `raw-subagent`, `route-progressive`, `route-respond`, `submit`, `think-fast`, `think-full`, `think-off`

## Override keys

`abstain`, `catalog`, `control`, `feedback`, `format`, `prefill`, `route`, `subagent`, `terminal`, `thinking`, `transcript`, `transport`
