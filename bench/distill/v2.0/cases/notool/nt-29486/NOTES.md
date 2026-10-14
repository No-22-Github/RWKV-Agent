## Traps
- TR-NOTOOLNEED: a weather concept question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: 风向指风吹来的方向，西北风是从西北吹向东南；风级按风速划分（蒲福风级），3 到 4 级是微风到和风。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['吹来', '来自', '来的方向', '从西北', '风速', '蒲福'].

## Five alternative phrasings of the task
1. 西北风到底是往哪边吹的？风力 3 到 4 级是什么程度？
2. 预报里的风向是指风来的方向还是去的方向？风级怎么分？
3. 东南风是从东南吹来还是吹向东南？蒲福风级是什么？
4. 怎么理解天气预报中的风向和风力等级？
5. 解释一下风向的命名规则，以及风级大概对应多大的风。
