"""31349-31362: ambiguous document and table questions."""
from p2 import clarify, reg

R = ("list_files", "read_file", "search_text")
RX = 'import re\nans = re.search(%r, case["files"][%r]).group(1)'


@reg
def c31349():
    files = {"minutes/0910-产品.md": "# 产品周会 9/10\n决定：推迟灰度到下周。预算 120 万。\n", "minutes/0912-财务.md": "# 财务例会 9/12\n决定：Q4 预算总额 380 万，冻结差旅。\n",
             "minutes/0915-运营.md": "# 运营例会 9/15\n决定：双十一活动提前一周。预算 75 万。\n"}
    clarify("nt-31349", scen="nt", task_type="ambiguous_request", files=files, p1="把那份会议纪要总结一下。", p2="财务那份。", stems=["财务", "运营"], must=R, edit=False,
            calc=RX % (r"总额 (\d+) 万", "minutes/0912-财务.md"), ans2="380", desc="Asks to summarise 'that meeting note' with three notes and no hint", ref="三份纪要，追问哪一份；答财务后总结，含预算 380 万。")


@reg
def c31350():
    files = {"contracts/vendor-a.md": "# Vendor A agreement\nTerm: 12 months. Fee: 4,000 per month.\n", "contracts/vendor-b.md": "# Vendor B agreement\nTerm: 18 months. Fee: 3,500 per month.\n"}
    clarify("nt-31350", scen="nt", task_type="ambiguous_request", files=files, p1="Summarise the contract for me.", p2="Vendor B.", stems=["vendor-a", "vendor-b"], must=R, edit=False,
            calc=RX % (r"Term: (\d+) months", "contracts/vendor-b.md"), ans2="18", desc="Asks to summarise 'the contract' with two vendor agreements", ref="两份合同，追问哪一家；B 的期限 18 个月。")


@reg
def c31351():
    files = {"quotes/报价-甲公司.md": "# 甲公司报价\n总价 48000 元，含安装。\n", "quotes/报价-乙公司.md": "# 乙公司报价\n总价 52500 元，含安装与三年维保。\n"}
    clarify("nt-31351", scen="nt", task_type="ambiguous_request", files=files, p1="那份报价多少钱？", stems=["甲公司", "乙公司"], must=R, edit=False,
            excl1=["48000 元", "52500 元"], desc="Asks the price of 'that quote' when two company quotes exist", ref="两份报价，追问是哪家；不能挑一份直接报价。")


@reg
def c31352():
    files = {"proposals/alpha.md": "# Proposal Alpha\nDeadline: 2026-10-03\nBudget: 90k\n", "proposals/beta.md": "# Proposal Beta\nDeadline: 2026-11-21\nBudget: 140k\n"}
    clarify("nt-31352", scen="nt", task_type="ambiguous_request", files=files, p1="What's the deadline in the proposal?", stems=["alpha", "beta"], must=R, edit=False,
            excl1=["2026-10-03", "2026-11-21"], desc="Asks for 'the proposal' deadline with alpha and beta proposals", ref="两份提案，追问哪一份，不直接给日期。")


@reg
def c31353():
    files = {"resumes/张三.md": "# 张三\n工作年限：3 年\n", "resumes/李四.md": "# 李四\n工作年限：12 年\n", "resumes/王五.md": "# 王五\n工作年限：9 年\n"}
    clarify("nt-31353", scen="nt", task_type="ambiguous_request", files=files, p1="帮我看看简历里的工作年限。", p2="李四的。", stems=["张三", "李四"], must=R, edit=False,
            calc=RX % (r"工作年限：(\d+) 年", "resumes/李四.md"), ans2="12", desc="Asks for work years from 'the resume' with three resumes", ref="三份简历，追问是谁的；李四 12 年。")


@reg
def c31354():
    files = {"manuals/router.md": "# Router manual\nReset: hold the reset pin for 5 seconds.\n", "manuals/camera.md": "# Camera manual\nReset: hold the button for 10 seconds.\n"}
    clarify("nt-31354", scen="nt", task_type="ambiguous_request", files=files, p1="What does the manual say about resetting?", p2="The camera one.", stems=["router", "camera"], must=R, edit=False,
            calc=RX % (r"for (\d+) seconds", "manuals/camera.md"), ans2="10", desc="Asks what 'the manual' says about reset with router and camera manuals", ref="两份手册，追问哪个设备；camera 为 10 秒。")


