import requests, time, json, feedparser, sqlite3, os

# TG消息推送
def tg_bot(message, bot_token, chat_id):
    api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    response = requests.post(api_url, params=params)

    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message. Status code:', response.status_code)

# 解析 RSS 源
def parse_rss_feed(rss_url, dl_path):
    feed = feedparser.parse(rss_url)
    entries = feed.entries
    parsed_entries = []
    # 添加保存路径
    for entry in entries[:20]:
        parsed_entry = {
            'link': entry.link,
            'description': entry.description,
            'published': entry.published,
            'torrent_url': entry.enclosures[0].get("url") if entry.enclosures else None,
            'dl_path': dl_path
        }
        parsed_entries.append(parsed_entry)
    return parsed_entries[:20]  # 返回最新的20项内容

# 检查历史记录
def check_history_entries(entries, database):
    # 连接数据库
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # 获取已有的历史记录
    cursor.execute("SELECT Link FROM history")
    existing_links = {row[0] for row in cursor.fetchall()}

    # 过滤掉已存在的内容
    new_entries = [entry for entry in entries if entry['link'] not in existing_links]

    # 关闭数据库连接
    conn.close()

    return new_entries

# 将新内容写入数据库
def write_to_database(entries, database):
    # 连接数据库
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # 插入新内容到 history 表
    inserted_ids = []
    for parsed_entry in entries:
        cursor.execute("INSERT INTO history (Link, Description, PubDate, Torrent_url, Download_path) VALUES (?, ?, ?, ?, ?)",
                       (parsed_entry['link'], parsed_entry['description'], parsed_entry['published'],
                        parsed_entry['torrent_url'], parsed_entry['dl_path']))
        inserted_ids.append(cursor.lastrowid)
    # 提交并关闭数据库连接
    conn.commit()
    conn.close()

    return inserted_ids

