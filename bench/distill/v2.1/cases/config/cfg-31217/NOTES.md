## Traps
- TR-ABSENT: min_supported_ios 在被问的范围内没有定义。
- TR-DECOY: ios.json has min_supported_ios=15.0; the Android file has no such key (it has min_supported_sdk).

## Reference solution
Read android.json: no min_supported_ios.

## Why the answer is unique
android.json has no min_supported_ios (it uses min_supported_sdk: 26); 15.0 is the iOS file's value, and an iOS key doesn't apply to Android anyway.
