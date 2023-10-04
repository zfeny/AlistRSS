#!/bin/bash

# 定义.pid文件的路径
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # 获取脚本所在的目录
pid_file="$script_dir/data/temp/task.pid"

# 检查.pid文件是否存在
if [ -e "$pid_file" ]; then
    # 读取.pid文件中的内容
    pid=$(cat "$pid_file")
    
    # 检查进程是否存在
    if ps -p $pid > /dev/null; then
        # 终止进程
        kill $pid
        echo "已终止进程 $pid"
    else
        echo "进程 $pid 不存在"
    fi
    # 删除.pid文件
    rm "$pid_file"
else
    echo ".pid 文件不存在，RSS订阅服务还没启动呢"
fi