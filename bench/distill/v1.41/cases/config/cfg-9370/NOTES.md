## Traps
- TR-DECOY: requests.cpu 250m sits next to limits.cpu 500m; values.yaml.orig says 1000m.

## Reference solution
1. read_file charts/web/values.yaml
Final answer: CPU limit 是 500m（requests 是 250m；.orig 里的 1000m 是旧值）。

## Why the answer is unique
The user names charts/web/values.yaml; only its live line holds the answer. requests.cpu is 250m and values.yaml.orig says 1000m.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash.

## Five alternative phrasings of the task
1. charts/web/values.yaml 的 resources.limits.cpu 是多少？
2. web 这个 chart 的 CPU 上限（limits）写的是什么？看 charts/web/values.yaml。
3. values.yaml（charts/web 下）里 limits 的 cpu 值是多少？
4. 请查 charts/web/values.yaml：容器 CPU limit 是？
5. charts/web/values.yaml 给 CPU 限制了多少？
