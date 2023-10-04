#!/bin/bash

# 获取脚本所在的目录
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
requirements_file="$script_dir/data/requirements.txt"  
file_to_change="stop.sh"

# 检查pip是否存在
if ! command -v pip3 &> /dev/null; then
    echo "pip3 未安装。尝试安装..."
    sudo apt-get install python3-pip  # 请根据您的系统使用适当的命令
fi

# 安装依赖项从requirements.txt文件
if [ -f "$requirements_file" ]; then
    echo "安装依赖项..."
    pip3 install -r "$requirements_file"
else
    echo "$requirements_file 不存在."
fi

# 添加可执行权限
if [ -f "$script_dir/$file_to_change" ]; then
  chmod +x "$script_dir/$file_to_change"
  echo "Added execute permission to $script_dir/$file_to_change"
else
  echo "$script_dir/$file_to_change not found."
fi

# 启动后台服务
nohup /usr/bin/python3 "$script_dir/py_scripts/loop.py" > /dev/null 2>&1 &

# 输出进程ID到文件（可选）
mkdir -p "$script_dir/data/temp/"
echo $! > "$script_dir/data/temp/task.pid"