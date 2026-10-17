## Traps
TR-NEARNAME: MAX_UPLOAD_BYTES_ANON and _LEGACY; TR-DECOY: test comment and import.

## Reference solution
grep MAX_UPLOAD_BYTES; pick the assignment line.

## Why the answer is unique
Only limits.py has `MAX_UPLOAD_BYTES =`; line 15.
Expected: media/config/limits.py; 15; 52428800
