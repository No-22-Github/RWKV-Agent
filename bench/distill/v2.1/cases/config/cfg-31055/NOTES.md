## Traps
- TR-READONLY: secrets.env also has APP_REGION=cn-east and must stay.
- 2 file(s) change, 2 stay byte-identical.

## Reference solution
1. read the README/NOTES first
2. read README
3. edit timeout
4. edit region in two files

## Why the answer is unique
app.env and worker.env change; secrets stays.
Final answer should mention: 45; cn-north; secrets.env
