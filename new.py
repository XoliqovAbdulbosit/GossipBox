from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CHANNEL_ID = '@just_do_it_with_me'
TOKEN = ''
ADMIN_ID = 0
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'
waiting = {}


def send_telegram_message(chat_id, text):
    url = f'{BASE_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
    }
    requests.post(url, json=payload)


def send_telegram_message_with_inline_keyboard(chat_id, text, keyboard):
    url = f'{BASE_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'reply_markup': keyboard,
    }
    requests.post(url, json=payload)


def delete_message(chat_id, msg_id):
    url = f'{BASE_URL}/deleteMessage'
    payload = {'chat_id': chat_id, 'message_id': msg_id}
    requests.post(url, json=payload)


def set_webhook(url):
    url = f'{BASE_URL}/setWebhook?url={url}'
    requests.post(url)


@app.route('/', methods=['POST'])
def bot():
    data = request.json
    if 'callback_query' in data:
        state, saved_message_id = data["callback_query"]["data"].split('.')
        saved_message_id = int(saved_message_id)
        message_id = data["callback_query"]["message"]['message_id']
        if state == 'accept' and saved_message_id in waiting:
            send_telegram_message(CHANNEL_ID, waiting[saved_message_id])
        delete_message(ADMIN_ID, message_id)
        if saved_message_id in waiting:
            del waiting[saved_message_id]
    elif 'message' in data:
        chat_id = data['message']['chat']['id']
        message = data['message'].get('text', '')
        message_id = data['message']['message_id']
        if message == '/start':
            send_telegram_message(chat_id,
                                  'GossipBox botiga xush kelibsiz. Kanalga xabar yuborish uchun xabarni shu yerda yozing.')
        else:
            waiting[message_id] = message
            keyboard = {'inline_keyboard': [[
                {'text': 'Accept', 'callback_data': f'accept.{message_id}'},
                {'text': 'Reject', 'callback_data': f'reject.{message_id}'}
            ]]}
            send_telegram_message_with_inline_keyboard(ADMIN_ID, message, keyboard)
    return jsonify({'success': True})


if __name__ == '__main__':
    url = ''
    set_webhook(url)
    app.run(debug=True)
