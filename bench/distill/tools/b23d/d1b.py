"""b23d D1 part b: 3-turn chains, ids 35213-35224."""
from common import mk, T, L

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c13():
    f = "docs/saffron-pricing.md"
    files = {f: L("| Plan | Price per seat per month |", "| --- | --- |", "| Starter | 9 |", "| Team | 24 |", "| Enterprise | 60 |")}
    mk("hyb-35213", sub="D1", tt="undo", trap="TR-CLAIM", desc="Raise one price, then revert it and raise a different one instead", files=files,
       turns=[T("How much is the Team plan per seat in docs/saffron-pricing.md?", inc=["24"]),
              T("Raise it to 29 and confirm.", inc=["29"]),
              T("On reflection, leave Team alone: change it back, and raise Enterprise by 10% instead. Which prices did you touch, and what are they now?", inc=["24", "66"])],
       edits=[(f, "| Enterprise | 60 |", "| Enterprise | 66 |")], vals=["29"], must=["read_file", "replace_lines", "write_file", "calculator"], rc=5)


@reg
def c14():
    a, b, c = "部署/订单服务.env", "部署/支付服务.env", "部署/库存服务.env"
    files = {a: L("SERVICE=order", "PORT=8443", "LOG_LEVEL=info"), b: L("SERVICE=pay", "PORT=8444", "LOG_LEVEL=warn"), c: L("SERVICE=stock", "PORT=8445", "LOG_LEVEL=info")}
    mk("hyb-35214", sub="D1", tt="multi", trap="TR-MULTISRC", desc="Find the file by a port number, change it, then check the others and recall the old port", files=files,
       turns=[T("部署目录里哪个服务用的是 8443 端口？", inc=["订单服务"]),
              T("把它改成 9443，改完说一下文件名和新端口。", inc=["订单服务.env", "9443"]),
              T("再看看有没有别的服务也用了 9443，顺便告诉我支付服务现在用哪个端口，以及你刚改的那个服务原来是多少。", inc=["8444", "8443"])],
       edits=[(a, "PORT=8443", "PORT=9443")], must=["list_files", "search_text", "read_file", "replace_lines", "write_file"], rc=6)


@reg
def c15():
    f = "release/v3.2-checklist.md"
    files = {f: L("- [x] Freeze main", "- [ ] Update changelog", "- [ ] Run smoke tests", "- [ ] Tag release", "- [ ] Publish notes")}
    mk("hyb-35215", sub="D1", tt="comp", trap="TR-CLAIM", desc="Count open checklist items, tick two, append one, compare counts", files=files,
       turns=[T("How many items in release/v3.2-checklist.md are still unchecked?", inc=["4"]),
              T("Tick off 'Update changelog' and 'Tag release', then tell me what's left open.", inc=["Run smoke tests", "Publish notes"]),
              T("Add a new unchecked item 'Notify support team' at the end. How many items were open when we started, and how many are open now?", inc=["4", "3"])],
       edits=[(f, "- [ ] Update changelog", "- [x] Update changelog"), (f, "- [ ] Tag release", "- [x] Tag release")], adds=[(f, "- [ ] Notify support team\n")],
       must=["read_file", "replace_lines", "append_file", "write_file"], rc=5, dep="4 open at the start")


