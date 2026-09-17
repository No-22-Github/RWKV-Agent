# WORKBANK-CANARY-3d7a91e4 : bank artifact, excluded from training corpora
import json, re
case = json.load(open('case.json'))
prompt = case['turns'][0]['prompt']
m = re.search(r'([0-9.]+) MiB per second', prompt)
rate = float(m.group(1))
print(json.dumps({'expected_number': rate * 3600}))
