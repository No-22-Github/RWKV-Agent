## Traps
- TR-ABSENT: wake_word_sensitivity 在被问的范围内没有定义。
- TR-DECOY: CN 的灵敏度 0.7；EU 的 audio.yaml 没有，README 说没有共享默认值。

## Reference solution
读 eu/audio.yaml 与 README：没有该键、没有默认值。

## Why the answer is unique
fw/eu/audio.yaml 没有 wake_word_sensitivity，README 也说没有共享默认值；0.7 只是 CN 版的值。
