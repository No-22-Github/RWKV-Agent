## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（合同审查/采购合同-条款清单.md 620 行、合同审查/外包合同-条款清单.md 732 行、合同审查/租赁合同-条款清单.md 508 行、合同审查/合作协议-条款清单.md 690 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态和负责人
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 吴婷-高风险待确认条款.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open and the named owner; decoys differ in exactly one field.

## Estimated trajectory tokens
14260
(fixture: 合同审查/采购合同-条款清单.md=7926, 合同审查/外包合同-条款清单.md=9356, 合同审查/租赁合同-条款清单.md=6522, 合同审查/合作协议-条款清单.md=8924)
lines per document: [620, 732, 508, 690]

## Five alternative phrasings of the task
1. 法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。
2. 麻烦帮我：法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。
3. 法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。（用中文回答）
4. 想请你看看：法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。
5. 再确认一下：法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。
