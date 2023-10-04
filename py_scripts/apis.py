import requests

def alist_get_token(login_url, login_data):
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

def alist_add_aria2(aria2_url, alist_headers, alist_data):

    alist_response = requests.post(aria2_url, headers=alist_headers, json=alist_data)

    return alist_response

def tg_bot(message, tg_bot_info):
    bot_token = tg_bot_info["token"]
    chat_id = tg_bot_info["chat_id"]
    requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={message}')