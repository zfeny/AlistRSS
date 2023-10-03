import time, json, subprocess

def sleeptime(hour, min, sec):
    return hour*3600 + min*60 + sec

# 文件路径
config_json_path = "config.json"
task_name = "main.py"

with open(config_json_path, "r", encoding='utf-8') as config_file:
    config_data = json.load(config_file)
    clock = config_data["clock"]

while 1==1:
    time.sleep(clock)
    subprocess.run(['python', task_name])