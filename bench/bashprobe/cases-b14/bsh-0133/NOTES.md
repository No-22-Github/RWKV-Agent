## Traps
- TR-READONLY: 前端/工具/logger.js uses console.log on purpose.
- The commented example line starts with spaces and // and stays.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `sed -i "/^console\.log('debug /d" 前端/页面/*.js`
2. bash: `grep -rn console.log 前端`
Final answer: 五个页面里的 debug console.log 已删除，注释示例和 logger.js 保留，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
