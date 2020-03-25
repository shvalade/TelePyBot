import logging
import sqlite3
import datetime
from pathlib import Path
import urllib3
import certifi
from bs4 import BeautifulSoup

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
    db_list(update, context)


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


def db_list(update, context):

    db_folder = Path("../db/")
    file_to_open = db_folder / "database.db"
    conn = sqlite3.connect(file_to_open)
    cursor = conn.cursor()
    sql = "SELECT link FROM actual_songs"
    cursor.execute(sql)
    logger.info(sql)
    fetch = cursor.fetchall()
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    logger.info(fetch)
    logger.info(fetch[0])
    res = ''
    for i in fetch:
        r = http.request('GET', i[0])
        soup = BeautifulSoup(r.data, 'html.parser')
        res += soup.title.string + '\n'
    update.message.reply_text(res)
    pass


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
    prob_table = cursor.fetchall()
    result_prob = 0.0
    logger.info(prob_table)
    for i in range(count):
        result_prob = result_prob + prob_table[i][1] / (count+1)
        temp = prob_table[i][1] - prob_table[i][1] / (count+1)  # TO DO add some cof
        sql = f'UPDATE probability SET prob = "{temp}" WHERE id = {prob_table[i][0]}'
        logger.info(sql)
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
    date_ = datetime.datetime.now()
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
    sql = "SELECT id, link FROM actual_songs ORDER BY RANDOM() LIMIT 1"
    cursor.execute(sql)
    logger.info(sql)
    fetch = cursor.fetchone()
    logger.info(fetch)
    logger.info(fetch[0])
    date_ = datetime.datetime.now()
    logger.info(date_)
    # sql = f'UPDATE actual_songs SET last_access = "{date_}" WHERE id = {fetch[0]}'
    sql = f'INSERT INTO old_songs (actual_song_id, create_timestamp, last_access, link, rotate_timestamp) \
            SELECT id, create_timestamp, last_access, link, "{date_}" \
            FROM actual_songs WHERE actual_songs.id = {fetch[0]}'
    cursor.execute(sql)
    conn.commit()

    sql = f'DELETE FROM actual_songs WHERE id = {fetch[0]};\
            DELETE FROM probability WHERE id = {fetch[0]};'
    cursor.executescript(sql)
    conn.commit()

    update.message.reply_text(fetch[1])


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