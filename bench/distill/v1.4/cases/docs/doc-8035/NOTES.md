## Traps
- None. 起点和间隔都在题面里；用户明确说别查。

## Reference solution
不调用任何工具：周五往后 10 天，10 ÷ 7 余 3，即再过三天，周五加三天是周一，会员日是周一。判据：零调用，包含「周一/星期一/礼拜一」之一。

## Why the answer is unique
(周五 + 10 天) mod 7 唯一对应周一。
