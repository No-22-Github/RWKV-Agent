from common import T, make

C = "code_help"


def build():
    make("nt-33115", sub="code", tt=C, family="x", desc="Explain a Python dedupe function pasted in prompt",
         turns=[T("这段 Python 是干什么的？一两句话说清就行：\n```python\ndef uniq_keep_order(items):\n    seen = set()\n    out = []\n    for x in items:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out\n```",
                  any_=["去重", "重复", "duplicate", "unique"], fmt=["zh"])],
         notes={"ref": "Removes duplicates keeping order.", "why": "Keyword check."})
    make("nt-33116", sub="code", tt=C, family="x", desc="Write a small JS function",
         turns=[T("写一个 JavaScript 函数 clampPercent(n)，把数字限制在 0 到 100 之间，小于 0 返回 0，大于 100 返回 100。直接给代码。",
                  inc=["clampPercent", "100"], any_=["Math.min", "Math.max", "return", "?"]),
                T("再给它加一段 JSDoc 注释。", inc=["clampPercent"], any_=["@param", "/**"])],
         notes={"ref": "function clampPercent", "why": "Identifier check."})
    make("nt-33117", sub="code", tt=C, family="x", desc="Find the off-by-one bug in pasted loop",
         turns=[T("下面这段循环想打印 1 到 10，但只打印到 9，哪里错了？\n```python\nfor i in range(1, 10):\n    print(i)\n```",
                  inc=["range"], any_=["11", "range(1, 11)", "range(1,11)"], fmt=["zh"])],
         notes={"ref": "Use range(1, 11).", "why": "11 appears."})
    make("nt-33118", sub="code", tt=C, family="x", desc="Explain SQL query pasted",
         turns=[T("帮我看看这条 SQL 是什么意思：\n```sql\nSELECT dept, COUNT(*) AS n FROM staff WHERE active = 1 GROUP BY dept HAVING COUNT(*) > 5 ORDER BY n DESC;\n```",
                  any_=["分组", "每个部门", "按部门", "各部门"], inc=["HAVING"], fmt=["zh"])],
         notes={"ref": "Departments with more than 5 active staff, sorted desc.", "why": "HAVING & grouping."})
    make("nt-33119", sub="code", tt=C, family="x", desc="Write a bash one-liner",
         turns=[T("写一条 shell 命令，统计当前目录下 .log 文件一共有多少个。只要命令，加一句话解释。",
                  any_=["find", "ls"], inc=["wc -l"])],
         notes={"ref": "find . -name '*.log' | wc -l", "why": "wc -l present."})
    make("nt-33120", sub="code", tt=C, family="x", desc="Fix Python mutable default argument",
         turns=[T("这个函数连续调用两次，第二次会带着第一次的内容，为什么？怎么改？\n```python\ndef add_tag(tag, tags=[]):\n    tags.append(tag)\n    return tags\n```",
                  inc=["None"], any_=["默认", "可变", "mutable", "default"], fmt=["zh"])],
         notes={"ref": "Mutable default; use None.", "why": "None in fix."})
    make("nt-33121", sub="code", tt=C, family="x", desc="Two-turn: write then translate comments",
         turns=[T("Write a Python function is_leap(year) that returns True for leap years.", inc=["is_leap", "400"], token=True),
                T("请把代码里的注释换成中文，再说一下 1900 年是不是闰年。", inc=["1900"], any_=["不是", "否"], fmt=["zh"])],
         notes={"ref": "Leap rule; 1900 not leap.", "why": "Rule uses 400."})
    make("nt-33122", sub="code", tt=C, family="x", desc="Explain a regex",
         turns=[T("这个正则 `^1[3-9]\\d{9}$` 匹配什么？",
                  any_=["手机号", "手机", "11位", "11 位", "11 digits", "phone"], fmt=["zh"])],
         notes={"ref": "Chinese mobile number.", "why": "Keyword."})