@reg
def c31355():
    files = {"projects/A-项目.md": "# A 项目\n负责人：陈磊\n状态：进行中\n", "projects/B-项目.md": "# B 项目\n负责人：周敏\n状态：已暂停\n"}
    clarify("nt-31355", scen="nt", task_type="ambiguous_request", files=files, p1="那个项目的负责人是谁？", stems=["A-项目", "B-项目"], must=R, edit=False,
            excl1=["陈磊", "周敏"], desc="Asks who leads 'that project' with two project pages", ref="两个项目，追问是哪个。")


@reg
def c31356():
    files = {"reviews/review-2026-09-08.md": "# Review 9/8\nAttendees: Tom, Lena\n", "reviews/review-2026-09-15.md": "# Review 9/15\nAttendees: Priya, Tom, Marc\n"}
    clarify("nt-31356", scen="nt", task_type="ambiguous_request", files=files, p1="Who attended the review?", p2="The one on the 15th.", stems=["09-08", "09-15"], must=R, edit=False,
            calc=RX % (r"Attendees: (Priya)", "reviews/review-2026-09-15.md"), ans2="Priya", desc="Asks who attended 'the review' with two dated review notes", ref="两次评审，追问哪一次；15 日有 Priya。")


CSV_SUM = 'import csv, io\nans = str(sum(int(r[%r]) for r in csv.DictReader(io.StringIO(case["files"][%r]))))'


@reg
def c31357():
    files = {"sales/sales-2026-07.csv": "day,amount\n1,1200\n2,800\n3,950\n", "sales/sales-2026-08.csv": "day,amount\n1,1500\n2,700\n3,1100\n4,640\n"}
    clarify("tab-31357", scen="tab", task_type="aggregate", files=files, p1="汇总一下销售额。", p2="8 月的。", stems=["2026-07", "2026-08"], must=R, edit=False,
            calc=CSV_SUM % ("amount", "sales/sales-2026-08.csv"), ans2="3940", desc="Asks to total sales with July and August files and no month given", ref="两个月份文件，追问哪个月；8 月合计 3940。")


@reg
def c31358():
    files = {"finance/expenses-q2.csv": "item,cost\nlaptops,5400\ntravel,1900\n", "finance/expenses-q3.csv": "item,cost\nlaptops,2100\ntravel,3300\ntraining,1250\n"}
    clarify("tab-31358", scen="tab", task_type="aggregate", files=files, p1="Total the expenses.", p2="Q3.", stems=["q2", "q3"], must=R, edit=False,
            calc=CSV_SUM % ("cost", "finance/expenses-q3.csv"), ans2="6650", desc="Asks to total expenses with Q2 and Q3 files", ref="两个季度，追问；Q3 合计 6650。")


@reg
def c31359():
    files = {"orders/orders-online.csv": "id,amount\n1,88\n2,120\n3,64\n", "orders/orders-store.csv": "id,amount\n1,210\n2,175\n"}
    clarify("tab-31359", scen="tab", task_type="aggregate", files=files, p1="平均客单价是多少？", stems=["online", "store"], must=R, edit=False,
            excl1=["90.67", "192.5"], desc="Asks for average order value with online and in-store order files", ref="线上与门店两份，追问口径（哪份或合并）。")


@reg
def c31360():
    files = {"hr/staff-eng.csv": "name,salary\nAda,21000\nBen,18500\n", "hr/staff-ops.csv": "name,salary\nCara,15200\nDan,16800\n"}
    clarify("tab-31360", scen="tab", task_type="aggregate", files=files, p1="What's the highest salary?", stems=["staff-eng", "staff-ops"], must=R, edit=False,
            desc="Asks for the highest salary with engineering and operations staff files", ref="两个部门的表，追问范围（某部门还是全公司）。")


@reg
def c31361():
    files = {"stock/warehouse-east.csv": "sku,qty\nA1,120\nB2,45\n", "stock/warehouse-west.csv": "sku,qty\nA1,80\nB2,30\nC3,17\n"}
    clarify("tab-31361", scen="tab", task_type="aggregate", files=files, p1="库存一共多少件？", p2="西仓的。", stems=["east", "west"], must=R, edit=False,
            calc=CSV_SUM % ("qty", "stock/warehouse-west.csv"), ans2="127", desc="Asks for total stock with east and west warehouse files", ref="两个仓库，追问；西仓合计 127。")


@reg
def c31362():
    files = {"refunds/refunds-0914.csv": "id,amount\n1,30\n2,45\n", "refunds/refunds-0915.csv": "id,amount\n1,60\n2,25\n3,90\n"}
    clarify("tab-31362", scen="tab", task_type="aggregate", files=files, p1="Sum the refunds.", stems=["0914", "0915"], must=R, edit=False,
            desc="Asks to sum refunds with two daily refund files and no date", ref="两天文件，追问哪天或合计。")
