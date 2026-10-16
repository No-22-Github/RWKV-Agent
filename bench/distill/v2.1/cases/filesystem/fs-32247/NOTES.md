## Traps
- TR-TRUNC: 150+ files.

## Reference solution
1. find | cut -d/ -f2 | sort | uniq -c, reformat, write.
Reference commands (replayed in the sandbox): find 资料 -type f -name '*.dat' | cut -d/ -f2 | sort | uniq -c | awk '{print $2" "$1}' | sort > 资料/counts.txt; wc -l < 资料/counts.txt; cat 资料/counts.txt
Final answer: turn 1 -> 57 其它; turn 2 -> 6 

## Why the answer is unique
Counts are exact; file lines sorted by name (byte order).
