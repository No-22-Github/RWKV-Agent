## Traps
- TR-ABSENT: rate_limit_burst 在被问的范围内没有定义。
- TR-DECOY: 灰度文件里 rate_limit_burst=120，线上文件没有。

## Reference solution
读线上 limits.yaml：没有 rate_limit_burst。

## Why the answer is unique
线上 limits.yaml 没有定义 rate_limit_burst，只有 rate_limit_per_sec=200；120 只是灰度机器的值。
