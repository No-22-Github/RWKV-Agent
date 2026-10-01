## Traps
- TR-DECOY: archive.py 里有一行注释掉的旧调用 `# extra = calc_surcharge(...)`，把它当真会得 3。

## Reference solution
1. 搜索 calc_surcharge，列出 tariff.py（定义）、invoice.py、nightly.py、archive.py（注释）的命中。
2. 读 invoice.py 与 nightly.py，各有一处真实调用。
3. 确认 archive.py 的命中在注释里，作答 2。

## Why the answer is unique
「调用」指会真正执行的调用：invoice.py 循环体内一处、nightly.py 一处，共 2 处。archive.py 的命中以 `#` 开头，是改版时留下的注释，不产生调用；tariff.py 是定义本身。数注释会得到 3，但注释代码不执行，不是调用点。

## 正确答案
2
