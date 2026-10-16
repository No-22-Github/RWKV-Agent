## Traps
- TR-DECOY: ansible_port=22 on every host; turn 2 must modify db2 only.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. sed on db2 line
2. sed port
3. grep db hosts.ini

## Why the answer is unique
db2 line final: 10.0.2.52 port 2222.
Final answer should mention: 10.0.2.52; 2222; 10.0.2.52; db1
