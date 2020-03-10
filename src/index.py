import logging
import sqlite3
import datetime


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')


def help(update, context):
    update.message.reply_text('Help!')


def echo(update, context):
    update.message.reply_text(update.message.text)


def push_to_db(update, context):
    conn = sqlite3.connect("..\\db\\database.db")
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM test_table1"
    cursor.execute(sql)
    #id_ = int(cursor.fetchone()) + 1
    print(cursor.fetchone()[0], context.args[0])
    #logger.info(sql.replace('?', context.args[0]))
    link_ = context.args[0]
    date_ = datetime.datetime.now().__str__()
    sql = f'INSERT INTO test_table1 (link, create_time) VALUES ("{link_}","{date_}")'
    cursor.execute(sql)
    conn.commit()
    conn.close()



def get_from_db(update, context):
    conn = sqlite3.connect("..\\db\\database.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM albums WHERE artist=?"
    cursor.execute(sql, [context.args[0]])
    logger.info(sql.replace('?', context.args[0]))

    # print(context.args)


    update.message.reply_text(cursor.fetchall())


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    updater = Updater('1068603310:AAH88xjTIJEWiltRjxWlkQ5kXvh7gy2danI', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("get", get_from_db))
    dp.add_handler(CommandHandler("push", push_to_db))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()