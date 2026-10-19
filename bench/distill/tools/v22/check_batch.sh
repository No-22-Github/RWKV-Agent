#!/usr/bin/env bash
# Main-agent acceptance for one v2.2 authoring batch: gate (lint + verify),
# byte-identical rebuild, sub-type counts, no read_lines / work-v3 tag, and
# decontam against every test bank run_teacher.sh checks (any flag there
# drops the case before the teacher sees it).
#   bench/distill/tools/v22/check_batch.sh <batch> <id-substring> <gate-glob>
#   bench/distill/tools/v22/check_batch.sh b22b -341 '*-341[0-5][0-9]'
set -uo pipefail
batch=$1; sub=$2; glob=$3
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
RWKV_LAB=local/bin/rwkv-lab-v3 bench/distill/tools/gate.sh v2.2 "$glob" 2>&1 | tail -2
h(){ find bench/distill/v2.2/cases -path "*$sub*" -type f -exec shasum {} + | sort | shasum; }
a=$(h); (cd bench/distill/tools/$batch && python3 build.py >/dev/null 2>&1); b=$(h); [ "$a" = "$b" ] && echo deterministic || echo NONDETERMINISTIC
python3 - "$sub" <<'PY'
import json,glob,sys,collections
sub=sys.argv[1]; c=collections.Counter(); bad=[]; zh=multi=0; n=0
for p in sorted(glob.glob(f'bench/distill/v2.2/cases/*/*{sub}*/case.json')):
    d=json.load(open(p)); t=d['tags']; c[t.get('subtype')]+=1; n+=1
    s=json.dumps(d,ensure_ascii=False)
    if '"read_lines"' in s or t.get('tool_catalog')!='work-v3': bad.append(d['id'])
    zh+=any('一'<=ch<='鿿' for ch in d['turns'][0]['prompt']); multi+=len(d['turns'])>1
print(n, dict(c), f'zh {zh} multi {multi}', 'bad', bad)
PY
D=${TMPDIR:-/tmp}/dc-$batch; rm -rf $D; mkdir -p $D
for d in bench/distill/v2.2/cases/*/*$sub*; do sc=$(basename $(dirname $d)); mkdir -p $D/$sc; cp -R $d $D/$sc/; done
for t in bench/exam/cases bench/workbank/cases bench/workbank/cases-shelved bench/holdout/p13 bench/distill/v1/cases-shelved bench/bashprobe/cases bench/bashprobe/cases-b14 bench/bashprobe/reserve bench/weatherprobe/cases bench/weatherprobe/cases-b14 bench/weatherprobe/reserve; do
  r=$(local/bin/rwkv-lab-v3 corpus decontam --test $t --candidates $D 2>&1 | grep -E 'flagged|~'); echo "$r" | grep -q " 0 flagged" && [ $(echo "$r" | wc -l) -eq 1 ] || echo "DECONTAM $t: $r"
done
echo decontam-done
