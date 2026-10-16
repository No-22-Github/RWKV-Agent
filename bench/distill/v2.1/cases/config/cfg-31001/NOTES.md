## Traps
- TR-DECOY: three server blocks carry the identical client_max_body_size 10m line; only the api block changes.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines conf/nginx.conf to get numbered lines
2. replace_lines on line 14 with the 50m line
3. read back lines 12-15

## Why the answer is unique
Only the api.lantern.example block's limit becomes 50m; expect.files equals pins the whole file.
Final answer should mention: 50m; client_max_body_size
