"""33448-33454: partial undo."""
from p0 import undo, reg
from u1 import W, WB, eq


@reg
def c33448():
    o = "alpha=1\nbeta=2\ngamma=3\n"
    undo("hyb-33448", files={"params.txt": o}, p1="把 params.txt 里三个参数的值都翻倍。", p2="beta 不该改，把它改回去，另外两个保留。", rules=eq("params.txt", "alpha=2\nbeta=2\ngamma=6\n"),
         chk1=["alpha"], must=W, desc="Doubles three parameters, then asks to restore only beta", ref="三个值翻倍后用户要求仅 beta 恢复为 2，终态 2/2/6。")


@reg
def c33449():
    hdr = lambda n: "// Copyright 2025 Northwind Ltd.\n// file: %s\n" % n
    files = {"src/a.go": hdr("a.go") + "package a\n", "src/b.go": hdr("b.go") + "package b\n", "vendor/lib.go": hdr("lib.go") + "package lib\n"}
    final = dict((p, ("sub", "2025", "2026")) for p in ["src/a.go", "src/b.go"])
    undo("hyb-33449", files=files, p1="Change the copyright year from 2025 to 2026 in all three Go files.", p2="Revert the one in vendor/, we don't own that code. Keep the other two.", rules=final,
         chk1=["2026"], must=WB, desc="Updates a copyright year in three files, then asks to revert only the vendored one", ref="Update all three, then restore vendor/lib.go only.")


@reg
def c33450():
    o = "- TODO 写接口文档\n- TODO 补单元测试\n- TODO 配置 CI\n- TODO 发布 0.1\n"
    f = "- DONE 写接口文档\n- TODO 补单元测试\n- DONE 配置 CI\n- DONE 发布 0.1\n"
    undo("hyb-33450", files={"todo.md": o}, p1="把 todo.md 里所有 TODO 标记改成 DONE。", p2="第二条其实还没做完，把它改回 TODO，其他保持 DONE。", rules=eq("todo.md", f),
         chk1=["DONE"], must=W, desc="Marks all four items done, then asks to reopen only the second", ref="全部改 DONE；用户要求第二条恢复 TODO。")


@reg
def c33451():
    o = "GET /health\nGET /users\nPOST /users\nGET /orders\n"
    f = "GET /v2/users\nPOST /v2/users\nGET /v2/orders\n"
    f = "GET /health\n" + f
    undo("hyb-33451", files={"routes.txt": o}, p1="Prefix every path in routes.txt with /v2.", p2="Undo it for /health only; the others stay prefixed.", rules=eq("routes.txt", f),
         chk1=["/v2"], must=W, desc="Prefixes every route with /v2, then asks to undo it for /health only", ref="Prefix all four, then restore /health.")


@reg
def c33452():
    mk = lambda n: "name: %s\nlog_level: debug\n" % n
    files = {"svc/auth.yaml": mk("auth"), "svc/pay.yaml": mk("pay"), "svc/search.yaml": mk("search")}
    final = {"svc/auth.yaml": ("sub", "debug", "info"), "svc/search.yaml": ("sub", "debug", "info")}
    undo("hyb-33452", files=files, p1="三个服务的日志级别都从 debug 降到 info。", p2="支付服务还要排查问题，把它改回 debug，其他两个维持 info。", rules=final,
         chk1=["info"], must=W, desc="Lowers log level in three services, then asks to restore debug for the payment service only", ref="三处 debug→info；用户要求 pay 恢复 debug。")


@reg
def c33453():
    o = "mango\napple\nbanana\napple\ncherry\nbanana\napple\n"
    undo("hyb-33453", files={"names.txt": o}, p1="Sort the lines in names.txt alphabetically and remove duplicates.", p2="Undo the dedupe but keep the sort.",
         rules=eq("names.txt", "apple\napple\napple\nbanana\nbanana\ncherry\nmango\n"), chk1=["cherry"], must=W,
         desc="Sorts and dedupes a list, then asks to undo only the dedupe", ref="排序去重后，用户要求保留排序、恢复重复行：3 个 apple、2 个 banana。")


@reg
def c33454():
    o = "拿铁 28\n美式 22\n蛋糕 36\n三明治 32\n"
    f = "拿铁 31\n美式 24\n蛋糕 36\n三明治 32\n"
    undo("hyb-33454", files={"menu.md": o}, p1="把 menu.md 里所有价格上调 10%，四舍五入到整数。", p2="只撤销食物的涨价（蛋糕、三明治），饮料保持新价。", rules=eq("menu.md", f),
         chk1=["31"], must=W, desc="Raises all menu prices 10%, then asks to undo only the food items", ref="28→31、22→24、36→40、32→35；用户要求食物恢复 36/32。")
