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


# # DB initialisation
# db_folder = Path("../db/")
# db_path = db_folder / "database.db"
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()


# Buttons
button_get = 'Запит на пісню'
button_get_rotate = 'Запит на пісню \n+ delete'
button_push = 'Залити в базу'
button_list = 'Список доступних'
button_help = 'Допомога'


def button_get_handler(update, context):
    song = get_from_db(update, context)
    # rotate_song(song)


def button_get_rotate_handler(update, context):
    song = get_from_db(update, context)
    rotate_song(song)


def button_push_handler(update: Update, context: CallbackContext, click=True):
    if update.message.text.__contains__('http'):
        push_to_db(update, context, update.message.text)
    else:
        update.message.reply_text('Enter link')

    # push_to_db(update, context)


def button_list_handler(update, context):
    db_list(update, context)


def button_help_handler(update, context):
    pass


def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button_get),
                KeyboardButton(text=button_get_rotate),
                KeyboardButton(text=button_push)
            ],
            [
                KeyboardButton(text=button_list),
                KeyboardButton(text=button_help),
                KeyboardButton(text=button_help)
            ]
        ],
        resize_keyboard=True
    )
    update.message.reply_text(text='click on button', reply_markup=reply_markup)


def help(update, context):
    update.message.reply_text('Help!')


def db_list(update, context):
    # DB initialisation
    db_folder = Path("../db/")
    db_path = db_folder / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql = "SELECT title, link FROM actual_songs"
    cursor.execute(sql)
    logger.info(sql)
    fetch = cursor.fetchall()

    # http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    logger.info(fetch)
    logger.info(fetch[0])

    res = ''
    for i in fetch:
        res += i[0] + '\n' + i[1] + '\n\n'

    update.message.reply_text(res, disable_web_page_preview=True)
    conn.close()


def push_to_db(update, context, internal_link=''):
    # DB initialisation
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
        result_prob = result_prob + prob_table[i][1] / (count + 1)
        temp = prob_table[i][1] - prob_table[i][1] / (count + 1)  # TO DO add some cof
        sql = f'UPDATE probability SET prob = "{temp}" WHERE id = {prob_table[i][0]}'
        logger.info(sql)
        cursor.execute(sql)
    conn.commit()

    # id_ = int(cursor.fetchone()) + 1
    # print(cursor.fetchone()[0], context.args[0])
    # logger.info(sql.replace('?', context.args[0]))
    try:
        link_ = context.args[0]
    except:
        link_ = internal_link

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', link_)
    soup = BeautifulSoup(r.data, 'html.parser')
    # soup.title.string

    # print(update.message.text + link_)
    date_ = datetime.datetime.now()
    sql = f'INSERT INTO actual_songs (link, create_timestamp, title) VALUES ("{link_}","{date_}","{soup.title.string}")'
    cursor.execute(sql)

    sql = f'INSERT INTO probability (prob ) VALUES ("{result_prob}")'
    cursor.execute(sql)

    conn.commit()

    conn.close()
    logger.info(sql)


def get_from_db(update, context):
    # DB initialisation
    db_folder = Path("../db/")
    db_path = db_folder / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql = "SELECT id, link FROM actual_songs ORDER BY RANDOM() LIMIT 1"
    cursor.execute(sql)
    logger.info(sql)
    fetch = cursor.fetchone()
    song_id = fetch[0]

    logger.info(fetch)
    logger.info(song_id)

    # date_ = datetime.datetime.now()
    # logger.info(date_)
    # # sql = f'UPDATE actual_songs SET last_access = "{date_}" WHERE id = {fetch[0]}'
    # sql = f'INSERT INTO old_songs (actual_song_id, create_timestamp, last_access, link, rotate_timestamp) \
    #         SELECT id, create_timestamp, last_access, link, "{date_}" \
    #         FROM actual_songs WHERE actual_songs.id = {song_id}'
    # cursor.execute(sql)
    # conn.commit()
    #
    # sql = f'DELETE FROM actual_songs WHERE id = {song_id};\
    #         DELETE FROM probability WHERE id = {song_id};'
    # cursor.executescript(sql)
    # conn.commit()

    update.message.reply_text(fetch[1])
    conn.close()
    return song_id


def rotate_song(song_id):
    # DB initialisation
    db_folder = Path("../db/")
    db_path = db_folder / "database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    date_ = datetime.datetime.now()
    # sql = f'UPDATE actual_songs SET last_access = "{date_}" WHERE id = {fetch[0]}'
    sql = f'INSERT INTO old_songs (actual_song_id, create_timestamp, last_access, link, rotate_timestamp) \
                SELECT id, create_timestamp, last_access, link, "{date_}" \
                FROM actual_songs WHERE actual_songs.id = {song_id}'
    cursor.execute(sql)

    sql = 'SELECT * FROM probability'
    cursor.execute(sql)
    prob_table = cursor.fetchall()

    result_prob = prob_table.__contains__(song_id)
    logger.info(prob_table)
    for i in range(count):
        result_prob = result_prob + prob_table[i][1] / (count + 1)
        temp = prob_table[i][1] - prob_table[i][1] / (count + 1)  # TO DO add some cof
        sql = f'UPDATE probability SET prob = "{temp}" WHERE id = {prob_table[i][0]}'
        logger.info(sql)
        cursor.execute(sql)
    conn.commit()

    sql = f'DELETE FROM actual_songs WHERE id = {song_id};\
                DELETE FROM probability WHERE id = {song_id};'

    cursor.executescript(sql)
    conn.commit()
    conn.close()


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def message_handler(update: Update, context: CallbackContext):
    text = str(update.message.text)
    logger.info(text)

    temp = {
        button_get: button_get_handler,

        button_get_rotate: button_get_rotate_handler,

        button_list: button_list_handler,

        button_help: button_help_handler,

    }.get(text, button_push_handler)(update, context)

    # if text == button_get:
    #     button_get_handler(update, context)
    #
    # elif text == button_push or text.__contains__('http'):
    #     button_push_handler(update, context)
    #
    # # elif text.__contains__('http'):
    # #    button_push_handler(update, context, click=False)
    #
    # elif text == button_list:
    #     button_list_handler(update, context)
    #
    # elif text == button_help:
    #     button_help_handler(update, context)
    #
    # else:
    #     start(update, context)

# def choice(x):
#     return {
#         button_get: button_get_handler()
#     }


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
