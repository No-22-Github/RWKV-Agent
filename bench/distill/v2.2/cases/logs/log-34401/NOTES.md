## Traps
First screen of logs/edge-proxy-0913.log shows only 200/304/404; the first 502 is at line 1389. 500 and 503 appear earlier and are not 502.

## Reference solution
wc -l / head to see format, grep -n '" 502 ' | head -1, then grep -c.

## Why the answer is unique
verify.py recomputes the first 502 time and the total from the fixture. Expected answer per turn: 09:11:22; 3.
