## Traps
- TR-MULTISRC: the window's alarms are split across two files, five in the boiler house journal and three in the turbine hall journal. Reading only the boiler house file answers 5.

## Reference solution
1. List the workspace: README.md, logs/boiler-house.log, logs/turbine-hall.log.
2. Read logs/boiler-house.log and count ALARM lines stamped 09:00:00 up to 10:00:00: 09:03, 09:21, 09:38, 09:47, 09:56 = 5.
3. Read logs/turbine-hall.log and count its ALARM lines in the same window: 09:12, 09:31, 09:55 = 3. Together 5 + 3 = 8.

## Why the answer is unique
Both files stamp in the same style and the question asks for the mill's alarms, so the window cut applies to the union of the two journals; every alarm line sits in exactly one file, so the union has one reading. A single-file count is a partial answer by construction, which is the decoy 5. The union yields 8.
