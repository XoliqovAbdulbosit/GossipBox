import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, CommandHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHANNEL_ID = ''
TOKEN = ''


async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text='INHA Universitetining GossipBox botiga xush kelibsiz. Kanalga xabar yuborish uchun xabarni shu yerda yozing.')


async def forward_to_channel(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=CHANNEL_ID, text=update.message.text)
    await context.bot.send_message(chat_id=update.message.chat_id, text='Xabar yuborildi.')


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_channel))
    application.run_polling()


if __name__ == '__main__':
    main()
