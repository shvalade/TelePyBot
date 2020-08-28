#!/usr/bin/env python3
#from telebot import AsyncTeleBot
import cherrypy
import telebot
import logging
#from telebot import TeleBot, types
import config
# import time
from sqlighter import SQLighter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.loggingLevel)
logger = logging.getLogger(__name__)

BOT_TOKEN = config.token
bot = telebot.TeleBot(BOT_TOKEN)


# task = bot.get_me()
# result = task.wait()
# bot.send_message(message.chat.id, result)

db = SQLighter(user=config.db_user, passwd=config.db_passwd, db=config.db)

WelcomeText = f'Welcome!\n' \
       f'This bot can save songs from different users.\n' \
       f'You can request a random song from DB that any users added\n' \
       f'And much more) stay tuned!'


def print_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        telebot.types.InlineKeyboardButton(text='Subscribe', callback_data='sub'),
        telebot.types.InlineKeyboardButton(text='Unsubscribe', callback_data='unsub'),
        telebot.types.InlineKeyboardButton(text='Status', callback_data='status'),
        telebot.types.InlineKeyboardButton(text='Get song', callback_data='get_song_call'),
        telebot.types.InlineKeyboardButton(text='Get song+rotate', callback_data='get_rotate_call'),
        telebot.types.InlineKeyboardButton(text='Push song', callback_data='push_song_call'),
        telebot.types.InlineKeyboardButton(text='All list', callback_data='all_list'),
        telebot.types.InlineKeyboardButton(text='Songs added by you', callback_data='user_songs'),
        telebot.types.InlineKeyboardButton(text='Help', callback_data='help'),
    )
    return markup
    # bot.send_message(user_id, text, reply_markup=markup)


@bot.message_handler(commands=["start"])
def command_start(message, text=WelcomeText):
    #  print_keyboard(message.from_user.id, text=text)
    bot.send_message(message.chat.id, text, reply_markup=print_keyboard())

    # time.sleep(5)
    # markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    # markup.add(
    #     telebot.types.InlineKeyboardButton(text='Subscribe', callback_data='sub'),
    #     telebot.types.InlineKeyboardButton(text='Unsubscribe', callback_data='unsub'),
    #     telebot.types.InlineKeyboardButton(text='Status', callback_data='status'),
    #     telebot.types.InlineKeyboardButton(text='Get song', callback_data='get_song_call'),
    #     telebot.types.InlineKeyboardButton(text='Get song+rotate', callback_data='get_rotate_call'),
    #     telebot.types.InlineKeyboardButton(text='Push song', callback_data='push_song_call'),
    #     telebot.types.InlineKeyboardButton(text='All list', callback_data='all_list'),
    #     telebot.types.InlineKeyboardButton(text='Songs added by you', callback_data='user_songs'),
    #     telebot.types.InlineKeyboardButton(text='Help', callback_data='help'),
    # )
    #


@bot.callback_query_handler(func=lambda call: call.data == 'sub')
def subscribe_call(call):
    if not db.subscriber_exist(call.from_user.id):
        db.add_subscriber(call.from_user.id)
        bot.answer_callback_query(callback_query_id=call.id, text="Success subscribe!")
    elif db.get_user_status(call.from_user.id):
        bot.answer_callback_query(callback_query_id=call.id, text="Already subscribed!")
    else:
        db.update_subscription(call.from_user.id, True)
        bot.answer_callback_query(callback_query_id=call.id, text="Subscribed!")


@bot.callback_query_handler(func=lambda call: call.data == 'unsub')
# @bot.message_handler(commands=['unsub'])
def unsubscribe_call(call):
    # bot.send_message(call.from_user.id, 'YESSSS')
    if not db.subscriber_exist(call.from_user.id):
        db.add_subscriber(call.from_user.id, status=False)
        bot.answer_callback_query(callback_query_id=call.id, text="Not subscribed yet!")
    elif not db.get_user_status(call.from_user.id):
        bot.answer_callback_query(callback_query_id=call.id, text="Already unsubscribed!")
    else:
        db.update_subscription(call.from_user.id, False)
        bot.answer_callback_query(callback_query_id=call.id, text="Unsubscribed!")


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    if not db.subscriber_exist(message.from_user.id):
        db.add_subscriber(message.from_user.id)
        bot.send_message(message.chat.id, "Subscribed successfully!")
    elif db.get_user_status(message.from_user.id):
        bot.send_message(message.chat.id, "You already subscribed!")
    else:
        db.update_subscription(message.from_user.id, True)
        bot.send_message(message.chat.id, "Subscribed successfully!")


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    if not db.subscriber_exist(message.from_user.id):
        db.add_subscriber(message.from_user.id, False)
        bot.send_message(message.chat.id, "You not subscribed yet!")
    elif not db.get_user_status(message.from_user.id):
        bot.send_message(message.chat.id, "You already unsubscribed!")
    else:
        db.update_subscription(message.from_user.id, False)
        bot.send_message(message.chat.id, "Unsubscribed successfully!")


@bot.callback_query_handler(func=lambda call: call.data == 'status')
@bot.message_handler(commands=['status'])
def get_status(call):
    if db.get_user_status(call.from_user.id):
        bot.send_message(call.from_user.id, 'Subscribed to updates!')
    else:
        bot.send_message(call.from_user.id, 'Not subscribed to updates!')


@bot.callback_query_handler(func=lambda call: call.data == 'get_rotate_call')
@bot.message_handler(commands=['get_rotate'])
def get_rotate(call):
    usr_id, link = db.get_rotate_random_song()
    # logger.debug(list)
    res = f'From user {usr_id}:\n{link}'
    bot.send_message(call.from_user.id, res, reply_markup=print_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'get_song_call')
@bot.message_handler(commands=['get_song'])
def get_random_song(call):
    list = db.get_random_song()
    logger.debug(list)
    res = f'From user {list[0]}:\n{list[1]}'
    bot.send_message(call.from_user.id, res, reply_markup=print_keyboard())
    # print_keyboard(call.from_user.id, text='123')


@bot.callback_query_handler(func=lambda call: call.data == 'push_song_call')
@bot.message_handler(commands=['push_song'])
def push_song(call):
    # if call == 'push_song_call':
    msg = bot.send_message(call.from_user.id, 'Enter link:')
    bot.register_next_step_handler(msg, process_link)


def process_link(message):
    # logger.debug('===========================================++++++++++++++++ ')
    # logger.debug(message.from_user.id)
    try:
        # add validation to link

        link = message.text
        db.push_song(message.from_user.id, link)
    except Exception as e:
        bot.reply_to(message, e)


@bot.callback_query_handler(func=lambda call: call.data == 'all_list')
def get_all_list(call):
    bot.send_message(call.from_user.id, db.select_all(), disable_web_page_preview=True, reply_markup=print_keyboard())
    # ''.join(map(lambda x: str('\n'.join(map(str, x)) + '\n\n'), test))


@bot.callback_query_handler(func=lambda call: call.data == 'user_songs')
def user_songs(call):
    links_list = db.get_user_songs(call.from_user.id)
    bot.send_message(call.from_user.id, links_list,
                     disable_web_page_preview=True, reply_markup=print_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def helps(call):
    bot.send_message(call.from_user.id, '0 Help yet')

    bot._notify_reply_handlers('another')

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        length = int(cherrypy.request.headers['content-length'])
        json_string = cherrypy.request.body.read(length).decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.delete_webhook()
    bot.set_webhook(url="https://vshakhrai.dns-cloud.net/AAAA/")
    print(bot.get_webhook_info())
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 9977,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})

