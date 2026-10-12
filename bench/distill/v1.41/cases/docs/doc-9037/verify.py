# DISTILL-CANARY-2d9a4ae8 : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("# 项目文档")
assert case["files"]["文档/接口/v1/README.md"] == "# 接口 v1" + chr(10) + chr(10) + "签名算法: MD5" + chr(10)
assert case["files"]["文档/接口/v2/示例.json"] == '{"sign": "..."}' + chr(10)
text = case["files"]["文档/接口/v2/README.md"]
assert text.startswith("# 接口 v2")
print(json.dumps({"expected_string": re.search(r"签名算法: (\S+)", text).group(1)}))
