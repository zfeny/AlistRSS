import subprocess

# 文件路径
pid_file_path = 'data/imp_pid.txt'
py_file_path = 'rss/loop.py'
requirements_file = 'data/requirements.txt'

# 安装依赖库
pip_install_command = f'pip install -r {requirements_file}'
try:
    subprocess.run(pip_install_command, shell=True, check=True)
    print("库已成功安装")
except subprocess.CalledProcessError as e:
    print(f"安装库时出错: {e}")

# 启动后台任务
try:
    result = subprocess.Popen(['nohup', 'python', py_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(pid_file_path, 'w') as pid_file:
        pid_file.write(str(result.pid))
    print(f"后台任务：{result.pid}已启动，终止进程请使用`python stop.py`")
except IOError as e:
    print(f"写入PID文件时出错: {e}")