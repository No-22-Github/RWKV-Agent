# DISTILL-CANARY-a3504c4b : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'wuling-coffee.com/mf300' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'coffeeclub.cn/review/mf300' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '1.8' in sec["content"]
files = case["files"]
assert files['采购/茶水间设备.csv'].splitlines()[0] == '品名,型号,数量,金额'
assert '咖啡机,雾岭 MF-300,2,6400' in files['采购/茶水间设备.csv'].splitlines()

print(json.dumps({"expected_string": '1.8'}, ensure_ascii=False))
