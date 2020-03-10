import logging
import sqlite3
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


def start(update, context):
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [InlineKeyboardButton("1", callback_data=str(ONE)),
         InlineKeyboardButton("2", callback_data=str(TWO))]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Start handler, Choose a route",
        reply_markup=reply_markup
    )

    return FIRST


# def start_over(update, context):
#     """Prompt same text & keyboard as `start` does but not as new message"""
#     # Get CallbackQuery from Update
#     query = update.callback_query
#     # Get Bot from CallbackContext
#     bot = context.bot
#     keyboard = [
#         [InlineKeyboardButton("1", callback_data=str(ONE)),
#          InlineKeyboardButton("2", callback_data=str(TWO))]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     # Instead of sending a new message, edit the message that
#     # originated the CallbackQuery. This gives the feeling of an
#     # interactive menu.
#     bot.edit_message_text(
#         chat_id=query.message.chat_id,
#         message_id=query.message.message_id,
#         text="Start handler, Choose a route",
#         reply_markup=reply_markup
#     )
#     return FIRST


def help(update, context):
    update.message.reply_text('Help!')


# def echo(update, context):
#     update.message.reply_text(update.message.text)


def push_to_db(update, context):
    conn = sqlite3.connect("..\\db\\database.db")
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM test_table1"
    cursor.execute(sql)
    #id_ = int(cursor.fetchone()) + 1
    # print(cursor.fetchone()[0], context.args[0])
    # logger.info(sql.replace('?', context.args[0]))
    link_ = context.args[0]
    date_ = datetime.datetime.now().__str__()
    sql = f'INSERT INTO test_table1 (link, create_time) VALUES ("{link_}","{date_}")'
    cursor.execute(sql)
    conn.commit()
    conn.close()
    logger.info(sql)



def get_from_db(update, context):
    conn = sqlite3.connect("..\\db\\database.db")
    cursor = conn.cursor()
    # sql = "SELECT * FROM albums WHERE artist=?"
    sql = "SELECT * FROM test_table1 ORDER BY RANDOM() LIMIT 1"
    # cursor.execute(sql, [context.args[0]])
    cursor.execute(sql)
    logger.info(sql)
    fetch = cursor.fetchall()
    logger.info(fetch)
    logger.info(int(fetch[0][0]))
    date_ = datetime.datetime.now().__str__()
    sql = f'UPDATE test_table1 SET request_time = "{date_}" WHERE id = {int(fetch[0][0])}'
    cursor.execute(sql)
    conn.commit()
    # print(context.args)


    update.message.reply_text(fetch[0][1])


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    updater = Updater('1068603310:AAH88xjTIJEWiltRjxWlkQ5kXvh7gy2danI', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("get", get_from_db))
    dp.add_handler(CommandHandler("push", push_to_db))

    # dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()