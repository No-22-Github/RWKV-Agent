## Traps
- TR-MULTISRC: 调用分散在 invoice.py（两处）、picking.py、returns.py；只看题面点名的 invoice.py 会得 2。
- TR-DECOY: picking.py 的 return 之后有一行注释掉的旧调用，把它算上会得 5。

## Reference solution
1. 搜索 reserve_stock，列出 stock.py（定义）、invoice.py、picking.py、returns.py 的命中。
2. 读 picking.py 与 returns.py，确认各有一处真实调用、picking.py 末尾的命中在注释里。
3. 汇总 invoice.py 两处 + picking.py 一处 + returns.py 一处，作答 4。

## Why the answer is unique
真实执行的调用：invoice.py 的循环体与草稿分支各一处（同一函数里两个调用表达式）、picking.py 一处、returns.py 一处，共 4 处。只看 invoice.py 得 2 漏了两个模块；把 picking.py 末尾 `#` 注释算上得 5，但注释不执行，不是调用点。

## 正确答案
4
