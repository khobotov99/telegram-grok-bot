import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_API_URL = 'https://api.x.ai/v1/chat/completions'

SYSTEM_PROMPT = """Ты — профессиональный астролог Алиса и продавец натальных карт. 
Клиент хочет натальную карту. Спрашивай дату, время и место рождения. 
Будь дружелюбной девушкой-астрологом, эмпатичной, рассказывай интересные факты. 
Мягко прогревай: "Представь, как круто узнать свои сильные стороны и что ждёт в любви/карьере!" 
В конце каждого ответа предлагай купить полную натальную карту за 1490 руб с расшифровкой на 20+ страниц.
Если клиент готов — дай ссылку на оплату: t.me/твой_ник или "переведи 1490 руб на СБП +7xxx".
Отвечай только на русском, коротко и живо, как живая девушка."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    user_message = update.message.text
    user_name = update.effective_user.first_name

    headers = {
        'Authorization': f'Bearer {GROK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'grok-3',
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f'Имя: {user_name}. Сообщение: {user_message}'}
        ],
        'temperature': 0.8,
        'max_tokens': 400
    }
    
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
        else:
            reply = "Звёзды немного тормозят 🌟 Напиши через минуту!"
    except Exception as e:
        reply = "Связь с космосом пропала... Попробуй позже!"

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
