import time, json, subprocess
import file_rw 

def sleeptime(hour, min, sec):
    return hour*3600 + min*60 + sec

# 文件路径
task_name = "main.py"
config_json_path = file_rw.path2data("config.json")
task_path = file_rw.get_task_path(task_name)

with open(config_json_path, "r", encoding='utf-8') as config_file:
    config_data = json.load(config_file)
    clock = config_data["clock"]

while 1==1:
    time.sleep(clock)
    subprocess.run(['python', task_path])