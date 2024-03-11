import os
import requests
import easydict

Bot_Token = os.environ.get('TELEGRAM_BOT_TOKEN')
Chat_id = os.environ.get('TELEGRAM_CHAT_ID')

input_message = input()

def send_message(message):
    args = easydict.EasyDict({
            "messages": message
    })

    requests.post('https://api.telegram.org/bot%s/%s'%(Bot_Token, 'sendMessage'),
    data={
        'chat_id':Chat_id,
        "text": message
    })

send_message(input_message)