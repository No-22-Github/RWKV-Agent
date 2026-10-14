## Traps
- TR-DECOY: a similar name must survive.

## Reference solution
第一轮 rm tmp/*.tmp；第二轮 rm -r old 并数文件，只剩 tmp/notes.txt，共 1 个。

## Why the answer is unique
bash is offered and works in the sandbox, so the files must end up exactly as expect.files says (a reply claiming it without the change fails, and so does leaving the files alone).
