## Traps
Three restarts with different causes; the earlier ones are in the first half of the file.

## Reference solution
grep -n 'service restarted' | tail -1 -> 3172; read_file start_line=3170 end_line=3173.

## Why the answer is unique
watchdog (no heartbeat for 60s). Expected answer per turn: watchdog.
