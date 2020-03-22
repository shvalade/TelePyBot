import logging
import sqlite3
import datetime
from pathlib import Path

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

button_get = 'Запит на пісню'
button_push = 'Залити в базу'
button_list = 'Список доступних'
button_help = 'Допомога'


def button_get_handler(update, context):
    get_from_db(update, context)


def button_push_handler(update: Update, context: CallbackContext, click=True):
    if update.message.text.__contains__('http'):
        push_to_db(update, context, update.message.text)
    else:
        update.message.reply_text('Enter link')

    #push_to_db(update, context)


def button_list_handler(update, context):
    pass


def button_help_handler(update, context):
    pass


def start(update: Update, context: CallbackContext):

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button_get),
                KeyboardButton(text=button_push)
            ],
            [
                KeyboardButton(text=button_list),
                KeyboardButton(text=button_help)
            ]
        ],
        resize_keyboard=True
    )
    update.message.reply_text(text='click on button', reply_markup=reply_markup)


def help(update, context):
    update.message.reply_text('Help!')


def push_to_db(update, context, internal_link=''):
    db_folder = Path("../db/")
    file_to_open = db_folder / "database.db"
    conn = sqlite3.connect(file_to_open)
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM actual_songs"
    cursor.execute(sql)
    count = cursor.fetchone()[0]

    sql = "SELECT * FROM probability"
    cursor.execute(sql)
    prob_table = list(cursor.fetchall())
    result_prob = 0.0

    for i in range(count):
        result_prob = result_prob + prob_table[i][1] / (count+1)
        temp = prob_table[i][1] - prob_table[i][1] / (count+1)  # TO DO add some cof
        sql = f'UPDATE probability SET prob = "{temp}" WHERE id = {prob_table[i][1]}'
        cursor.execute(sql)
    conn.commit()

    #id_ = int(cursor.fetchone()) + 1
    # print(cursor.fetchone()[0], context.args[0])
    # logger.info(sql.replace('?', context.args[0]))
    try:
        link_ = context.args[0]
    except:
        link_ = internal_link

    # print(update.message.text + link_)
    date_ = datetime.datetime.now().timestamp().__int__()
    sql = f'INSERT INTO actual_songs (link, create_timestamp) VALUES ("{link_}","{date_}")'
    cursor.execute(sql)

    sql = f'INSERT INTO probability (prob ) VALUES ("{result_prob}")'
    cursor.execute(sql)

    conn.commit()

    conn.close()
    logger.info(sql)


def get_from_db(update, context):
    db_folder = Path("../db/")
    file_to_open = db_folder / "database.db"
    conn = sqlite3.connect(file_to_open)
    cursor = conn.cursor()
    # sql = "SELECT * FROM albums WHERE artist=?"
    sql = "SELECT * FROM actual_songs ORDER BY RANDOM() LIMIT 1"
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

    update.message.reply_text(fetch[0][1])


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def message_handler(update: Update, context: CallbackContext):
    text = str(update.message.text)
    print(text)
    if text == button_get:
        button_get_handler(update, context)

    elif text == button_push or text.__contains__('http'):
        button_push_handler(update, context)

    #elif text.__contains__('http'):
    #    button_push_handler(update, context, click=False)

    elif text == button_list:
        button_list_handler(update, context)

    elif text == button_help:
        button_help_handler(update, context)

    else:
        start(update, context)


def main():

    updater = Updater('1068603310:AAH88xjTIJEWiltRjxWlkQ5kXvh7gy2danI', use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(filters=Filters.all, callback=message_handler))
    dp.add_handler(CommandHandler(command='start', callback=start))
    dp.add_handler(CommandHandler(command='help', callback=help))
    dp.add_handler(CommandHandler(command='get', callback=get_from_db))
    dp.add_handler(CommandHandler(command='push', callback=push_to_db))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()