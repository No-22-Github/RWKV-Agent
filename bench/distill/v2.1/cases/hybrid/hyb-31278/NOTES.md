## Traps
- TR-ABSENT: 问题的后半部分（sensor-17 的电量）查不到。
- TR-DECOY: sensor-22 有 battery=63，是别的设备。

## Reference solution
sensor-17 最后上报 08:45:09；日志里 sensor-17 没有 battery 字段，只有 sensor-22 有 63。

## Why the answer is unique
读日志：17 最后 08:45:09，没有电量；22 的 63 不能算 17 的。

## Five alternative phrasings of the task
1. 查查设备 sensor-17 最后一次上报的时间和电池电量。
2. 想确认一下：查查设备 sensor-17 最后一次上报的时间和电池电量。
3. 查查设备 sensor-17 最后一次上报的时间和电池电量。（简单说就行）
4. 麻烦帮我看看：查查设备 sensor-17 最后一次上报的时间和电池电量。
5. 再问一件事：查查设备 sensor-17 最后一次上报的时间和电池电量。