# 订阅RSS源
def rss_sub(rss_url, dl_path, rss_data):
    # 检查数据库是否存在
    if not os.path.isfile(rss_data):
        conn = sqlite3.connect(rss_data)
        cursor = conn.cursor()

        # 创建 history 表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                Link TEXT UNIQUE,
                Description TEXT,
                PubDate TEXT,
                Torrent_url TEXT,
                Download_path TEXT
            )
        ''')

        conn.commit()
        conn.close()
    
    # 解析 RSS 源
    entries = parse_rss_feed(rss_url, dl_path)

    # 检查历史记录，过滤掉已存在的内容
    new_entries = check_history_entries(entries, rss_data)

    if new_entries:
        # 有新内容，写入数据库并触发推送任务
        new_item_id = write_to_database(new_entries, rss_data)
        # 触发推送任务的代码放在这里
        return new_item_id
    else:
        # 没有新内容，不触发推送任务
        return []

# 获取对应下载链接和保存路径
def get_TRurl_path(record_ids, database):
    # 连接数据库
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # 构建查询语句
    query = "SELECT id, Torrent_url, Download_path FROM history WHERE id IN ({})".format(", ".join(map(str, record_ids)))

    # 执行查询
    cursor.execute(query)

    # 获取结果
    records = cursor.fetchall()

    # 关闭数据库连接
    conn.close()

    return records

# 获取对应描述和保存路径
def get_DS_path(record_ids, database):
    if isinstance(record_ids, int):
        # 如果record_ids是整数，将其包装成一个包含单个元素的列表
        record_ids = [record_ids]
    # 连接数据库
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # 构建查询语句
    query = "SELECT Description, Download_path FROM history WHERE id IN ({})".format(", ".join(map(str, record_ids)))

    # 执行查询
    cursor.execute(query)

    # 获取结果
    records = cursor.fetchall()

    # 关闭数据库连接
    conn.close()

    return records

# 获取对应描述和原文链接
def get_DS_link(record_ids, database):
    if isinstance(record_ids, int):
        # 如果record_ids是整数，将其包装成一个包含单个元素的列表
        record_ids = [record_ids]
    # 连接数据库
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # 构建查询语句
    query = "SELECT Description, Link FROM history WHERE id IN ({})".format(", ".join(map(str, record_ids)))

    # 执行查询
    cursor.execute(query)

    # 获取结果
    records = cursor.fetchall()

    # 关闭数据库连接
    conn.close()

    return records

# 封装Alist Token API
def get_auth_token(login_url, login_data):
    # 发送HTTP POST请求以登录并获取令牌
    response = requests.post(login_url, json=login_data)

    # 解析API响应
    if response.status_code == 200:
        # 获取返回的令牌
        token = response.json().get('data', {}).get('token', '')
        return token
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

# 封装Alist Aria2 API
def send_to_aria2(record_ids, rss_db, alist_config):
    # 获取下载链接和保存路径
    records = get_TRurl_path(record_ids, rss_db)
    # 发送到Aria2
    domain = alist_config["domain"]
    if domain.endswith('/'):
        domain = domain.rstrip('/')
    aria2_url = domain + '/api/fs/add_aria2'
    login_url = domain + '/api/auth/login'
    login_data = {
        'username': alist_config["username"],
        'password': alist_config["password"]
    }
    success_id = []
    failed_id = []

    for record in records:
        alist_token = get_auth_token(login_url, login_data)
        alist_headers = {
            'Authorization': alist_token
        }
        alist_data = {
            'urls': [record[1]],
            'path': record[2]
        }
        alist_response = requests.post(aria2_url, headers=alist_headers, json=alist_data)

        # 解析API响应
        if alist_response.status_code == 200:
            success_id.append(record[0])
        else:
            failed_id.append(record[0])
        # time.sleep(1) # 防止Aria2过载
    
    # 返回处理结果
    values = {
        'success_id': success_id,
        'failed_id': failed_id
    }
    return values

if __name__ == "__main__":
    start_time = time.time() # 用于运行计时
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 用于生成时间戳

    with open("config.json", "r", encoding='utf-8') as config_file:
        config_data = json.load(config_file)
        alist_config = config_data["alist_config"]
        rss_feeds = config_data["rss_feeds"]
        tg_bot_token = config_data["tg_bot_token"]
        tg_chat_id = config_data["tg_chat_id"]

    # 获取RSS更新
    new_entries = [] # 更新的RSS项序号
    rss_db = "rss_data.db"
    for rss_feed in rss_feeds:
        new_entry = rss_sub(rss_feed["url"], rss_feed["path"], rss_db)
        for item in new_entry:
            new_entries.append(item)
    
    # 发送到Aria2
    if new_entries:
        aria2_return = send_to_aria2(new_entries, rss_db, alist_config)
        rss_success = len(aria2_return["success_id"])
        rss_failed = len(aria2_return["failed_id"])
        rss_num = rss_success + rss_failed

        # Telegram推送消息
        tg_ms = f'RSS订阅程序运行完毕，本次共拉取*{rss_num}*个RSS项。\n'
        if rss_failed > 0:
            tg_ms += f'其中有*{rss_failed}*个RSS项下载失败，请检查Aria2状态。\n'
        tg_ms += "---\n"
        for i in aria2_return["success_id"]:
            get_DS_path_return = get_DS_path(i, rss_db)
            ms_title = get_DS_path_return[0][0]
            ms_url = alist_config["domain"]+get_DS_path_return[0][1]
            tg_ms += f'"[{ms_title}]({ms_url})\n"'
        tg_ms += "---\n"
        if rss_failed > 0:
            tg_ms += "*以下RSS项添加失败：*\n"
            for i in aria2_return["failed_id"]:
                get_DS_link_return = get_DS_link(i, rss_db)
                ms_title = get_DS_link_return[0][0]
                ms_url = get_DS_link_return[0][1]
                tg_ms += f"[{ms_title}]({ms_url})\n"
        tg_ms += "---\n"

        end_time = time.time() 
        run_time = end_time - start_time
        minutes, seconds = divmod(run_time, 60)
        hours, minutes = divmod(minutes, 60)
        tg_ms += f"本次程序运行时间：*{int(hours)} 小时 {int(minutes)} 分钟 {int(seconds)} 秒*\n"
        if minutes > 1:
            tg_ms += "您的程序运行时间大于一分钟，请考虑升级服务器配置或减少RSS订阅源数量。\n"
        
        tg_bot(tg_ms, tg_bot_token, tg_chat_id)
    else:
        end_time = time.time() 
        run_time = end_time - start_time
        minutes, seconds = divmod(run_time, 60)
        hours, minutes = divmod(minutes, 60)
        running_time = f"程序运行时间：{int(hours)} 小时 {int(minutes)} 分钟 {int(seconds)} 秒\n"
        print(f"{running_time}没有新的RSS项。")
    