## Traps
- TR-NEARNAME: the request uses the old work-ticket name 汤池区; the config
  section is 泡池区, as the README records. Raising 客房暖气's 52 or touching
  the section name is the trap.

## Reference solution
1. Read README.md: 汤池区 maps to the 泡池区 section.
2. Read config/boiler.yaml.
3. Change 泡池区's 供水温度 from 41 to 44, leaving every other line as it is.

## Why the answer is unique
README 明确「汤池区＝泡池区」，客房暖气的 52 与泡池区的保温温度 46 都
不是目标键；41 只在泡池区出现一次，行式保持不变，改完的文件只有一种。
