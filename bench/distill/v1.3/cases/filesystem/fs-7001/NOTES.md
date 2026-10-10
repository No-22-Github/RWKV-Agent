## Traps
- 无陷阱（L0 基题）。相邻干扰：maintenance/pump-01.txt 也是水泵档案，但安装位置是北泵房（溪引水），额定流量 8.2；题面问的是南泵房。

## Reference solution
1. 看 maintenance/ 目录或读 README.md：每台设备一份档案，档案头记录安装位置。
2. 读 maintenance/pump-02.txt：安装位置为南泵房（井水），额定流量 12.5 立方米每小时。
3. 终答只报数字 12.5。

## Why the answer is unique
两份水泵档案里只有 pump-02 的安装位置是南泵房，8.2 属于北泵房的水泵；发电机档案只有额定功率、没有额定流量字段。位置字段唯一、数值字段唯一，答案只有 12.5。
