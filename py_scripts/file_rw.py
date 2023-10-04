# 不要移动这个文件！
# 其他的文件最好也别动，除非你知道自己在干什么
# File Read and Write

import os, sqlite3, csv, feedparser
from datetime import datetime, timedelta

# 文件路径相关
def get_path():
    current_script_path = os.path.abspath(__file__)
    father_path = os.path.dirname(current_script_path)
    main_folder_path = os.path.dirname(father_path)
    return main_folder_path

def get_task_path(task_name):
    current_script_path = os.path.abspath(__file__)
    father_path = os.path.dirname(current_script_path)
    task_path = os.path.join(father_path, task_name)
    return task_path

def path2data(filename):
    data_folder_path = os.path.join(get_path(), 'data')
    return os.path.join(data_folder_path, filename)

def path2py_scripts(filename):
    py_scripts_folder_path = os.path.join(get_path(), 'py_scripts')
    return os.path.join(py_scripts_folder_path, filename)

#检测csv文件，填补空值
def fill_empty_values(input_csv):
    output_csv = input_csv  # 输出文件和输入文件相同

    with open(input_csv, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # 检查文件是否为空
        try:
            header = next(csv_reader)
        except StopIteration:
            return

        with open(output_csv, 'w', newline='') as output_file:
            csv_writer = csv.writer(output_file)

            # 将标题行写入输出文件
            csv_writer.writerow(header)

            for row in csv_reader:
                # 确保每一行都至少有4个列（url, name, save_path, last_updated）
                while len(row) < 4:
                    row.append(None)
                csv_writer.writerow(row)

# 数据库读写
def sqlite_creat_table(database,table_structure):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(table_structure)
    conn.commit()
    conn.close()

def sqlite_get_updated(database, query, conditions):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(query, conditions)
    records = cursor.fetchall()
    conn.close()
    return records

def sqlite_add_feed(database, csv_path):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    fill_empty_values(csv_path)

    with open(csv_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:

            url, name, save_path, last_updated = row

            cursor.execute('''
                INSERT INTO feeds (url, name, save_path, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (url, name, save_path, last_updated))

    conn.commit()
    conn.close()

    with open(csv_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)

    os.remove(csv_path)

    # 重新创建CSV文件并写回标题行
    with open(csv_path, 'w', newline='') as new_csv_file:
        csv_writer = csv.writer(new_csv_file)
        csv_writer.writerow(header)

def sqlite_add_history(database, id1, id2, link, description, pub_date, torrent_url, Save_path, Status):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("SELECT Link FROM history WHERE Link=?", (link,))
    existing_link = cursor.fetchone()
    if existing_link is None:
        cursor.execute("INSERT OR IGNORE INTO history (Bagumi_id, Subgroup_id, Link, Description, PubDate, Torrent_url, Save_path, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (id1, id2, link, description, pub_date, torrent_url, Save_path, Status))

    conn.commit()
    conn.close()
    if existing_link is None:
        return True
    else:
        return None

def sqlite_add_feed_time(database, record_urls):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    current_time = datetime.now()

    for record_url in record_urls:
        cursor.execute('''
            UPDATE feeds
            SET last_updated = ?
            WHERE url = ?
        ''', (current_time, record_url))

    conn.commit()
    conn.close()

def sqlite_get_status(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id FROM history
        WHERE status = 0
    ''')
    
    ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return ids

def sqlite_get_urlpath(database, item_id):
    url_path_mapping = {
        'urls': [],
        'path': ''
    }
    
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT Torrent_url, Save_path FROM history
        WHERE id = ?
    ''', (item_id,))

    result = cursor.fetchone()

    conn.close()

    url, save_path = result
    url_path_mapping['urls'].append(url)
    url_path_mapping['path'] = save_path
    
    return url_path_mapping

def sqlite_set_status(database, item_id):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE history
        SET Status = 1
        WHERE id = ?
    ''', (item_id,))
    
    conn.commit()
    conn.close()

def sqlite_get_info(database, item_id):

    info = {
        'title': '',
        'link': '',
        'path': ''
    }

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT Description, Link, Save_path FROM history
        WHERE id = ?
    ''', (item_id,))

    result = cursor.fetchone()

    conn.close()
    info['title'], info['link'], info['path'] = result
    
    return info

# 管理RSS源
def feed_read(database,csv_file):
    # database_path = path2data(database)
    # csv_path = path2data(csv_file)
    table = '''
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            save_path TEXT NOT NULL,
            last_updated TIMESTAMP
        )
    '''
    sqlite_creat_table(database, table)
    sqlite_add_feed(database, csv_file)

    one_day_ago = datetime.now() - timedelta(days=1)
    rule = '''
        SELECT url, save_path FROM feeds
        WHERE last_updated < ? OR last_updated IS NULL
    '''

    condition = (one_day_ago,)
    need_update = sqlite_get_updated(database, rule, condition)

    record_ids = [record[0] for record in need_update]
    sqlite_add_feed_time(database, record_ids)
     
    return need_update

# 拉取RSS源并把更新项写入数据库
def feed_sub(database, url, save_path, auto_path, feed_id):
    table = '''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Bagumi_id INTEGER,
            Subgroup_id INTEGER,
            Link TEXT UNIQUE,
            Description TEXT,
            PubDate TEXT,
            Torrent_url TEXT,
            Save_path TEXT,
            Status INTEGER
        )
    '''
    sqlite_creat_table(database, table)
    resource = feedparser.parse(url)
    if not save_path:
        save_path = auto_path + '/' + feed_id[0] + '/' + feed_id[1]
    for entry in resource.entries:
        link = entry.link
        description = entry.title
        pub_date = entry.published
        torrent_url = entry.enclosures[0].href if entry.enclosures else ""
        if sqlite_add_history(database, feed_id[0], feed_id[1], link, description, pub_date, torrent_url, save_path, 0):
            return True
        else:
            return None
        
