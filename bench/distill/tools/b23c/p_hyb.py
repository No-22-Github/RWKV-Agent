"""35131-35142 (C1) and 35162-35166 (C0): computed edits."""
from common import c1, c0

BUILDERS = []


def reg(f):
    BUILDERS.append(f)
    return f


BUD_H1 = "科目,金额\n人力,820000\n市场费用,140000\n差旅,60000\n"
BUD_H2 = "科目,金额\n人力,860000\n市场费用,160000\n差旅,70000\n"
DISC = "# Discount rules\n- Standard customers: 5%\n- Partner customers: 12%\n- Staff orders: 20%\n"


@reg
def hyb_35131():
    files = {"budgets/2026-H1.csv": BUD_H1, "budgets/2026-H2.csv": BUD_H2}
    c1("hyb-35131", tt="tool_then_write", files=files, p1="把预算表里的市场费用加 15%。", stem="H2", calc=True,
       desc="Asks to raise marketing spend 15% with an H1 and an H2 budget table", ref="读两张预算表，都有市场费用，追问哪一张。")


@reg
def hyb_35132():
    files = {"pricing/discount-rules.md": DISC, "orders/PO-5530.txt": "PO-5530\nItems: 40 x fitting kit\nTotal: 4800.00\nDiscount: (none)\n"}
    c1("hyb-35132", tt="tool_then_write", files=files, p1="Apply the usual discount to the order total.", stem="partner", calc=True,
       desc="Asks for the usual discount when the rules depend on a customer type the order lacks", ref="read rules and order; customer type is not stated, ask.")


@reg
def hyb_35133():
    files = {"quotes/报价-A.txt": "报价 A\n金额：1200 USD\n折合人民币：（待填）\n", "rates/汇率-银行.txt": "USD/CNY 7.12（银行中间价，9 月 15 日）\n",
             "rates/汇率-内部结算.txt": "USD/CNY 7.05（财务内部结算价，本季度）\n"}
    c1("hyb-35133", tt="tool_then_write", files=files, p1="按汇率把报价单换算成人民币写进去。", stem="内部结算", calc=True,
       desc="Asks to convert a quote when a bank rate and an internal settlement rate disagree", ref="读到两个汇率，追问用哪个。")


@reg
def hyb_35134():
    files = {"invoices/INV-0412.md": "# INV-0412\nIssued: 2026-09-01\nDue: ____\n", "contracts/vendor-terms.md": "# Vendor terms\nPayment: Net 30 for standard orders; Net 15 for rush orders.\n"}
    c1("hyb-35134", tt="tool_then_write", files=files, p1="Fill the due date on the invoice, the payment terms are in the contract.", stem="rush", calc=True,
       desc="Asks for a due date when terms differ for rush orders and the invoice does not say which", ref="read both; ask whether this was a rush order.")


@reg
def hyb_35135():
    files = {"forms/签收单-0916.txt": "签收单\n日期：\n签收人：\n货物：打印机 2 台\n"}
    c1("hyb-35135", tt="tool_then_write", files=files, p1="把今天的日期和我的名字写到签收单上。", stem="签收单",
       desc="Asks to sign a receipt with 'my name' which the workspace does not hold", ref="读签收单，名字未知，追问。")


@reg
def hyb_35136():
    files = {"crm/customer-0192.md": "# Customer 0192\nShipping country: Canada\nBilling country: United States\n", "invoices/INV-7710.md": "# INV-7710\nCurrency: ______\nTotal: 2300\n"}
    c1("hyb-35136", tt="tool_then_write", files=files, p1="Make the invoice use the right currency for this customer.", stem="billing", calc=True,
       desc="Asks for the right invoice currency when the customer's shipping and billing countries differ", ref="read both; ask whether to follow billing or shipping country.")


@reg
def hyb_35137():
    files = {"sales/提成表-9月.csv": "销售,销售额,提成\n赵敏,50000,1500\n周凯,32000,960\n", "sales/说明.txt": "当前提成比例 3%。\n"}
    c1("hyb-35137", tt="tool_then_write", files=files, p1="按新的提成比例重新算提成表里的提成。", stem="3%", calc=True,
       desc="Asks to recompute commissions at a new rate that is not given", ref="读到当前 3%，新比例未给，追问。")


@reg
def hyb_35138():
    files = {"orders/order-7751.txt": "Order 7751\nSubtotal: 120.00\nDestination: (not set)\nShipping: TBD\nTotal: TBD\n",
             "shipping/rates-domestic.md": "Domestic flat rate: 6.50\n", "shipping/rates-international.md": "Canada: 24.50\nMexico: 21.00\nUK: 27.00\n"}
    c1("hyb-35138", tt="tool_then_write", files=files, p1="Update the shipping total in the order file.", p2="It's going to Canada.", stem="destination", calc=True,
       rules={"orders/order-7751.txt": ("has", ["Order 7751", "Subtotal: 120.00", "Shipping: 24.50", "Total: 144.50"])},
       desc="Asks for shipping when the order lacks a destination; turn 2 says Canada", ref="ask destination; then compute 120+24.50.")


@reg
def hyb_35139():
    files = {"invoices/inv-5120.txt": "发票 5120\n不含税金额：2000.00\n税额：\n价税合计：\n", "tax/rates.md": "# 税率\n- 标准 13%\n- 低税率 9%\n- 免税 0%\n"}
    c1("hyb-35139", tt="tool_then_write", files=files, p1="按新的税率重新算发票金额。", p2="按 9%，把税额和价税合计填上。", stem="低税率", calc=True,
       rules={"invoices/inv-5120.txt": ("has", ["发票 5120", "不含税金额：2000.00", "180", "2180"])},
       desc="Asks to recompute an invoice when three tax rates exist and none is named", ref="追问税率；答复后税额 180、合计 2180。")


