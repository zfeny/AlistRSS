import requests

# 设置Telegram Bot API令牌和目标聊天ID
bot_token = '6600084626:AAFYIIzo1DTJxK3u3LeYm61DSnq8hjx9Q9s'
chat_id = '6053101561'

name =123
# 定义Markdown消息模板
if 1 == 1:
    message = f"""
<b>bold</b>{name}
_____________________________________
    """


message += """
<a href="tg://user?id=123456789">inline mention of a user</a>

"""

requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={message}')
