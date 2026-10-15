# EXAM-CANARY-c27e913b : sol pilot case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
prompt=case["turns"][0]["prompt"]
a,b=re.search(r"我们有(.+?)和(.+?)两套环境",prompt).groups()
forms=["哪个环境","哪套环境","哪一套环境","什么环境","哪种环境","哪边","确认环境","指定环境","明确环境"]
forms += [f"{x}{sep}{y}" for x,y in ((a,b),(b,a)) for sep in ("还是","或是","或","/","环境还是","环境，还是","环境或","环境，或")]
forms += ["dev or prod","prod or dev","dev 还是 prod","prod 还是 dev","development or production","production or development","which environment","Which environment"]
print(json.dumps({"expected_contains_any":forms},ensure_ascii=False))
