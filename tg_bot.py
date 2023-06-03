import os
import logging
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from store import get_all_products, get_token, get_product_by_id, get_product_price


def start(update, context):
    products = get_all_products(access_token)["data"]
    keyboard = [
        [InlineKeyboardButton(f"{product['attributes']['name']}", callback_data=f"{product['id']}")] for product in products
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Please choose',
                             reply_markup=reply_markup)
    return "MENU"


def handle_menu(update, context):
    user_reply = update.callback_query
    if user_reply:
        product_id = update.callback_query.data
        product = get_product_by_id(access_token, product_id)
        product_attributes = product["data"]["attributes"]
        product_price = get_product_price(access_token, price_book_id, product_attributes["sku"])
        final_price = product_price["data"]["attributes"]["currencies"]["USD"]["amount"]
        template = f"{product_attributes['name']}\n\n" \
                   f"${final_price} per kg\n\n" \
                   f"{product_attributes['description']}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=template)
        return "START"


def handle_users_reply(update, context):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = r.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'MENU': handle_menu
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        r.set(chat_id, next_state)
    except Exception as err:
        print(err)


if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0)

    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    price_book_id = os.environ["PRICE_BOOK_ID"]

    access_token = get_token(client_id, client_secret)

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
