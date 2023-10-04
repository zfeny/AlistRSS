import json, time
from py_scripts import file_rw, rss_sub, apis

if __name__ == "__main__":
    start_time = time.time() # 用于运行计时
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 用于生成时间戳

    config_json_path = file_rw.path2data("config.json")
    rss_data_db_path = file_rw.path2data("rss_data.db")
    feeds_csv_path = file_rw.path2data("feeds.csv")
    
    with open(config_json_path, "r", encoding='utf-8') as config_file:
        config_data = json.load(config_file)
        alist_config = config_data["alist_config"]
        clock = config_data["clock"]
        tg_bot_info = config_data["tg_bot_info"]

    # 获取RSS更新
    return_rss_sub_new = rss_sub.new(rss_data_db_path, feeds_csv_path, alist_config["auto_path"])
    
    # 返回信息需修改
    if return_rss_sub_new == 0:
        print("RSS无更新")
    elif return_rss_sub_new == -1:
        print("非MikananiRSS链，无法解析URL。")
    else:
        print(f"RSS更新完成，共更新{return_rss_sub_new}个RSS项。")

        # Alist集成
        need_to_sends = file_rw.sqlite_get_status(rss_data_db_path)
        success_id = []
        failed_id = []

        for need_to_send in need_to_sends:

            alist_auth_url = alist_config["domain"].rstrip('/') + '/api/auth/login' if alist_config["domain"].endswith('/') else alist_config["domain"] + '/api/auth/login'
            alist_aria2_url = alist_config["domain"].rstrip('/') + '/api/fs/add_aria2' if alist_config["domain"].endswith('/') else alist_config["domain"] + '/api/fs/add_aria2'
            alist_auth_token = apis.alist_get_token(alist_auth_url, alist_config["login_data"])
            alist_headers = {
                'Authorization': alist_auth_token
            }
            alist_data = file_rw.sqlite_get_urlpath(rss_data_db_path, need_to_send)
            alist_response = apis.alist_add_aria2(alist_aria2_url, alist_headers, alist_data)

            # 记录API响应
            if alist_response.status_code == 200:
                success_id.append(need_to_send)
                file_rw.sqlite_set_status(rss_data_db_path, need_to_send)
            else:
                failed_id.append(need_to_send)
            
            time.sleep(1) # 防止Aria2过载

        # Telegram集成
        suc_num = len(success_id)
        fai_num = len(failed_id)
        rss_num = suc_num + fai_num
        tg_ms = f"""
本次RSS程序运行完毕，共拉取 <b>{rss_num}</b> 个RSS项。
_____________________________________
"""
        if fai_num > 0:
            tg_ms += f"""
其中有 <b>{fai_num}</b> 个RSS项下载失败，请检查 <b>Aria2</b> 状态。
_____________________________________
"""
        
        for item in success_id:
            item_info = file_rw.sqlite_get_info(rss_data_db_path, item)
            item_path = alist_config["domain"] + item_info['path']
            tg_ms += f"""
<a href="{item_path}">{item_info['title']}</a>

"""
        tg_ms += f"""
_____________________________________
"""
        if fai_num > 0:
            tg_ms += f"""
以下 <b>RSS</b> 项下载失败:

"""
            for item in failed_id:
                item_info = file_rw.sqlite_get_info(rss_data_db_path, item)
                tg_ms += f"""
<a href="{item_info['link']}">{item_info['title']}</a>

"""
            tg_ms += f"""
_____________________________________
"""
        end_time = time.time()
        run_time = end_time - start_time
        minutes, seconds = divmod(run_time, 60)
        hours, minutes = divmod(minutes, 60)
        tg_ms += f"""
本次程序运行时间：<b>{int(hours)}</b> 小时 <b>{int(minutes)}</b> 分钟 <b>{int(seconds)}</b> 秒

"""

        if minutes > 1:
            tg_ms += """
您的程序运行时间大于一分钟，请考虑升级服务器配置或减少RSS订阅源数量。
"""
        
        apis.tg_bot(tg_ms, tg_bot_info)