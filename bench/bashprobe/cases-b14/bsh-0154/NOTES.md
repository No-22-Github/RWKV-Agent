## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `tar -xzf 下载/安装包.tar.gz -C /opt/app`。

## Why the answer is unique
The command's key option is fixed by the task; any of tar -xzf, tar xzf, tar -zxf, tar zxf, tar -xvzf, tar xvzf, tar -zxvf, tar zxvf shows it.
