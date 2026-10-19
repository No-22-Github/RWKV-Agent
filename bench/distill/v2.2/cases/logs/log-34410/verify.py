# DISTILL-CANARY-51242ded : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c4a01bf33e7d14951c46eb98ca061d7cc79d71ef21fc23b30950e452ff5506eb', "fixture changed"
import re, collections
h = [re.search(r'"[A-Z]+ (\S+) HTTP', l).group(1) for l in files['logs/cdn-origin-0917.log'].split('\n') if '" 404 ' in l]
m = collections.Counter(h).most_common(1)[0][0]
answers = [[m], len(h)]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
