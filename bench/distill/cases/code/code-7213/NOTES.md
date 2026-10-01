## Traps
- TR-NEARNAME: 包里定义并调用了 load_model_lazy（调用 5 处），名字以 load_model 开头；按前缀或文本统计会把懒加载孪生折进来。
- TR-DECOY: 注释（第 446 行、第 826 行）也写着 load_model；调用点是真实调用表达式。按名字精确匹配后调用共 14 处。

## Reference solution
1. 读 README.md：范围是 shibei_ops/，调用点指真实调用表达式，名字精确匹配。
2. 检索 load_model，在命中处附近的行段里逐条核对。
3. 排除定义本身、注释与 load_model_lazy 的调用。
4. 实际调用 14 处。

## Why the answer is unique
README 钉死了范围与精确匹配；load_model_lazy 是另一个函数，注释不是调用表达式。包内 load_model 的调用表达式恰好 14 处。
