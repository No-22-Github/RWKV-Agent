from common import T, make

C = "code_help"


def build():
    make("nt-33123", sub="code", tt=C, family="x", desc="Write a Python function to count words",
         turns=[T("用 Python 写个函数 count_words(text)，返回每个单词出现的次数（用字典），按空格切分、统一小写。",
                  inc=["count_words"], any_=["lower()", "Counter", "split"])],
         notes={"ref": "dict counting", "why": "identifier"})
    make("nt-33124", sub="code", tt=C, family="x", desc="Explain git command",
         turns=[T("`git reset --soft HEAD~1` 做了什么？会丢掉我改的代码吗？",
                  any_=["保留", "不会丢", "暂存", "staged", "keep"], fmt=["zh"])],
         notes={"ref": "Undoes commit, keeps changes staged.", "why": "keyword"})
    make("nt-33125", sub="code", tt=C, family="x", desc="Explain a JS closure counter",
         turns=[T("Explain in two sentences what this does:\n```js\nfunction makeCounter() {\n  let c = 0;\n  return () => ++c;\n}\nconst next = makeCounter();\nnext(); next();\n```\nWhat does the last call return?",
                  inc=["2"], any_=["closure", "Closure"], token=True, fmt=["en"])],
         notes={"ref": "Closure; returns 2.", "why": "token 2"})
    make("nt-33126", sub="code", tt=C, family="x", desc="Convert loop to list comprehension",
         turns=[T("把这段改成一行列表推导式：\n```python\nres = []\nfor n in nums:\n    if n % 2 == 0:\n        res.append(n * n)\n```",
                  inc=["for n in nums", "n * n"], any_=["if n % 2 == 0", "if n%2==0", "n % 2 == 0"])],
         notes={"ref": "res = [n*n for n in nums if n%2==0]", "why": "tokens"})
    make("nt-33127", sub="code", tt=C, family="x", desc="Explain Go defer order",
         turns=[T("下面这段 Go 代码的输出顺序是什么？\n```go\nfunc main() {\n    defer fmt.Println(\"A\")\n    defer fmt.Println(\"B\")\n    fmt.Println(\"C\")\n}\n```",
                  inc=["C", "B", "A"], any_=["后进先出", "LIFO", "倒序", "逆序"], fmt=["zh"], token=True)],
         notes={"ref": "C B A", "why": "LIFO"})
    make("nt-33128", sub="code", tt=C, family="x", desc="Write CSS for centred box then shorter",
         turns=[T("写一段 CSS，让 .card 在页面里水平垂直居中，用 flex 实现，给出父容器的样式。",
                  any_=["justify-content", "place-items", "align-items"], inc=["center"]),
                T("不用 flex，换成 grid 写一下。", inc=["grid"], any_=["place-items", "place-content", "justify-content"])],
         notes={"ref": "flex then grid", "why": "keywords"})
