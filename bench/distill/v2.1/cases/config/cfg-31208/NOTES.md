## Traps
- TR-ABSENT: defrost_interval_h 在被问的范围内没有定义。
- TR-DECOY: A 区是 8 小时；B 区没有 defrost_interval_h，只有近名的 defrost_duration_min=25（时长不是间隔）。

## Reference solution
读 zoneB.yaml：没有 defrost_interval_h。

## Why the answer is unique
zoneB.yaml 没有 defrost_interval_h，只有 defrost_duration_min=25（化霜时长，不是间隔）；A 区的 8 不能套用。
