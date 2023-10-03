import subprocess, os

def terminate_process(pid):
    try:
        subprocess.run(['kill', str(pid)])
        print(f"进程 {pid} 已被终止，定时任务已取消。")
    except subprocess.CalledProcessError:
        print(f"终止进程 {pid} 时出错")

# 文件路径
pid_file_path = 'data/imp_pid.txt'
try:
    with open(pid_file_path, 'r') as pid_file:
        pid_value = pid_file.read()
        # 将读取的PID值转换为整数
        pid = int(pid_value)
    terminate_process(pid)
    os.remove(pid_file_path)
except FileNotFoundError:
    print(f"文件 '{pid_file_path}' 不存在，你还没启动程序呢")
except IOError as e:
    print(f"读取PID文件时出错: {e}")
except ValueError:
    print("无效的PID值在文件中。")