@reg
def c16():
    f = "配置/直播间-弹幕.json"
    files = {f: '{\n  "room": 1042,\n  "delay_ms": 150,\n  "max_per_sec": 20\n}\n'}
    mk("hyb-35216", sub="D1", tt="undo", trap="TR-CLAIM", desc="A staged edit is rejected by the user, then a different edit is requested; recall the rejected target", files=files,
       turns=[T("把 配置/直播间-弹幕.json 里的 delay_ms 改成 300。"),
              T("我没保存这个改动。现在文件里 delay_ms 是多少？", inc=["150"], review="reject"),
              T("好，这次改 max_per_sec 到 35，delay_ms 保持原样。然后告诉我第一次让你改的 delay_ms 目标值，以及现在两项各是多少。", inc=["300", "150", "35"])],
       edits=[(f, '"max_per_sec": 20', '"max_per_sec": 35')], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c17():
    log, out = "logs/payments-edge-1002.log", "logs/failed-orders-1002.txt"
    files = {log: L("10:01 INFO charge ok order=A-1001 ms=210", "10:02 INFO charge ok order=A-1002 ms=190", "10:05 ERROR charge declined order=A-1003 code=51",
                    "10:09 ERROR gateway timeout order=A-1004 ms=5000", "10:14 INFO charge ok order=A-1005 ms=240")}
    mk("hyb-35217", sub="D1", tt="write", trap="TR-CLAIM", desc="Extract failed order ids into a new file, then remove one and recall its error code", files=files,
       turns=[T("How many ERROR lines are in logs/payments-edge-1002.log, and which orders do they involve?", inc=["A-1003", "A-1004"]),
              T("Write those failed order ids, one per line and nothing else, to logs/failed-orders-1002.txt."),
              T("Order A-1003 was retried successfully by the customer. Remove it from that file, then tell me what is left in the file and what error code A-1003 originally failed with.", inc=["A-1004", "51"])],
       adds=[(out, "A-1004\n")], exact=[out], must=["read_file", "write_file", "replace_lines", "search_text"], rc=5)


@reg
def c18():
    f = "文档/周会安排.txt"
    files = {f: L("周一 09:30 产品评审（会议室A）", "周三 14:00 技术分享（会议室B）", "周五 10:00 复盘（会议室A）")}
    mk("hyb-35218", sub="D1", tt="multi", trap="TR-CLAIM", desc="Move a meeting twice, then ask for the full schedule and the original day", files=files,
       turns=[T("周三的会是什么，在哪个会议室？", inc=["技术分享", "会议室B"]),
              T("技术分享挪到周四同一时间，会议室不变。告诉我改完这行。", inc=["周四"]),
              T("周四会议室B被占了，换成会议室C。然后把这周的安排完整念一遍给我，另外提醒我技术分享最初是周几。", inc=["周三", "产品评审", "复盘", "会议室C"])],
       edits=[(f, "周三 14:00 技术分享（会议室B）", "周四 14:00 技术分享（会议室C）")], must=["read_file", "replace_lines", "write_file"], rc=4)


@reg
def c19():
    f = "billing/inv-7731.txt"
    files = {f: L("Item: Hosting 3 mo x 120 = 360", "Item: Support 1 x 450 = 450", "Item: Domain 2 x 15 = 30", "Tax rate: 8%")}
    mk("hyb-35219", sub="D1", tt="comp", trap="TR-CLAIM", desc="Subtotal, fix the tax rate, drop a line, compare the new total to the original one", files=files,
       turns=[T("What's the subtotal on billing/inv-7731.txt before tax?", inc=["840"]),
              T("The tax rate should be 10%, not 8%. Fix that and tell me the total with tax.", inc=["924"]),
              T("Also drop the Domain line entirely. Give me the new total with tax and compare it with the very first total (the one at 8% tax).", inc=["891", "907.2"])],
       edits=[(f, "Tax rate: 8%", "Tax rate: 10%"), (f, "Item: Domain 2 x 15 = 30\n", "")], vals=["924", "891", "907.2"],
       must=["read_file", "replace_lines", "write_file", "calculator"], rc=6, dep="original total 840*1.08 = 907.2 needs the turn-1 subtotal and old rate")


@reg
def c20():
    f, out = "数据/门店日营业额.csv", "数据/海淀店-合计.txt"
    files = {f: L("门店,日期,营业额", "朝阳店,10-01,12800", "海淀店,10-01,9600", "朝阳店,10-02,11200", "海淀店,10-02,10400")}
    mk("hyb-35220", sub="D1", tt="write", trap="TR-CLAIM", desc="Sum one store, write it to a new file, append a second store, compare", files=files,
       turns=[T("海淀店这两天合计营业额多少？", any=["20000", "20,000", "2万"]),
              T("新建 数据/海淀店-合计.txt，里面就一行：“海淀店合计：金额”。")
              ,
              T("朝阳店也一样算，按同样格式追加一行到这个文件末尾。然后告诉我哪家店更高、高出多少。", inc=["朝阳"], any=["4000", "4,000"])],
       writes={out: ["海淀店合计", "朝阳店合计"]}, vals=["4000"], must=["read_file", "write_file", "append_file", "calculator", "bash"], rc=5, dep="Haidian total from turn 1 vs Chaoyang 24000")


@reg
def c21():
    f = "flags/checkout-rollout.yaml"
    files = {f: L("new_checkout: false", "express_pay: true", "gift_cards: false")}
    mk("hyb-35221", sub="D1", tt="undo", trap="TR-CLAIM", desc="Turn a flag on, revert it, enable another, recall the first request", files=files,
       turns=[T("Which flags are on in flags/checkout-rollout.yaml?", inc=["express_pay"]),
              T("Turn on new_checkout.", inc=["new_checkout"]),
              T("That was premature: turn it back off and enable gift_cards instead. Then tell me which flags are on now, and which one I asked you to turn on first.", inc=["express_pay", "gift_cards", "new_checkout"])],
       edits=[(f, "gift_cards: false", "gift_cards: true")], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c22():
    f = "文档/供应商联系人.txt"
    files = {f: L("华达包装 | 王建国 | 13800001111", "顺丰仓 | 赵磊 | 13700003333", "联盛纸业 | 钱敏 | 13600004444")}
    mk("hyb-35222", sub="D1", tt="multi", trap="TR-CLAIM", desc="Update a phone number and a contact name, then recall the original phone", files=files,
       turns=[T("华达包装的联系人是谁、电话多少？", inc=["王建国", "13800001111"]),
              T("电话换成 13900002222，告诉我改后的整行。", inc=["13900002222"]),
              T("再把顺丰仓的联系人改成李娜。然后告诉我华达包装原来的电话是多少。", inc=["13800001111"])],
       edits=[(f, "13800001111", "13900002222"), (f, "顺丰仓 | 赵磊", "顺丰仓 | 李娜")], must=["read_file", "replace_lines", "write_file"], rc=4)


@reg
def c23():
    f = "src/retry_policy.py"
    files = {f: L("MAX_ATTEMPTS = 3", "BACKOFF_BASE_S = 0.5", "JITTER = True")}
    mk("hyb-35223", sub="D1", tt="comp", trap="TR-CLAIM", desc="Two constants edited, accepted by the user, then a worst-case wait computed from the file read back", files=files,
       turns=[T("What backoff base and attempt count does src/retry_policy.py use?", inc=["0.5", "3"]),
              T("Raise MAX_ATTEMPTS to 6 and halve BACKOFF_BASE_S. Tell me the two new values.", inc=["6", "0.25"]),
              T("I accepted both edits. Read the file back to check, then work out the worst-case total wait if all 6 attempts fail, with waits between attempts doubling from the base each time.", inc=["7.75"], review="accept")],
       edits=[(f, "MAX_ATTEMPTS = 3", "MAX_ATTEMPTS = 6"), (f, "BACKOFF_BASE_S = 0.5", "BACKOFF_BASE_S = 0.25")], vals=["7.75"],
       must=["read_file", "replace_lines", "write_file", "calculator"], rc=5, dep="0.25*(1+2+4+8+16)=7.75")


@reg
def c24():
    a, b, out = "文档/需求-登录.txt", "文档/需求-支付.txt", "文档/排期.md"
    files = {a: L("标题：短信登录", "优先级：P1", "负责人：韩雪"), b: L("标题：分期支付", "优先级：P0", "负责人：罗斌")}
    mk("hyb-35224", sub="D1", tt="write", trap="TR-CLAIM", desc="Order two requirements by priority into a new file, then re-rank after a priority change", files=files,
       turns=[T("文档 目录下的 需求-登录.txt 和 需求-支付.txt，优先级各是什么？", inc=["P1", "P0"]),
              T("按优先级从高到低，把两项需求的标题和负责人写进 文档/排期.md，一行一项，格式：标题（负责人）。"),
              T("产品把登录升成 P0 了，登录排到支付前面，把排期改好。然后告诉我登录原来的优先级和负责人是谁。", inc=["P1", "韩雪"])],
       adds=[(out, L("短信登录（韩雪）", "分期支付（罗斌）"))], exact=[out], must=["read_file", "write_file", "replace_lines"], rc=5)
