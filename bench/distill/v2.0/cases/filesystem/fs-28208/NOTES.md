## Traps
- The drafts subfolder holds two unpublished scripts.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：Four scripts are published (ep01 to ep04); ep05 and ep06 are still drafts.
判据见 case.json（contains=[] any=['4 ', 'four', 'Four', '4.', '4 episode', '4 script'] excl=['6 episode', 'six']）。

## Why the answer is unique
README says drafts are unpublished; four scripts sit outside drafts/.