@reg
def hyb_35140():
    files = {"schedule/launch-plan.md": "# Launch plan\n- Beta: 2026-09-28\n- Launch: 2026-10-12\n- Retro: 2026-10-26\n"}
    c1("hyb-35140", tt="tool_then_write", files=files, p1="Move the deadline in the schedule back by a week.", p2="Just the launch date.", stem="launch", calc=True,
       rules={"schedule/launch-plan.md": ("sub", "Launch: 2026-10-12", "Launch: 2026-10-19")},
       desc="Asks to push 'the deadline' by a week with three milestones in the plan", ref="ask which milestone; then change launch to 2026-10-19.")


@reg
def hyb_35141():
    files = {"inv/库存-0916.csv": "sku,在库,安全库存,补货\nA-100,12,20,\nB-200,45,30,\nC-300,3,10,\nD-400,8,8,\n"}
    c1("hyb-35141", tt="tool_then_write", files=files, p1="把库存表里低于安全库存的商品，补货数量算出来填上。", p2="补到安全库存的 1.5 倍，向上取整。", stem="安全库存", calc=True,
       rules={"inv/库存-0916.csv": ("has", ["A-100,12,20,18", "C-300,3,10,12", "B-200,45,30,", "D-400,8,8,"])},
       desc="Asks for restock quantities with no target level; turn 2 gives 1.5x safety stock", ref="追问补货目标；答复后 A 补 18、C 补 12。")


@reg
def hyb_35142():
    files = {"cost/estimate-sep.md": "# Monthly cost estimate\nServers: 6\nPer-server monthly: 140\nTotal: 840\n"}
    c1("hyb-35142", tt="tool_then_write", files=files, p1="Update the monthly cost estimate with the new server count.", p2="We're going from 6 to 9 servers.", stem="6", calc=True,
       rules={"cost/estimate-sep.md": ("has", ["Servers: 9", "Per-server monthly: 140", "Total: 1260"])},
       desc="Asks to update an estimate for a new server count that nobody states", ref="ask the count; then 9*140=1260.")


# ---- C0 ----
@reg
def hyb_35162():
    files = {"budgets/2026-H1.csv": BUD_H1, "budgets/2026-H2.csv": BUD_H2}
    c0("hyb-35162", tt="tool_then_write", files=files, calc=True, decoy=True,
       prompts=["把预算表 budgets/2026-H2.csv 里的市场费用加 15%。"],
       rules={"budgets/2026-H2.csv": ("has", ["科目,金额", "人力,860000", "市场费用,184000", "差旅,70000"])},
       desc="Names the H2 table for a 15 percent raise", ref="160000*1.15=184000 写回 H2。")


@reg
def hyb_35163():
    files = {"pricing/discount-rules.md": DISC, "orders/PO-5530.txt": "PO-5530\nItems: 40 x fitting kit\nTotal: 4800.00\nDiscount: (none)\n"}
    c0("hyb-35163", tt="tool_then_write", files=files, calc=True,
       prompts=["Apply the Partner discount to the order total in PO-5530 and write the discounted total on the Discount line."],
       rules={"orders/PO-5530.txt": ("has", ["PO-5530", "4224"])},
       desc="Names the Partner discount explicitly", ref="4800*0.88=4224.")


@reg
def hyb_35164():
    files = {"quotes/报价-A.txt": "报价 A\n金额：1200 USD\n折合人民币：（待填）\n", "rates/汇率-银行.txt": "USD/CNY 7.12（银行中间价，9 月 15 日）\n",
             "rates/汇率-内部结算.txt": "USD/CNY 7.05（财务内部结算价，本季度）\n"}
    c0("hyb-35164", tt="tool_then_write", files=files, calc=True, decoy=True,
       prompts=["按内部结算汇率把报价单换算成人民币，填到折合人民币那一行。"],
       rules={"quotes/报价-A.txt": ("has", ["报价 A", "金额：1200 USD", "8460"])},
       desc="Names the settlement rate", ref="1200*7.05=8460。")


@reg
def hyb_35165():
    files = {"invoices/INV-0412.md": "# INV-0412\nIssued: 2026-09-01\nDue: ____\n", "contracts/vendor-terms.md": "# Vendor terms\nPayment: Net 30.\nLate fee: 1.5% per month.\n"}
    c0("hyb-35165", tt="tool_then_write", files=files, calc=True,
       prompts=["Fill the due date on INV-0412 using the payment terms in the vendor contract.", "Now add a line to the invoice saying the late fee, as in the contract."],
       rules={"invoices/INV-0412.md": ("has", ["# INV-0412", "Issued: 2026-09-01", "2026-10-01", "1.5%"])},
       desc="Single payment term in the contract, then a follow-up line", ref="due 2026-10-01; second turn adds a late fee line.")


@reg
def hyb_35166():
    files = {"schedule/发布计划.md": "# 发布计划\n- 发布日期：2026-10-12\n"}
    c0("hyb-35166", tt="tool_then_write", files=files, calc=True, prompts=["Push the release date in the plan back by a week."],
       rules={"schedule/发布计划.md": ("sub", "2026-10-12", "2026-10-19")},
       desc="A plan with a single date to move", ref="只有一个日期，改成 2026-10-19。")
