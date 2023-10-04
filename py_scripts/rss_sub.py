import re
from . import file_rw

# 解析URL，获取BangumiID和SubgroupID
def parse_feed_url(url):
    # 定义正则表达式模式来匹配数字
    pattern = r'bangumiId=(\d+)&subgroupid=(\d+)'

    # 使用正则表达式进行匹配
    match = re.search(pattern, url)

    # 检查是否匹配到了
    if match:
        # 通过group()方法获取匹配的值，并赋值给变量
        n1 = match.group(1)
        n2 = match.group(2)
        return [n1, n2]
    else:
        return None

# 更新RSS源
def new(database, csv_file, auto_path):
    feed_need_update = file_rw.feed_read(database, csv_file)
    result = 0
    for feed in feed_need_update:
        feed_url = feed[0]
        feed_save_path = feed[1]
        feed_id = parse_feed_url(feed_url)
        if feed_id:
            if file_rw.feed_sub(database, feed_url, feed_save_path, auto_path, feed_id):
                result += 1
        else:
            result -= 1
            break
    
    return result