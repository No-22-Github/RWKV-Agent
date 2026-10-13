## Traps
- TR-DECOY: a case-sensitive '*.jpg' glob (misses .JPG/.jpeg, counts thumbnails) gives 74; the README's rule gives 93.
- 229 files in nested folders under 相册/, so counting by listing is not practical.

## Reference solution
1. bash: `find 相册 -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -not -path '*/.thumbs/*' | wc -l` -> 93
Final answer: 按说明的口径一共 93 张照片（.jpg/.jpeg 不分大小写，缩略图和 .bak 不算）。

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
