from flask import Flask, request
import requests

app = Flask(__name__)

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

# Функция для отправки сообщений в Telegram
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)