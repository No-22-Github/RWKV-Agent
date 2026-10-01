## Traps
- TR-DECOY: 开槽 already has a 槽间距: 5; putting the new 拉槽间距 6 there,
  or merging the milling settings into the grooving section, is the trap. The
  README says the milling stage gets its own section.

## Reference solution
1. Read README.md: the milling stage is its own section 铣背 with keys 铣背深度 and 拉槽间距, appended at the end of the file; the 开槽 section's keys belong to the groover and stay.
2. Read config/binder.yaml.
3. Append the 铣背 section with 2 and 6, leaving every existing line byte-identical.

## Why the answer is unique
README 把新段名、键名、位置（文件末尾）都固定下来，两个数值由请求给出；
开槽段的 槽间距 5 属于刨副机，动了它就会改变既有工位的行为。所以追加的
块和改完的文件各只有一种内容。
