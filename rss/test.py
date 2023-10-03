import os,requests
def tg_bot(message, bot_token, chat_id):
    api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    response = requests.post(api_url, params=params)
    # requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}')

    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message. Status code:', response.status_code)

aria2_return = [1,2,3,4,5]
tg_bot_token = "6600084626:AAFYIIzo1DTJxK3u3LeYm61DSnq8hjx9Q9s"
tg_chat_id = "6053101561"
rss_num = 5
# Telegram推送消息
tg_ms = f'RSS订阅程序运行完毕，本次共拉取*{rss_num}*个RSS项。\n'
tg_ms += "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
for i in aria2_return:
    ms_title = 'title'
    ms_url = 'www.baidu.com'
    tg_ms += f"[{ms_title}]({ms_url})\n"
tg_ms += "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
# if rss_failed > 0:
#     tg_ms += "*以下RSS项添加失败：*\n"
#     for i in aria2_return["failed_id"]:
#         get_DS_link_return = get_DS_link(i, rss_db_path)
#         ms_title = get_DS_link_return[0][0]
#         ms_url = get_DS_link_return[0][1]
#         tg_ms += f"[{ms_title}]({ms_url})\n"
#     tg_ms += "---\n"

tg_bot(tg_ms, tg_bot_token, tg_chat_id)