## Traps
- TR-NOTOOLNEED: a weather concept question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: 相对湿度是空气中实际水汽含量与同温度下饱和水汽量之比，100% 表示饱和，不一定下雨。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['饱和', '水汽', '最大'].

## Five alternative phrasings of the task
1. 相对湿度 100% 是不是一定在下雨？这个数字怎么理解？
2. 湿度 100% 说明什么？和下雨有必然联系吗？
3. 天气里的相对湿度是个什么概念，100% 代表下雨吗？
4. 为什么湿度很高有时也不下雨？相对湿度的定义是什么？
5. 解释一下相对湿度，100% 就是在下雨吗？
