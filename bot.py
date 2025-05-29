from flask import Flask, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/send_telegram_notification": {"origins": ["chrome-extension://pnfhoobelgilgafgacdnmebgohgknkdg", "https://crypto-predictor-acr2.onrender.com"]}})

# Токен твоего бота
TELEGRAM_BOT_TOKEN = '8176459174:AAHYP9fGzmGbnoUnmTplk7OxUGyeEuTqA5U'
# URL твоего сервера (Render)
SERVER_URL = 'https://crypto-predictor-acr2.onrender.com'

# Эндпоинт вебхука
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    # Проверяем, есть ли сообщение и команда /start
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        # Если команда /start с параметром (например, /start user123)
        if text.startswith('/start'):
            user_id = text.split()[1] if len(text.split()) > 1 else None
            if user_id:
                # Отправляем user_id и chat_id на сервер
                response = requests.post(
                    f'{SERVER_URL}/subscribe_telegram',
                    params={'userId': user_id, 'chatId': chat_id}
                )
                if response.json().get('ok'):
                    # Отправляем сообщение пользователю в Telegram
                    send_message(chat_id, 'Вы успешно подписались на уведомления! 🎉')
                else:
                    send_message(chat_id, 'Ошибка подписки. Попробуйте снова.')
            else:
                send_message(chat_id, 'Пожалуйста, используйте ссылку из расширения.')
    return 'OK', 200

# Эндпоинт для отправки уведомлений
@app.route('/send_telegram_notification', methods=['POST'])
def send_telegram_notification():
    user_id = request.args.get('userId')
    message = request.args.get('message')
    lang = request.args.get('lang', 'ru')  # Язык по умолчанию — русский

    if not user_id or not message:
        return {'ok': False, 'message': 'Missing userId or message'}, 400

    # Отправляем запрос на сервер для получения chat_id
    try:
        response = requests.get(f'{SERVER_URL}/get_chat_id', params={'userId': user_id})
        response.raise_for_status()
        data = response.json()
        if not data.get('ok'):
            return {'ok': False, 'message': 'User not subscribed'}, 404
        chat_id = data['chat_id']
    except requests.RequestException as e:
        return {'ok': False, 'message': f'Failed to fetch chat_id: {str(e)}'}, 500

    # Отправляем сообщение в Telegram
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if not data.get('ok'):
            return {'ok': False, 'message': data.get('description')}, 500
        return {'ok': True, 'message': 'Notification sent'}, 200
    except requests.RequestException as e:
        return {'ok': False, 'message': f'Failed to send Telegram message: {str(e)}'}, 500

# Функция для отправки сообщений в Telegram
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)