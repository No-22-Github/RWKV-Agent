## Traps
- TR-READONLY: 照片/素材库/ file names are referenced by the website.
- .png files keep their names.
- 15 files change; 10 stay byte-identical.

## Reference solution
1. bash: `for f in $(find 照片 -name '*.jpeg' -not -path '*/素材库/*'); do mv "$f" "${f%.jpeg}.jpg"; done`
2. bash: `find 照片 -name '*.jp*g' | sort`
Final answer: 照片 下的 .jpeg 都改成了 .jpg（素材库除外），find 确认过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
