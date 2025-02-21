from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CHANNEL_ID = '@just_do_it_with_me'
TOKEN = ''
ADMIN_ID = 0
counter_file_path = 'counter.txt'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'
waiting = {}


def send_telegram_message(chat_id, text, photo=None, video=None, audio=None, voice=None, keyboard=None):
    url = ''
    payload = {'chat_id': chat_id, 'parse_mode': 'Markdown'}
    if photo:
        url = f'{BASE_URL}/sendPhoto'
        payload['photo'] = photo
        if text:
            payload['caption'] = text
    elif video:
        url = f'{BASE_URL}/sendVideo'
        payload['video'] = video
        if text:
            payload['caption'] = text
    elif audio:
        url = f'{BASE_URL}/sendAudio'
        payload['audio'] = audio
        if text:
            payload['caption'] = text
    elif voice:
        url = f'{BASE_URL}/sendVoice'
        payload['voice'] = voice
        if text:
            payload['caption'] = text
    elif text:
        url = f'{BASE_URL}/sendMessage'
        payload['text'] = text
    if keyboard:
        payload['reply_markup'] = keyboard
    requests.post(url, json=payload)


def get_counter():
    if not os.path.exists(counter_file_path):
        with open(counter_file_path, 'w') as f:
            f.write('835')
    with open(counter_file_path, 'r') as f:
        return int(f.read().strip())


def update_counter(value):
    with open(counter_file_path, 'w') as f:
        f.write(str(value))


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
            counter = get_counter()
            counter += 1
            update_counter(counter)
            text = waiting[saved_message_id]['text'] + f'\n*№{counter}*'
            if 'photo' in waiting[saved_message_id]:
                send_telegram_message(CHANNEL_ID, text, photo=waiting[saved_message_id]['photo'])
            elif 'video' in waiting[saved_message_id]:
                send_telegram_message(CHANNEL_ID, text, video=waiting[saved_message_id]['video'])
            elif 'audio' in waiting[saved_message_id]:
                send_telegram_message(CHANNEL_ID, text, audio=waiting[saved_message_id]['audio'])
            elif 'voice' in waiting[saved_message_id]:
                send_telegram_message(CHANNEL_ID, text, voice=waiting[saved_message_id]['voice'])
            else:
                send_telegram_message(CHANNEL_ID, text)
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
            keyboard = {'inline_keyboard': [[
                {'text': 'Accept', 'callback_data': f'accept.{message_id}'},
                {'text': 'Reject', 'callback_data': f'reject.{message_id}'}
            ]]}
            if 'photo' in data['message']:
                file_id = data['message']['photo'][-1]['file_id']
                message = data['message'].get('caption', '')
                waiting[message_id] = {'text': message, 'photo': file_id}
                send_telegram_message(ADMIN_ID, message, keyboard=keyboard, photo=file_id)
            elif 'video' in data['message']:
                file_id = data['message']['video']['file_id']
                message = data['message'].get('caption', '')
                waiting[message_id] = {'text': message, 'video': file_id}
                send_telegram_message(ADMIN_ID, message, keyboard=keyboard, video=file_id)
            elif 'audio' in data['message']:
                file_id = data['message']['audio']['file_id']
                message = data['message'].get('caption', '')
                waiting[message_id] = {'text': message, 'audio': file_id}
                send_telegram_message(ADMIN_ID, message, keyboard=keyboard, audio=file_id)
            elif 'voice' in data['message']:
                file_id = data['message']['voice']['file_id']
                message = data['message'].get('caption', '')
                waiting[message_id] = {'text': message, 'voice': file_id}
                send_telegram_message(ADMIN_ID, message, keyboard=keyboard, voice=file_id)
            elif 'text' in data['message']:
                waiting[message_id] = {'text': message}
                send_telegram_message(ADMIN_ID, message, keyboard=keyboard)
    return jsonify({'success': True})


if __name__ == '__main__':
    url = ''
    set_webhook(url)
    app.run(debug=True)
