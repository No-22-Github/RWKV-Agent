# DISTILL-CANARY-686ffa06 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'docs.songling-auth.cn/5.x/tokens' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'segmentfault-like.cn/q/songling-token' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '900' in sec["content"]
files = case["files"]
assert files['部署/清单.csv'].splitlines()[0] == '组件,版本,环境'
assert '松岭认证,5.2.0,生产' in files['部署/清单.csv'].splitlines()

print(json.dumps({"expected_string": '900'}, ensure_ascii=False))
